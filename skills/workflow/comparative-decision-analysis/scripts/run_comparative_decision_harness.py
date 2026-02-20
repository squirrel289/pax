#!/usr/bin/env python3
"""Deterministic harness wrapper for comparative decision scoring."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run comparative decision scoring with reproducible artifacts."
    )
    parser.add_argument("--input", required=True, help="Path to analysis input JSON.")
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory for generated report/result/manifest artifacts.",
    )
    parser.add_argument(
        "--run-id",
        help="Stable run id to use for output file names. Defaults to input hash prefix.",
    )
    parser.add_argument(
        "--schema",
        default=str(
            Path(__file__).resolve().parent.parent / "references" / "input-schema.json"
        ),
        help="Path to machine-readable input schema (recorded for traceability).",
    )
    parser.add_argument(
        "--allow-unconfirmed",
        action="store_true",
        help="Pass through simulation override to scorer.",
    )
    parser.add_argument(
        "--allow-single-option",
        action="store_true",
        help="Pass through simulation override to scorer.",
    )
    parser.add_argument(
        "--allow-nonisolated-evaluations",
        action="store_true",
        help="Pass through simulation override to scorer.",
    )
    return parser.parse_args()


def _build_score_cmd(
    *,
    score_script: Path,
    input_path: Path,
    report_path: Path,
    result_path: Path,
    args: argparse.Namespace,
) -> list[str]:
    cmd = [
        sys.executable,
        str(score_script),
        "--input",
        str(input_path),
        "--output",
        str(report_path),
        "--json-output",
        str(result_path),
    ]
    if args.allow_unconfirmed:
        cmd.append("--allow-unconfirmed")
    if args.allow_single_option:
        cmd.append("--allow-single-option")
    if args.allow_nonisolated_evaluations:
        cmd.append("--allow-nonisolated-evaluations")
    return cmd


def main() -> int:
    args = parse_args()

    input_path = Path(args.input).resolve()
    if not input_path.exists():
        raise SystemExit(f"Input file not found: {input_path}")

    schema_path = Path(args.schema).resolve()
    if not schema_path.exists():
        raise SystemExit(f"Schema file not found: {schema_path}")

    input_sha = _sha256(input_path)
    schema_sha = _sha256(schema_path)
    run_id = args.run_id or f"run-{input_sha[:12]}"
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    report_path = output_dir / f"{run_id}.analysis-report.md"
    result_path = output_dir / f"{run_id}.analysis-result.json"
    manifest_path = output_dir / f"{run_id}.manifest.json"

    score_script = Path(__file__).with_name("score_with_guardrails.py").resolve()
    cmd = _build_score_cmd(
        score_script=score_script,
        input_path=input_path,
        report_path=report_path,
        result_path=result_path,
        args=args,
    )

    completed = subprocess.run(
        cmd,
        text=True,
        capture_output=True,
        check=False,
    )

    manifest: dict[str, Any] = {
        "run_id": run_id,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "input": {
            "path": str(input_path),
            "sha256": input_sha,
        },
        "schema": {
            "path": str(schema_path),
            "sha256": schema_sha,
        },
        "score_script": str(score_script),
        "command": cmd,
        "artifacts": {
            "report": str(report_path),
            "result_json": str(result_path),
        },
        "exit_code": completed.returncode,
        "stderr": completed.stderr.strip(),
    }

    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    if completed.returncode != 0:
        if completed.stderr:
            print(completed.stderr, file=sys.stderr)
        print(f"Manifest: {manifest_path}")
        return completed.returncode

    print(f"Report: {report_path}")
    print(f"Result JSON: {result_path}")
    print(f"Manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
