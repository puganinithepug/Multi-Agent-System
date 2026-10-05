# tests/test_researcher_agent.py
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.mcp_client import MCPManager
from agents.researcher import create_researcher


async def main():
    print("[1] Connecting to web_search server...")
    mcp = MCPManager()
    try:
        await mcp.connect_server(
            "web", "python", ["mcp_servers/web_search/servers.py"]
        )

        print("[2] Building researcher agent with web tools...")
        agent = create_researcher(mcp.tools_from("web"))

        print("[3] Running agent: 'When was LangChain released?'")
        # LangGraph graph expects a dict with "messages" key
        result = await agent.ainvoke({
            "messages": [("human", "When was LangChain released?")]
        })

        # Extract the final answer from the last message
        final_message = result["messages"][-1]
        answer = final_message.content

        print("\n" + "=" * 50)
        print(answer)
        print("=" * 50)

        assert answer, "Agent returned empty output"
        print("\n[PASS] Researcher agent executed successfully.")

    except Exception as e:
        print(f"\n[FAIL] {e}")
        import traceback
        traceback.print_exc()
    finally:
        await mcp.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
