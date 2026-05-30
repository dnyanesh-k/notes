"""
kira-brain MCP server.
Exposes search_kb as an MCP tool over stdio transport.
Run standalone: python mcp_server.py
"""

from mcp.server.fastmcp import FastMCP
from routing_core import search as _search

mcp = FastMCP("kira-brain")


@mcp.tool()
def search_kb(queries: list[str]) -> str:
    """
    Search the KIRA knowledge base for relevant cards.

    IMPORTANT: Call this tool FIRST before any other action on every turn.
    Pass 2-5 short keyword phrases that describe the user's question.

    Returns: matched knowledge card file paths to load, with relevance scores.
    """
    return _search(queries)


if __name__ == "__main__":
    mcp.run()
