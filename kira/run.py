"""
ARIA Mini — entry point.

Usage:
    python run.py                        # persona=engineer, env=dev
    python run.py --persona viewer       # read-only persona
    python run.py --persona engineer --env staging

Requires:
    Copy .env.example to .env and set GROQ_API_KEY (or provider key for LLM_MODEL).
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

import hooks
import llm_client

SYSTEM_PROMPT_FILE = Path(__file__).parent / "system_prompt.md"


def _load_system_prompt() -> str:
    """Load system prompt from system_prompt.md — editable without touching code."""
    if SYSTEM_PROMPT_FILE.exists():
        return SYSTEM_PROMPT_FILE.read_text(encoding="utf-8")
    # Fallback if file missing
    return (
        "You are ARIA. Call search_kb first, then read_file, then answer. "
        "Do not answer without retrieving knowledge first."
    )


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _mcp_tool_to_schema(tool) -> dict:
    """Convert an MCP Tool object to OpenAI function-calling schema."""
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
    session: ClientSession,
    mcp_tool_names: set[str],
    llm_tools: list[dict],
    persona: str,
    environment: str,
    user_input: str,
    silent: bool = False,                  # True in eval mode — suppresses all prints
    mock_tools: dict | None = None,        # mock proxy: tool_name → canned response string
) -> tuple[list[dict], str]:               # returns (messages, final_answer)
    import time

    messages: list[dict] = [
        {"role": "system", "content": _load_system_prompt()},
        {"role": "user", "content": user_input},
    ]

    def _p(*args, **kwargs):
        if not silent:
            print(*args, **kwargs)

    def _lg(label, text=""):
        if not silent:
            _log(label, text)

    step = 0
    _p()
    if not silent:
        _divider("─")

    while True:
        step += 1
        model = llm_client.get_agent_model()
        _lg(f"[Step {step}]", f"Calling {model} via LiteLLM...")
        t0 = time.time()

        response = llm_client.chat_completion(
            model=model,
            messages=messages,
            tools=llm_tools,
            tool_choice="auto",
            max_tokens=2048,
            temperature=0.1,
        )

        elapsed = time.time() - t0
        choice = response.choices[0]
        msg = choice.message
        usage = response.usage
        _lg("  └─ LLM", f"{elapsed:.1f}s | in={usage.prompt_tokens} out={usage.completion_tokens} tokens")

        # No tool calls — final answer
        if not msg.tool_calls:
            final_answer = msg.content or "(no response)"
            if not silent:
                _divider("─")
                _p(f"\nARIA:\n{final_answer}\n")
                _divider("═")
            return messages, final_answer

        # Show what the model decided to do
        tool_names_called = [tc.function.name for tc in msg.tool_calls]
        _lg("  └─ Tools", f"Requesting: {', '.join(tool_names_called)}")

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

            _p()
            _lg(f"[{tool_name}]", json.dumps(args, ensure_ascii=False))

            # Guardrail check — always show decision
            decision, reason = hooks.check_tool(persona, tool_name, environment)
            if decision == "block":
                _lg("  └─ Guardrail", f"BLOCKED — {reason}")
                result = f"[BLOCKED by guardrail] {reason}"
            else:
                _lg("  └─ Guardrail", f"ALLOWED ({persona} / {environment})")

                t1 = time.time()
                # Mock proxy: if canned response exists for this tool, use it
                if mock_tools and tool_name in mock_tools:
                    mock_resp = mock_tools[tool_name]
                    # read_file mock is a dict keyed by filename substring
                    if isinstance(mock_resp, dict):
                        path_arg = args.get("path", "")
                        result = next(
                            (v for k, v in mock_resp.items() if k in path_arg),
                            f"[mock] No canned response for path: {path_arg}",
                        )
                    else:
                        result = mock_resp
                elif tool_name in mcp_tool_names:
                    mcp_result = await session.call_tool(tool_name, args)
                    result = mcp_result.content[0].text if mcp_result.content else "(empty)"
                elif tool_name == "read_file":
                    result = _execute_read_file(args.get("path", ""))
                else:
                    result = f"Unknown tool: {tool_name}"
                tool_ms = (time.time() - t1) * 1000

                # Format result preview — for search_kb show all matched lines
                lines = result.strip().splitlines()
                if tool_name == "search_kb" and not silent:
                    _log("  └─ Result", f"({tool_ms:.0f}ms)")
                    for line in lines:
                        if line.strip():
                            print(f"             {line.strip()}")
                elif not silent:
                    preview = result[:140].replace("\n", " ")
                    suffix = "..." if len(result) > 140 else ""
                    _log("  └─ Result", f"({tool_ms:.0f}ms) {preview}{suffix}")

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })

    # Safety fallback — should not be reached in normal operation
    return messages, "(agent loop exceeded max steps)"


# ─── Main ────────────────────────────────────────────────────────────────────

async def _build_tools(session: ClientSession) -> tuple[set[str], list[dict]]:
    """Ask MCP server for its tool list and convert to OpenAI schema.
    Also appends the built-in read_file tool. Reusable by eval runner."""
    tools_response = await session.list_tools()
    mcp_tool_names = {t.name for t in tools_response.tools}
    llm_tools = [_mcp_tool_to_schema(t) for t in tools_response.tools]
    llm_tools.append(READ_FILE_TOOL)
    return mcp_tool_names, llm_tools


async def main(persona: str, environment: str) -> None:
    llm_client.check_llm_env()

    agent_model = llm_client.get_agent_model()
    fallback = llm_client.get_fallback_model()

    print(f"\n{'═'*57}")
    print(f"  ARIA Mini")
    print(f"  Persona : {persona}  |  Environment : {environment}")
    print(f"  Gateway : LiteLLM")
    print(f"  Model   : {agent_model}")
    if fallback:
        print(f"  Fallback: {fallback}")
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

            mcp_tool_names, llm_tools = await _build_tools(session)

            # Show routing index size; start hot-reload watcher
            from routing_core import _get_index, start_watcher
            index = _get_index()
            start_watcher()
            print(f"  [Boot] System prompt      — {SYSTEM_PROMPT_FILE.name}")
            print(f"  [Boot] MCP server started  — tools : {sorted(mcp_tool_names)}")
            print(f"  [Boot] Routing index ready — {len(index)} entries loaded from brain/routing.md")
            print(f"  [Boot] Index snapshot      — brain/index_snapshot.json (human-readable, updates on reload)")
            print(f"  [Boot] Hot-reload watcher  — watching brain/routing.md every 2s")
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
                    session=session,
                    mcp_tool_names=mcp_tool_names,
                    llm_tools=llm_tools,
                    persona=persona,
                    environment=environment,
                    user_input=user_input,
                    silent=False,
                )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ARIA Mini — AI assistant POC")
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
