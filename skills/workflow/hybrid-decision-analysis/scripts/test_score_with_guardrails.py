#!/usr/bin/env python3
"""Regression tests for hybrid guardrail scoring."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).with_name("score_with_guardrails.py")


def _run(input_data: dict[str, Any], extra_args: list[str] | None = None) -> tuple[subprocess.CompletedProcess[str], dict[str, Any] | None]:
    if extra_args is None:
        extra_args = []

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        input_path = tmp_path / "input.json"
        output_path = tmp_path / "output.json"
        input_path.write_text(json.dumps(input_data), encoding="utf-8")

        cmd = [
            "python3",
            str(SCRIPT),
            "--input",
            str(input_path),
            "--json-output",
            str(output_path),
            *extra_args,
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if proc.returncode != 0:
            return proc, None

        result = json.loads(output_path.read_text(encoding="utf-8"))
        return proc, result


def _base_input() -> dict[str, Any]:
    return {
        "decision": "test",
        "criteria_confirmed": True,
        "current_platform": "chatgpt",
        "major_platforms": ["chatgpt"],
        "score_scale": "0-100",
        "criteria": [
            {
                "id": "fit",
                "name": "Fit",
                "weight": 1,
                "metric": "fit metric",
                "data_source": "source",
                "scoring_rule": "0-100",
            },
            {
                "id": "risk",
                "name": "Risk",
                "weight": 1,
                "metric": "risk metric",
                "data_source": "source",
                "scoring_rule": "0-100",
            },
        ],
        "alternatives": [],
    }


class GuardrailScoreTests(unittest.TestCase):
    def test_missing_scores_are_excluded_not_zeroed(self) -> None:
        data = _base_input()
        data["alternatives"] = [
            {
                "id": "a",
                "name": "A",
                "effort": "S",
                "risk": "Low",
                "feasible": True,
                "justification": "A has missing evidence on risk",
                "scores": {"chatgpt": {"fit": 100, "risk": None}},
            },
            {
                "id": "b",
                "name": "B",
                "effort": "M",
                "risk": "Med",
                "feasible": True,
                "justification": "B has complete evidence",
                "scores": {"chatgpt": {"fit": 80, "risk": 80}},
            },
        ]

        proc, result = _run(data)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        assert result is not None

        ranked = result["ranked_alternatives"]
        self.assertEqual(ranked[0]["id"], "a")
        self.assertAlmostEqual(ranked[0]["current_platform_score"], 100.0, places=2)
        self.assertAlmostEqual(ranked[0]["coverage"], 0.5, places=3)

    def test_single_option_requires_discovery_by_default(self) -> None:
        data = _base_input()
        data["alternatives"] = [
            {
                "id": "a",
                "name": "A",
                "effort": "S",
                "risk": "Low",
                "feasible": True,
                "justification": "single option",
                "scores": {"chatgpt": {"fit": 99, "risk": 99}},
            }
        ]

        proc, result = _run(data)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIsNone(result)

        proc, result = _run(data, ["--allow-single-option"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        assert result is not None
        self.assertNotEqual(result["recommendation"]["action"], "select")

    def test_tie_break_uses_effort_then_risk(self) -> None:
        data = _base_input()
        data["alternatives"] = [
            {
                "id": "slow",
                "name": "Slow",
                "effort": "L",
                "risk": "High",
                "feasible": True,
                "justification": "same scores but higher effort and risk",
                "scores": {"chatgpt": {"fit": 90, "risk": 90}},
            },
            {
                "id": "fast",
                "name": "Fast",
                "effort": "S",
                "risk": "Low",
                "feasible": True,
                "justification": "same scores but lower effort and risk",
                "scores": {"chatgpt": {"fit": 90, "risk": 90}},
            },
        ]

        proc, result = _run(data)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        assert result is not None
        self.assertEqual(result["ranked_alternatives"][0]["id"], "fast")

    def test_select_is_blocked_when_coverage_below_gate(self) -> None:
        data = _base_input()
        data["recommendation_rules"] = {"select_margin": 1.0, "min_coverage": 0.9}
        data["alternatives"] = [
            {
                "id": "a",
                "name": "A",
                "effort": "S",
                "risk": "Low",
                "feasible": True,
                "justification": "high score but low coverage",
                "scores": {"chatgpt": {"fit": 100, "risk": None}},
            },
            {
                "id": "b",
                "name": "B",
                "effort": "M",
                "risk": "Med",
                "feasible": True,
                "justification": "lower score but complete coverage",
                "scores": {"chatgpt": {"fit": 80, "risk": 80}},
            },
        ]

        proc, result = _run(data)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        assert result is not None
        self.assertNotEqual(result["recommendation"]["action"], "select")


if __name__ == "__main__":
    unittest.main()
