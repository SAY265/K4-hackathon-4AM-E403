"""Run chatbot Golden Set against OpenRouter and preserve every output."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from codebase.quiz_ai import ChatRequest, OpenRouterClient  # noqa: E402
from eval.chat_evaluator import evaluate_chat_case  # noqa: E402


def run(golden_set: Path, output_path: Path, model: str) -> None:
    cases = json.loads(golden_set.read_text(encoding="utf-8"))
    client = OpenRouterClient(model=model)
    results = [_run_case(client, case) for case in cases]
    passed = sum(item["evaluation"]["passed"] for item in results)
    report = {
        "run_at_utc": datetime.now(timezone.utc).isoformat(),
        "model": model,
        "total": len(results),
        "passed": passed,
        "pass_rate_percent": round(100 * passed / len(results), 2),
        "results": results,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"{passed}/{len(results)} passed ({report['pass_rate_percent']}%)")
    print(f"Saved: {output_path}")


def _run_case(
    client: OpenRouterClient, case: dict[str, Any]
) -> dict[str, Any]:
    try:
        response = client.answer(
            ChatRequest(case["slide_context"], case["question"]),
            history=case.get("history", []),
        )
        evaluation = evaluate_chat_case(case, response)
        return {
            "case_id": case["id"],
            "output": response,
            "evaluation": evaluation,
        }
    except (RuntimeError, ValueError, KeyError) as error:
        return {
            "case_id": case["id"],
            "output": None,
            "evaluation": {
                "case_id": case["id"],
                "passed": False,
                "failures": [str(error)],
                "checks": {
                    "behavior": False,
                    "citation": False,
                    "content": False,
                },
            },
        }


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--golden-set",
        type=Path,
        default=ROOT / "eval" / "chat_golden_set.json",
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model", default="openai/gpt-4o-mini")
    return parser.parse_args()


if __name__ == "__main__":
    args = arguments()
    run(args.golden_set, args.output, args.model)
