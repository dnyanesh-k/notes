"""
Pre-tool authorization hook.
Called before every tool execution.
Returns (decision, reason): decision is 'allow' or 'block'.
"""

from __future__ import annotations
import yaml
from pathlib import Path


def _load_persona(name: str) -> dict:
    config = yaml.safe_load(Path("persona.yaml").read_text(encoding="utf-8"))
    personas = config.get("personas", {})
    if name not in personas:
        available = list(personas.keys())
        raise ValueError(f"Unknown persona '{name}'. Available: {available}")
    return personas[name]


def check_tool(persona_name: str, tool_name: str, environment: str = "dev") -> tuple[str, str]:
    """
    Authorize a tool call for a given persona and environment.

    Returns:
        ('allow', 'authorized')  — tool may proceed
        ('block', reason)        — tool is denied; reason is shown to user
    """
    persona = _load_persona(persona_name)

    # 1. Environment check
    allowed_envs = persona.get("environments", [])
    if environment not in allowed_envs:
        return (
            "block",
            f"Persona '{persona_name}' is not authorized in environment '{environment}'. "
            f"Allowed environments: {allowed_envs}",
        )

    # 2. Explicit deny list takes priority
    denied = persona.get("denied_tools", [])
    if tool_name in denied:
        return "block", f"Tool '{tool_name}' is explicitly denied for persona '{persona_name}'"

    # 3. Allow list (if defined — empty list means allow all)
    allowed = persona.get("allowed_tools", [])
    if allowed and tool_name not in allowed:
        return (
            "block",
            f"Tool '{tool_name}' is not in the allow list for persona '{persona_name}'. "
            f"Allowed: {allowed}",
        )

    return "allow", "authorized"


if __name__ == "__main__":
    # Smoke test
    print(check_tool("engineer", "search_kb", "dev"))    # allow
    print(check_tool("viewer",   "bash",       "dev"))   # block - denied
    print(check_tool("viewer",   "search_kb",  "prod"))  # block - wrong env
