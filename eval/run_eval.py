"""Run the Role 2 golden set against OpenRouter and save an immutable result."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from codebase.quiz_ai import OpenRouterClient, QuizRequest  # noqa: E402
from eval.evaluator import evaluate_case  # noqa: E402


def run(golden_set_path: Path, output_path: Path, model: str) -> None:
    cases = json.loads(golden_set_path.read_text(encoding="utf-8"))
    client = OpenRouterClient(model=model)
    results = [_run_case(client, case) for case in cases]
    passed = sum(result["evaluation"]["passed"] for result in results)
    report = {
        "run_at_utc": datetime.now(timezone.utc).isoformat(),
        "model": model,
        "total": len(results),
        "passed": passed,
        "pass_rate_percent": round(passed / len(results) * 100, 2),
        "results": results,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"{passed}/{len(results)} passed ({report['pass_rate_percent']}%)")
    print(f"Saved: {output_path}")


def _run_case(client: OpenRouterClient, case: dict[str, Any]) -> dict[str, Any]:
    request = QuizRequest(
        slide_context=case["slide_context"],
        question_count=case.get("question_count", 1),
        user_instruction=case["user_instruction"],
    )
    try:
        output = client.generate_quiz(request)
        evaluation = evaluate_case(case, output)
        return {"case_id": case["id"], "output": output, "evaluation": evaluation}
    except (RuntimeError, ValueError, KeyError) as error:
        return {
            "case_id": case["id"],
            "output": None,
            "error": str(error),
            "evaluation": {
                "case_id": case["id"],
                "passed": False,
                "failures": [str(error)],
                "checks": {"behavior": False, "citation": False, "grounding": False},
            },
        }


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--golden-set", type=Path, default=ROOT / "eval" / "golden_set.json"
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model", default="openai/gpt-4o-mini")
    return parser.parse_args()


if __name__ == "__main__":
    arguments = _arguments()
    run(arguments.golden_set, arguments.output, arguments.model)
