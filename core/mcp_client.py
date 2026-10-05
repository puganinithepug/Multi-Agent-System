# core/mcp_client.py
import asyncio
from contextlib import AsyncExitStack
from pathlib import Path
from typing import Optional, Any   # ← Any must be here


# MCP SDK
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# LangChain Integration
from langchain_core.tools import StructuredTool

# Pydantic
from pydantic import BaseModel, Field, create_model

class MCPManager:
    """
    Manages lifecycle of multiple MCP servers and exposes their tools
    as LangChain-compatible Tool objects.
    """

    def __init__(self):
        self.exit_stack = AsyncExitStack()
        self.sessions = {}   # server_name -> ClientSession
        self.tools = []      # Flat list of all LangChain Tools
        self._tool_meta = {} # Map: tool_name -> server_name (for filtering)

    async def connect_server(self, name: str, command: str, args: list):
        """
        Start an MCP server subprocess and register its tools.
        
        Args:
            name: Unique identifier for this server (e.g., 'files', 'web')
            command: Executable (e.g., 'python', 'node')
            args: Arguments to pass to the executable (e.g., ['server.py'])
        """
        print(f"[mcp] Connecting to server: {name}...")
        
        # 1. Create the process pipes
        params = StdioServerParameters(command=command, args=args)
        read, write = await self.exit_stack.enter_async_context(stdio_client(params))
        
        # 2. Initialize the session
        session = await self.exit_stack.enter_async_context(ClientSession(read, write))
        await session.initialize()
        self.sessions[name] = session

        # 3. Discover and wrap tools
        listed = await session.list_tools()
        for t in listed.tools:
            lc_tool = self._wrap(session, t) # converts mcp tool to lanchain tool
            # Tag the tool with its source server for filtering
            #lc_tool.metadata = {"server": name}
            #self.tools.append(lc_tool) # stores in global list
            self._tool_meta[t.name] = name
            self.tools.append(lc_tool)
            print(f"[mcp]   Registered tool: {t.name}")

    def _wrap(self, session: ClientSession, mcp_tool) -> StructuredTool:
        """Convert an MCP tool descriptor into a LangChain Tool."""

        def _sync_stub(**kwargs):
            raise NotImplementedError(
                f"{mcp_tool.name} is async-only. Use .ainvoke() instead of .invoke()."
            )
    
        async def _run(**kwargs):
            try:
                result = await session.call_tool(mcp_tool.name, arguments=kwargs)
                texts = []
                for content in result.content:
                    if hasattr(content, "text"):
                        texts.append(content.text)
                    else:
                        texts.append(str(content))
                return "\n".join(texts)
            except Exception as e:
                return f"[Tool Error] {mcp_tool.name} failed: {e}"
    

        # Convert MCP input schema to a Pydantic model
        schema_dict = mcp_tool.input_schema or {"type": "object", "properties": {}}
        pydantic_model = self._schema_to_pydantic(schema_dict, mcp_tool.name)
    
        return StructuredTool(
            name=mcp_tool.name,
            description=mcp_tool.description or f"Use {mcp_tool.name} to perform an action.",
            func=_sync_stub,
            coroutine=_run,
            args_schema=pydantic_model,  # ← enables multi-argument handling
        )


    def _schema_to_pydantic(self, schema_dict: dict, tool_name : str) -> type[BaseModel]:
        """Convert MCP JSON schema to a Pydantic BaseModel for StructuredTool."""
    
        fields = {}
        properties = schema_dict.get("properties", {})
        required = schema_dict.get("required", [])
    
        for prop_name, prop_def in properties.items():
            prop_type = prop_def.get("type", "string")
            default = prop_def.get("default", ...)
    
            # Map JSON schema types to Python types
            type_map = {
                "string": str,
                "integer": int,
                "number": float,
                "boolean": bool,
                "array": list,
                "object": dict,
            }
            python_type = type_map.get(prop_type, Any)
    
            field_kwargs = {"default": default}
            if prop_def.get("description"):
                field_kwargs["description"] = prop_def["description"]
    
            if prop_name not in required:
                python_type = Optional[python_type]
                field_kwargs["default"] = default if default != ... else None
    
            fields[prop_name] = (python_type, Field(**field_kwargs))
    
        return create_model(
            tool_name.capitalize() + "Input",
            **fields,
            __base__=BaseModel,
        )

    def tools_from(self, *server_names) -> list:
        return [
            t for t in self.tools
            if self._tool_meta.get(t.name) in server_names
        ]

    async def cleanup(self):
        """Close all connections and kill subprocesses."""
        print("[mcp] Cleaning up connections...")
        await self.exit_stack.aclose()
