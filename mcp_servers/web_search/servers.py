# mcp_servers/web_search/servers.py
import os
#from mcp.server.fastmcp import FastMfrom mcp.server.mcpserver import MCPServerCP
from mcp.server.mcpserver import MCPServer

#mcp = FastMCP("web-search")
mcp = MCPServer("web-search")

@mcp.tool()
def web_search(query: str, max_results: int = 5) -> str:
    """Search the web. Returns titles, URLs, and snippets."""
    try:
        from ddgs import DDGS
    except ImportError:
        return "Error: duckduckgo-search not installed. Run: pip install duckduckgo-search"

    results = []
    try:
        ddgs=DDGS()
        items = ddgs.text(query, max_results=max_results)
        if items:
            for r in items:
                results.append(
                    f"Title: {r.get('title', "N/A")}\n"
                    f"URL: {r.get('href', "N/A")}\n"
                    f"Snippet: {r.get('body', "N/A")}\n"
                )
    except Exception as e:
        return f"Search failed: {e}"

    return "\n---\n".join(results) if results else "No results found."

if __name__ == "__main__":
    mcp.run(transport="stdio")
