"""
KIRA Eval Runner
================
Runs all scenario YAML files through the agent and scores them.

Usage:
    python evals/run_evals.py [--scenario deploy_service]

Each scenario YAML defines:
  - A user prompt
  - Hard gates  (search_kb order, required cards)
  - LLM critic  (expected topics, answer theme, pass threshold)

The runner prints a per-scenario report and a summary table.
Exit code 0 = all pass, 1 = any failure.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

import yaml
from groq import Groq
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Add kira root to path so imports work
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

import run as agent_run        # noqa: E402
from evals import critic       # noqa: E402

SCENARIO_DIR = Path(__file__).parent / "scenarios"

# ─── Hard Gate Checkers ────────────────────────────────────────────────────────

def _all_tool_calls(messages: list[dict]) -> list[str]:
    """Return tool call names in the order they were made."""
    names: list[str] = []
    for m in messages:
        for tc in m.get("tool_calls") or []:
            names.append(tc["function"]["name"])
    return names


def _files_read(messages: list[dict]) -> list[str]:
    """Return all file paths passed to read_file throughout the conversation."""
    paths: list[str] = []
    for m in messages:
        for tc in m.get("tool_calls") or []:
            if tc["function"]["name"] == "read_file":
                try:
                    args = json.loads(tc["function"]["arguments"])
                    paths.append(args.get("path", ""))
                except Exception:
                    pass
    return paths


def check_hard_gates(scenario: dict, messages: list[dict]) -> list[str]:
    """
    Returns a list of gate failure descriptions.
    Empty list = all gates passed.
    """
    failures: list[str] = []
    gates = scenario.get("hard_gates", {})
    tool_order = _all_tool_calls(messages)

    # Gate 1: search_kb must be the very first tool called
    if gates.get("search_kb_must_be_first"):
        if not tool_order:
            failures.append("GATE FAIL: No tools were called at all (search_kb never invoked).")
        elif tool_order[0] != "search_kb":
            failures.append(
                f"GATE FAIL: search_kb was not first — first tool was '{tool_order[0]}'."
            )

    # Gate 2: required cards must have been loaded via read_file
    required_cards: list[str] = gates.get("required_cards", [])
    files_read = _files_read(messages)
    for card in required_cards:
        matched = any(card in fp for fp in files_read)
        if not matched:
            failures.append(f"GATE FAIL: Required card '{card}' was never passed to read_file.")

    return failures


# ─── Single Scenario Runner ───────────────────────────────────────────────────

def _build_mock_tools(scenario: dict) -> dict | None:
    """
    Convert mock_responses from the scenario YAML into the dict format
    _agent_loop expects:
      { "search_kb": "<string>", "read_file": { "filename_substr": "<content>" } }
    Returns None if no mock_responses defined (eval runs against live tools).
    """
    raw = scenario.get("mock_responses")
    if not raw:
        return None
    mock: dict = {}
    for tool, value in raw.items():
        mock[tool] = value
    return mock


async def run_scenario(
    scenario: dict,
    groq_client: Groq,
    persona: str = "engineer",
    environment: str = "dev",
) -> dict:
    """
    Runs one scenario through the agent, runs hard gates and the LLM critic.
    Returns a result dict.

    If the scenario defines mock_responses, the mock proxy is used —
    no MCP server subprocess or MiniLM embeddings are needed.
    """
    name = scenario["name"]
    prompt = scenario["prompt"]
    threshold = scenario.get("pass_threshold", 75)

    mock_tools = _build_mock_tools(scenario)
    using_mock = mock_tools is not None

    # Boot the MCP server only when NOT using mock proxy
    server_params = StdioServerParameters(
        command="python",
        args=[str(ROOT / "mcp_server.py")],
        cwd=str(ROOT),
    )

    messages: list[dict] = []
    final_answer: str = ""

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            mcp_tool_names, groq_tools = await agent_run._build_tools(session)

            messages, final_answer = await agent_run._agent_loop(
                groq=groq_client,
                session=session,
                mcp_tool_names=mcp_tool_names,
                groq_tools=groq_tools,
                persona=persona,
                environment=environment,
                user_input=prompt,
                silent=True,
                mock_tools=mock_tools,   # None = real tools; dict = mock proxy
            )

    # Hard gates
    gate_failures = check_hard_gates(scenario, messages)

    # LLM critic
    critic_result = critic.score(
        groq_client=groq_client,
        question=prompt,
        expected_theme=scenario.get("expected_answer_theme", ""),
        expected_topics=scenario.get("expected_topics", []),
        messages=messages,
    )

    passed = len(gate_failures) == 0 and critic_result.total >= threshold

    return {
        "name": name,
        "passed": passed,
        "gate_failures": gate_failures,
        "critic": critic_result,
        "threshold": threshold,
        "final_answer": final_answer,
        "using_mock": using_mock,
    }


# ─── Reporter ─────────────────────────────────────────────────────────────────

def _bar(score: int, max_score: int, width: int = 20) -> str:
    filled = round(width * score / max_score) if max_score else 0
    return "█" * filled + "░" * (width - filled)


def print_result(result: dict) -> None:
    name = result["name"]
    status = "✓  PASS" if result["passed"] else "✗  FAIL"
    c = result["critic"]
    threshold = result["threshold"]
    mode = "mock proxy" if result.get("using_mock") else "live tools"

    print()
    print(f"  {'═' * 55}")
    print(f"  Scenario : {name}   [{mode}]")
    print(f"  Status   : {status}   (need ≥{threshold}, got {c.total}/100)")
    print(f"  {'─' * 55}")

    # Hard gates
    if result["gate_failures"]:
        for f in result["gate_failures"]:
            print(f"  {f}")
    else:
        print("  Hard gates  : all passed")

    print(f"  {'─' * 55}")

    # Critic scores
    print(f"  Correctness  {c.correctness:>3}/40  {_bar(c.correctness, 40)}")
    print(f"  Completeness {c.completeness:>3}/30  {_bar(c.completeness, 30)}")
    print(f"  Groundedness {c.groundedness:>3}/30  {_bar(c.groundedness, 30)}")
    print(f"  Total        {c.total:>3}/100")
    print(f"  {'─' * 55}")

    # Critic reasoning
    for part in c.reasoning.split("|"):
        part = part.strip()
        if part:
            print(f"  > {part}")

    print(f"  {'─' * 55}")
    print(f"  Agent answer (truncated):")
    answer_preview = (result["final_answer"] or "")[:300].replace("\n", " ")
    print(f"    {answer_preview}{'...' if len(result['final_answer']) > 300 else ''}")


def print_summary(results: list[dict]) -> None:
    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    print()
    print(f"  {'═' * 55}")
    print(f"  EVAL SUMMARY  —  {passed}/{total} scenarios passed")
    print(f"  {'─' * 55}")
    for r in results:
        mark = "✓" if r["passed"] else "✗"
        c = r["critic"]
        print(f"  {mark}  {r['name']:<30}  {c.total:>3}/100")
    print(f"  {'═' * 55}")
    print()


# ─── Entry Point ─────────────────────────────────────────────────────────────

async def main(filter_name: str | None) -> int:
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key:
        print("Error: GROQ_API_KEY is not set.")
        sys.exit(1)

    groq_client = Groq(api_key=api_key)

    # Load scenarios
    scenario_files = sorted(SCENARIO_DIR.glob("*.yaml"))
    if not scenario_files:
        print(f"No scenario YAML files found in {SCENARIO_DIR}")
        return 1

    if filter_name:
        scenario_files = [f for f in scenario_files if filter_name in f.stem]
        if not scenario_files:
            print(f"No scenario matches '{filter_name}'")
            return 1

    print()
    print("  KIRA Eval Runner")
    print(f"  Running {len(scenario_files)} scenario(s)...")

    results: list[dict] = []
    for sf in scenario_files:
        scenario = yaml.safe_load(sf.read_text(encoding="utf-8"))
        print(f"\n  > Running: {scenario['name']}...")
        result = await run_scenario(scenario, groq_client)
        results.append(result)
        print_result(result)

    print_summary(results)
    return 0 if all(r["passed"] for r in results) else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="KIRA Eval Runner")
    parser.add_argument(
        "--scenario",
        default=None,
        help="Filter by scenario name (substring match). Omit to run all.",
    )
    args = parser.parse_args()

    code = asyncio.run(main(args.scenario))
    sys.exit(code)
