import csv
from pathlib import Path
from typing import Literal

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("research-tools")
@mcp.tool()
def generate_report(
    title: str,
    findings: list[str],
    format: Literal["markdown"] = "markdown",
) -> str:
    """Format supplied findings as a Markdown report."""
    bullets = "\n".join(f"- {finding}" for finding in findings)
    return f"# {title}\n\n{bullets}"

if __name__ == "__main__":
    mcp.run()
