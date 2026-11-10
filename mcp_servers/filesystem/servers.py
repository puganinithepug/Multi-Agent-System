# mcp_servers/file_search/server.py
import os
import hashlib
from pathlib import Path
#from mcp.server.fastmcp import FastMCP
from mcp.server.mcpserver import MCPServer

# Configuration
DATA_DIR = Path(os.getenv("SEARCH_DATA_DIR", "./data")).resolve()
ALLOWED_EXTENSIONS = {".pdf", ".csv", ".json", ".pbi", ".pbix"}

#mcp = FastMCP("file-search")
mcp = MCPServer("file-search")

@mcp.tool()
def search_local_files(query: str, extensions: list[str] | None = None) -> str:
    """
    Search local files (read-only).
    
    Args:
        query: Search term to find in file content or filename.
        extensions: Optional list of extensions to filter (e.g., ['.csv', '.json']).
                    Defaults to all allowed types if None.
    
    Returns:
        List of matching files with content snippets.
    """
    # Validate inputs
    if not query:
        return "Error: query cannot be empty."
    
    if extensions:
        # Filter allowed extensions to only those in ALLOWED_EXTENSIONS
        valid_exts = [ext for ext in extensions if ext.lower() in ALLOWED_EXTENSIONS]
        if not valid_exts:
            return f"Error: Invalid extensions. Allowed: {ALLOWED_EXTENSIONS}"
        search_exts = valid_exts
    else:
        search_exts = list(ALLOWED_EXTENSIONS)

    matches = []
    
    # Security: Ensure we don't escape the data directory
    try:
        DATA_DIR.relative_to(Path.cwd().resolve())
    except ValueError:
        return f"Error: SEARCH_DATA_DIR must be relative to project root."

    for path in DATA_DIR.rglob("*"):
        if not path.is_file():
            continue
        
        ext = path.suffix.lower()
        if ext not in search_exts:
            continue
        
        # Security Check: Resolve path and ensure it's inside DATA_DIR
        try:
            path.resolve().relative_to(DATA_DIR)
        except ValueError:
            continue

        # Search logic
        result = _search_file(path, query)
        if result:
            matches.append(result)

    if not matches:
        return "No matches found."
    
    return "\n---\n".join(matches[:20])  # Limit to 20 results to avoid context overflow


def _search_file(filepath: Path, query: str) -> str | None:
    """Search a single file and return snippet if found."""
    query_lower = query.lower()
    
    if filepath.suffix.lower() in {".csv", ".json"}:
        try:
            text = filepath.read_text(encoding="utf-8", errors="ignore")
            lines = []
            for i, line in enumerate(text.splitlines(), 1):
                if query_lower in line.lower():
                    # Get context: 2 lines before and after
                    start = max(0, i - 3)
                    end = min(len(text.splitlines()), i + 2)
                    context_lines = text.splitlines()[start:end]
                    snippet = "\n".join(context_lines)
                    lines.append(f"[{filepath.name}:{i}] {snippet}")
            
            if lines:
                return f"File: {filepath}\nMatches:\n" + "\n".join(lines[:5])
        except Exception as e:
            return f"File: {filepath}\nError reading: {e}"
    
    elif filepath.suffix.lower() in {".pdf", ".pbi", ".pbix"}:
        # For binary formats, only search filename
        if query_lower in filepath.name.lower():
            return f"File: {filepath}\nType: {filepath.suffix}\nNote: Content search not supported for binary files."
    
    return None


if __name__ == "__main__":
    # Verify data dir exists
    if not DATA_DIR.exists():
        print(f"Warning: Data directory {DATA_DIR} does not exist. Creating it.")
        DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    mcp.run(transport="stdio")
