"""
LLM-as-Judge critic for KIRA evals.

Given a conversation trace and a scenario's expectations,
asks the LLM to score the agent's final answer on three dimensions:
  - Correctness  (0-40): Does the answer correctly solve the user's problem?
  - Completeness (0-30): Are all expected topics covered?
  - Groundedness (0-30): Is the answer derived from retrieved knowledge, not hallucinated?

Returns a CriticResult with per-dimension scores, total, and reasoning.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from groq import Groq

CRITIC_MODEL = "llama-3.3-70b-versatile"

CRITIC_PROMPT = """You are a strict evaluator for an AI agent called KIRA.

## Scenario
User question: {question}

Expected answer theme:
{expected_theme}

Topics that MUST be covered: {topics}

## Agent conversation (last assistant message is the final answer)
{conversation}

## Scoring task
Score the FINAL ASSISTANT ANSWER only (not the tool calls) on these three dimensions.
Reply ONLY with valid JSON — no extra text, no markdown fence.

{{
  "correctness": <int 0-40>,
  "completeness": <int 0-30>,
  "groundedness": <int 0-30>,
  "reasoning": "<one sentence per dimension, separated by |>"
}}

Scoring guide:
- correctness  40 = fully correct and actionable; 0 = wrong or irrelevant
- completeness 30 = all listed topics addressed; 0 = none addressed
- groundedness 30 = every claim traceable to retrieved context; 0 = pure hallucination
"""


@dataclass
class CriticResult:
    correctness: int
    completeness: int
    groundedness: int
    total: int
    reasoning: str
    raw_response: str


def score(
    groq_client: Groq,
    question: str,
    expected_theme: str,
    expected_topics: list[str],
    messages: list[dict],
) -> CriticResult:
    """Call the LLM critic and parse its JSON score."""

    # Build a readable transcript of the conversation (skip the system prompt)
    lines: list[str] = []
    for m in messages:
        role = m.get("role", "")
        if role == "system":
            continue
        if role == "assistant":
            tool_calls = m.get("tool_calls") or []
            if tool_calls:
                names = [tc["function"]["name"] for tc in tool_calls]
                lines.append(f"[ASSISTANT called tools: {', '.join(names)}]")
            else:
                lines.append(f"ASSISTANT: {m.get('content', '')}")
        elif role == "tool":
            content = str(m.get("content", ""))[:200]
            lines.append(f"  TOOL RESULT: {content}...")
        elif role == "user":
            lines.append(f"USER: {m.get('content', '')}")

    conversation = "\n".join(lines)

    prompt = CRITIC_PROMPT.format(
        question=question,
        expected_theme=expected_theme.strip(),
        topics=", ".join(expected_topics),
        conversation=conversation,
    )

    response = groq_client.chat.completions.create(
        model=CRITIC_MODEL,
        temperature=0.0,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.choices[0].message.content or "{}"

    # Strip markdown fences if the model wrapped the JSON anyway
    raw_clean = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip(), flags=re.DOTALL)

    try:
        data = json.loads(raw_clean)
    except json.JSONDecodeError:
        return CriticResult(
            correctness=0,
            completeness=0,
            groundedness=0,
            total=0,
            reasoning="[Critic parse error — raw response below]",
            raw_response=raw,
        )

    c = int(data.get("correctness", 0))
    cm = int(data.get("completeness", 0))
    g = int(data.get("groundedness", 0))

    return CriticResult(
        correctness=c,
        completeness=cm,
        groundedness=g,
        total=c + cm + g,
        reasoning=data.get("reasoning", ""),
        raw_response=raw,
    )
