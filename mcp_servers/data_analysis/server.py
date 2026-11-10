import csv
from pathlib import Path
from typing import Literal

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("research-tools")


@mcp.tool()
def analyze_dataset(
    data_ref: Literal["sales"],
    task: Literal["summary", "columns", "missing_values"],
) -> dict:
    """Run one of the supported analyses on an approved CSV dataset."""
    path = DATASETS[data_ref].resolve()

    try:
        path.relative_to(ROOT)
    except ValueError:
        raise ValueError("Dataset is outside the approved directory")

    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if task == "columns":
        return {"columns": list(rows[0].keys()) if rows else []}

    if task == "missing_values":
        columns = list(rows[0].keys()) if rows else []
        return {
            "missing_by_column": {
                column: sum(not row.get(column) for row in rows)
                for column in columns
            }
        }

    return {
        "row_count": len(rows),
        "columns": list(rows[0].keys()) if rows else [],
    }
if __name__ == "__main__":
    mcp.run()
