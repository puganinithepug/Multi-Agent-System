# tests/test_web_mcp_client.py
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.mcp_client import MCPManager


async def main():
    print("[1] Initializing MCPManager...")
    mcp = MCPManager()

    try:
        print("[2] Connecting to web_search server...")
        await mcp.connect_server(
            "web",
            "python",
            ["mcp_servers/web_search/servers.py"]
        )

        # Verify tools were discovered
        names = [t.name for t in mcp.tools]
        print(f"[3] Discovered tools: {names}")
        assert "web_search" in names, f"web_search tool not found in: {names}"

        # Verify metadata tagging
        tool = mcp.tools[0]
        assert mcp._tool_meta[tool.name]== "web", f"Wrong server tag: {mcp._tool_meta[tool.name]}"
        print(f"[4] Tool metadata OK: {mcp._tool_meta[tool.name]}")

        # Invoke the tool
        print("[5] Invoking web_search...")
        result = await tool.ainvoke({
            "query": "what is langchain",
            "max_results": 2
        })

        print("\n" + "=" * 50)
        print(result)
        print("=" * 50)

        # Basic validation
        assert "Title:" in result, f"Expected 'Title:' in result. Got: {result[:200]}"
        assert "URL:" in result, f"Expected 'URL:' in result. Got: {result[:200]}"

        print("\n[PASS] All assertions passed.")

    except Exception as e:
        print(f"\n[FAIL] {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("[6] Cleaning up...")
        await mcp.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
