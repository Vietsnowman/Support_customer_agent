from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
DATASET = ROOT / "evaluation" / "datasets" / "behavior_cases.jsonl"
SCHEMA = ROOT / "evaluation" / "schemas" / "behavior-case.schema.json"
SPEC = ROOT / "config" / "agent-spec.json"
COVERAGE = ROOT / "evaluation" / "reports" / "behavior_cases_coverage.json"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_cases(path: Path):
    cases = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            cases.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise AssertionError(f"Invalid JSON at line {line_number}: {exc}") from exc
    return cases


def validate():
    spec = load_json(SPEC)
    schema = load_json(SCHEMA)
    cases = load_cases(DATASET)
    validator = Draft202012Validator(schema)
    errors = []

    ids = [case["case_id"] for case in cases]
    duplicates = [case_id for case_id, count in Counter(ids).items() if count > 1]
    if duplicates:
        errors.append(f"Duplicate case IDs: {duplicates}")

    all_tools = set(spec["tools"])
    global_tools = set(spec["global_control_tools"])

    for case in cases:
        case_id = case["case_id"]
        for err in validator.iter_errors(case):
            path = ".".join(str(x) for x in err.absolute_path)
            errors.append(f"{case_id}: schema error at {path}: {err.message}")

        expected = case["expected"]
        active = expected["active_intent"]
        selected_tool = expected["selected_tool"]
        human = expected["human_handling_status"]

        if selected_tool:
            if selected_tool not in all_tools:
                errors.append(f"{case_id}: unknown tool {selected_tool}")
            elif selected_tool in global_tools:
                if human != "ready_now":
                    errors.append(
                        f"{case_id}: handoff tool requires human_handling_status=ready_now"
                    )
            elif selected_tool not in spec["business_tool_allowlist"][active]:
                errors.append(
                    f"{case_id}: tool {selected_tool} is not allowed for active intent {active}"
                )

        if expected["safety_status"] == "blocked":
            if expected["current_route"] != "safety_block":
                errors.append(f"{case_id}: blocked safety status must use safety_block")
            if selected_tool is not None:
                errors.append(f"{case_id}: blocked case must not select a tool")

        if human == "ready_now":
            if expected["current_route"] != "human_handoff":
                errors.append(f"{case_id}: ready_now must route to human_handoff")
            if selected_tool != "request_human_handoff":
                errors.append(f"{case_id}: ready_now must select request_human_handoff")

        if human == "created" and expected["workflow_status"] != "handoff_created":
            errors.append(f"{case_id}: created human status must have handoff_created workflow")

        if expected["secondary_intents"]:
            if not expected["execution_plan"]:
                errors.append(f"{case_id}: multi-intent case requires execution_plan")
            if expected["relation_type"] is None:
                errors.append(f"{case_id}: multi-intent case requires relation_type")

        action = expected["next_action"]
        if "_and_" in action or "_or_" in action or "_then_" in action:
            errors.append(f"{case_id}: next_action must be atomic: {action}")

        if expected["reason_code"] and expected["reason_code"] not in spec["reason_codes"]:
            errors.append(f"{case_id}: unknown reason code {expected['reason_code']}")

        for forbidden in case["forbidden_actions"]:
            if forbidden == selected_tool:
                errors.append(f"{case_id}: selected tool is also forbidden: {forbidden}")

    expected_coverage = {
        "schema_version": "2.0",
        "total_cases": len(cases),
        "by_split": dict(Counter(c["split"] for c in cases)),
        "by_category": dict(Counter(c["category"] for c in cases)),
        "by_primary_intent": dict(Counter(c["expected"]["primary_intent"] for c in cases)),
        "by_route": dict(Counter(c["expected"]["current_route"] for c in cases)),
        "by_human_handling_status": dict(Counter(c["expected"]["human_handling_status"] for c in cases)),
        "by_safety_status": dict(Counter(c["expected"]["safety_status"] for c in cases)),
        "reason_code_count": len({c["expected"]["reason_code"] for c in cases if c["expected"]["reason_code"]}),
        "reason_codes_used": sorted({c["expected"]["reason_code"] for c in cases if c["expected"]["reason_code"]}),
        "multi_intent_cases": sum(bool(c["expected"]["secondary_intents"]) for c in cases),
    }
    actual_coverage = load_json(COVERAGE)
    if expected_coverage != actual_coverage:
        errors.append("Coverage report does not match behavior_cases.jsonl")

    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Validation passed: {len(cases)} behavior cases")
    print(f"Smoke cases: {sum(c['split'] == 'smoke' for c in cases)}")
    print(f"Distinct reason codes used: {expected_coverage['reason_code_count']}")
    return 0


if __name__ == "__main__":
    sys.exit(validate())
