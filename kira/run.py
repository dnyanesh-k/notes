"""
KIRA — entry point.

Usage:
    python run.py                        # persona=engineer, env=dev
    python run.py --persona viewer       # read-only persona
    python run.py --persona engineer --env staging

Requires:
    GROQ_API_KEY environment variable set.
    Get a free key at https://console.groq.com
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

from groq import Groq
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

import hooks

GROQ_MODEL = "llama-3.3-70b-versatile"
SYSTEM_PROMPT_FILE = Path(__file__).parent / "system_prompt.md"


def _load_system_prompt() -> str:
    """Load system prompt from system_prompt.md — editable without touching code."""
    if SYSTEM_PROMPT_FILE.exists():
        return SYSTEM_PROMPT_FILE.read_text(encoding="utf-8")
    # Fallback if file missing
    return (
        "You are KIRA. Call search_kb first, then read_file, then answer. "
        "Do not answer without retrieving knowledge first."
    )


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _mcp_tool_to_groq(tool) -> dict:
    """Convert an MCP Tool object to OpenAI/Groq function-calling schema."""
    schema = tool.inputSchema
    # inputSchema may be a dict or a Pydantic model depending on mcp version
    if hasattr(schema, "model_json_schema"):
        schema = schema.model_json_schema()
    elif hasattr(schema, "dict"):
        schema = schema.dict()
    if not isinstance(schema, dict):
        schema = {"type": "object", "properties": {}}
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description or "",
            "parameters": schema,
        },
    }


READ_FILE_TOOL = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "Read a markdown file from the brain/ directory.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Filename inside brain/, e.g. 'knowledge_card.md'",
                }
            },
            "required": ["path"],
        },
    },
}


def _execute_read_file(path_arg: str) -> str:
    """Built-in file reader — scoped to brain/ directory only."""
    # Security: only allow reads inside brain/
    target = (Path("brain") / Path(path_arg).name).resolve()
    brain_dir = Path("brain").resolve()
    if not str(target).startswith(str(brain_dir)):
        return "Error: access outside brain/ directory is not allowed."
    if not target.exists():
        return f"File not found: brain/{Path(path_arg).name}"
    if target.suffix not in (".md", ".txt", ".yaml", ".yml"):
        return "Error: only .md, .txt, .yaml files are readable."
    return target.read_text(encoding="utf-8")


# ─── Agent loop ──────────────────────────────────────────────────────────────

def _log(label: str, text: str = "", width: int = 55) -> None:
    """Print a labelled log line with consistent formatting."""
    if text:
        print(f"  {label:<14} {text}")
    else:
        print(f"  {label}")


def _divider(char: str = "-", width: int = 55) -> None:
    print(f"  {char * width}")


async def _agent_loop(
    groq: Groq,
    session: ClientSession,
    mcp_tool_names: set[str],
    groq_tools: list[dict],
    persona: str,
    environment: str,
    user_input: str,
) -> None:
    import time

    messages: list[dict] = [
        {"role": "system", "content": _load_system_prompt()},
        {"role": "user", "content": user_input},
    ]

    step = 0
    print()
    _divider("─")

    while True:
        step += 1
        _log(f"[Step {step}]", f"Calling {GROQ_MODEL}...")
        t0 = time.time()

        response = groq.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            tools=groq_tools,
            tool_choice="auto",
            max_tokens=2048,
            temperature=0.1,
        )

        elapsed = time.time() - t0
        choice = response.choices[0]
        msg = choice.message
        usage = response.usage
        _log("  └─ LLM", f"{elapsed:.1f}s | in={usage.prompt_tokens} out={usage.completion_tokens} tokens")

        # No tool calls — final answer
        if not msg.tool_calls:
            _divider("─")
            print(f"\KIRA:\n{msg.content or '(no response)'}\n")
            _divider("═")
            return

        # Show what the model decided to do
        tool_names_called = [tc.function.name for tc in msg.tool_calls]
        _log("  └─ Tools", f"Requesting: {', '.join(tool_names_called)}")

        # Build assistant message dict
        assistant_entry: dict = {"role": "assistant", "content": msg.content or ""}
        assistant_entry["tool_calls"] = [
            {
                "id": tc.id,
                "type": "function",
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments,
                },
            }
            for tc in msg.tool_calls
        ]
        messages.append(assistant_entry)

        # Execute each tool call
        for tc in msg.tool_calls:
            tool_name = tc.function.name
            try:
                args = json.loads(tc.function.arguments)
            except (json.JSONDecodeError, TypeError):
                args = {}

            print()
            _log(f"[{tool_name}]", json.dumps(args, ensure_ascii=False))

            # Guardrail check — always show decision
            decision, reason = hooks.check_tool(persona, tool_name, environment)
            if decision == "block":
                _log("  └─ Guardrail", f"BLOCKED — {reason}")
                result = f"[BLOCKED by guardrail] {reason}"
            else:
                _log("  └─ Guardrail", f"ALLOWED ({persona} / {environment})")

                t1 = time.time()
                if tool_name in mcp_tool_names:
                    mcp_result = await session.call_tool(tool_name, args)
                    result = mcp_result.content[0].text if mcp_result.content else "(empty)"
                elif tool_name == "read_file":
                    result = _execute_read_file(args.get("path", ""))
                else:
                    result = f"Unknown tool: {tool_name}"
                tool_ms = (time.time() - t1) * 1000

                # Format result preview — for search_kb show all matched lines
                lines = result.strip().splitlines()
                if tool_name == "search_kb":
                    _log("  └─ Result", f"({tool_ms:.0f}ms)")
                    for line in lines:
                        if line.strip():
                            print(f"             {line.strip()}")
                else:
                    preview = result[:140].replace("\n", " ")
                    suffix = "..." if len(result) > 140 else ""
                    _log("  └─ Result", f"({tool_ms:.0f}ms) {preview}{suffix}")

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })


# ─── Main ────────────────────────────────────────────────────────────────────

async def main(persona: str, environment: str) -> None:
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key:
        print("\nError: GROQ_API_KEY is not set.")
        print("  1. Get a free key at https://console.groq.com")
        print("  2. Set it:  export GROQ_API_KEY=your_key_here")
        sys.exit(1)

    groq = Groq(api_key=api_key)

    print(f"\n{'═'*57}")
    print(f"  KIRA")
    print(f"  Persona : {persona}  |  Environment : {environment}")
    print(f"  Model   : {GROQ_MODEL}")
    print(f"{'═'*57}")
    print()
    print("  [Boot] Loading MiniLM model + building routing index...")
    print("         (first run downloads ~100MB — subsequent runs are instant)")
    print()

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(Path(__file__).parent / "mcp_server.py")],
        env=None,
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools_response = await session.list_tools()
            mcp_tool_names = {t.name for t in tools_response.tools}
            groq_tools = [_mcp_tool_to_groq(t) for t in tools_response.tools]
            groq_tools.append(READ_FILE_TOOL)

            # Show routing index size
            from routing_core import _get_index
            index = _get_index()
            print(f"  [Boot] System prompt      — {SYSTEM_PROMPT_FILE.name}")
            print(f"  [Boot] MCP server started  — tools : {sorted(mcp_tool_names)}")
            print(f"  [Boot] Routing index ready — {len(index)} entries loaded from brain/routing.md")
            print()
            print(f"{'─'*57}")
            print(f"  Ready. Type your question or 'exit' to quit.")
            print(f"{'─'*57}")

            while True:
                try:
                    user_input = input("You: ").strip()
                except (EOFError, KeyboardInterrupt):
                    print("\nExiting.")
                    break

                if not user_input:
                    continue
                if user_input.lower() in ("exit", "quit", "q"):
                    print("Goodbye.")
                    break

                await _agent_loop(
                    groq=groq,
                    session=session,
                    mcp_tool_names=mcp_tool_names,
                    groq_tools=groq_tools,
                    persona=persona,
                    environment=environment,
                    user_input=user_input,
                )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="KIRA — AI assistant POC")
    parser.add_argument(
        "--persona",
        default="engineer",
        choices=["viewer", "engineer"],
        help="Persona to run as (default: engineer)",
    )
    parser.add_argument(
        "--env",
        default="dev",
        choices=["dev", "staging"],
        help="Environment (default: dev)",
    )
    args = parser.parse_args()
    asyncio.run(main(args.persona, args.env))
