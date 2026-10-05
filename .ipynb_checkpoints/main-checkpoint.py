import asyncio
import sys
import json
from core.mcp_client import MCPManager
from agents.react_agent import build_agent
SERVERS = [
    {"name": "files", "cmd": "python", "args": ["mcp_servers/file_search/server.py"]},
    {"name": "web", "cmd": "python", "args": ["mcp_servers/web_search/server.py"]}]

async def run(query: str):
    mcp = MCPManager()
    try:
        # 1. Connect to all MCP servers
        print("[init] Connecting to MCP servers...")
        for server in SERVERS:
            await mcp.connect_server(
                server["name"],
                server["cmd"],
                server["args"]
            )
        print(f"[init] Loaded {len(mcp.tools)} tools: {[t.name for t in mcp.tools]}")

        # 2. Build the agent
        # main.py — replace section 2 and 3
        print("[init] Building specialized agents...")

        researcher = build_agent(
        role="You search local files and the web. Find data, cite sources.",
        model="dolphin",
        tools=mcp.tools_from("files", "web"),
        )

analyst = build_agent(
    role="You analyze structured data (CSV/JSON) and write Python code.",
    model="deepseek",
    tools=mcp.tools_from("files"),
)

devops = build_agent(
    role="You execute scripts on AWS EC2 sandbox instances. Confirm before write operations.",
    model="deepseek",
    tools=mcp.tools_from("aws"),
)

agents = {"researcher": researcher, "analyst": analyst, "devops": devops}

# Route the query
    print(f"\n[query] {query}\n")
    result = await agents["researcher"].ainvoke({"input": query, "chat_history": ""})
print("\n=== FINAL ANSWER ===")
print(result["output"])

        # 3. Execute the query
        print(f"\n[query] {query}\n")
        result = await agent.ainvoke({
            "input": query,
            "chat_history": ""
        })

        # 4. Output the final answer
        print("\n=== FINAL ANSWER ===")
        print(result["output"])

    except Exception as e:
        print(f"\n[error] {e}")
        import traceback
        traceback.print_exc()
    finally:
        await mcp.cleanup()

if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Hello"
    asyncio.run(run(query))
