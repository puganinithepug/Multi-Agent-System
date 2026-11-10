from typing import Literal

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("research-tools")
@mcp.tool()
def run_sandboxed(
    job_id: Literal["summarize_dataset", "extract_text"],
    data_ref: Literal["sales"],
) -> dict:
    """Submit an allowlisted job to the separately managed sandbox."""
    # Delegate to a sandbox service; don't use eval() or exec() here.
    # The service should only accept approved job IDs and approved inputs.
    return sandbox_gateway.submit(job_id=job_id, data_ref=data_ref)


if __name__ == "__main__":
    mcp.run()
