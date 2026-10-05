import asyncio
import sys
import json
from core.mcp_client import MCPManager
from agents.researcher import create_researcher
from agents.analyst import create_analyst
from agents.writer import create_writer
# main.py
async def run(query: str):
    mcp = MCPManager()
    try:
        # 1. Connect
        await mcp.connect_server("files", "python", ["mcp_servers/file_search/servers.py"])
        await mcp.connect_server("web", "python", ["mcp_servers/web_search/servers.py"])

        # 2. Filter tools for specific agents
        researcher_tools = mcp.tools_from("files", "web")
        analyst_tools = mcp.tools_from("files")

        # 3. Build agents with filtered tools
        researcher = create_researcher(role="Researcher", model="qwen", tools=researcher_tools)
        analyst = create_analyst(role="Analyst", model="deepseek", tools=analyst_tools)

        # ... execute ...
    finally:
        await mcp.cleanup()
