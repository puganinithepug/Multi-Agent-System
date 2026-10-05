# test_web_mcp.py — run from project root
import asyncio
from core.mcp_client import MCPManager

async def main():
    mcp = MCPManager()
    try:
        await mcp.connect_server("web", "python", ["mcp_servers/web_search/server.py"])
        print("\nTools:", [t.name for t in mcp.tools])
        result = await mcp.tools[0].ainvoke({"query": "what is MCP protocol"})
        print("\nResult:\n", result[:500])
    finally:
        await mcp.cleanup()

asyncio.run(main())
