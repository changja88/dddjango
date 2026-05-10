#!/usr/bin/env python3
"""Validate that generated eval reports expose readable artifact views."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


V2_SCHEMA_VERSION = "eval-report-v2"
SCORE_TYPES = {"numeric", "pass_fail", "hard_gate", "narrative"}
SCORE_TYPE_SOURCES = {"explicit", "inferred"}
SOURCE_GRANULARITIES = {"case", "request", "answer_oracle", "hard_gate", "artifact_check"}
CHANGE_DIRECTIONS = {"improved", "regressed", "unchanged", "mixed", "not_comparable"}
VARIANT_KEYS = ("baseline", "with_dddjango")
REQUIRED_VARIANT_KEYS = {
    "score",
    "response_summary",
    "response",
    "evaluation_summary",
    "evaluation",
    "evidence",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument(
        "--require-code-artifacts",
        action="store_true",
        help="Require embedded code-backed changed-files and diff artifacts.",
    )
    return parser.parse_args()


def extract_report_data(report_html: str) -> dict[str, object]:
    match = re.search(r"const REPORT_DATA = (.*?);\n", report_html, re.S)
    if not match:
        raise AssertionError("REPORT_DATA block was not found")
    return json.loads(match.group(1))


def require_object(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise AssertionError(f"{label} must be an object")
    return value


def require_non_empty_text(value: object, label: str) -> str:
    if not isinstance(value, str):
        raise AssertionError(f"{label} must be text")
    text = value.strip()
    if not text:
        raise AssertionError(f"{label} must not be empty")
    return text


def require_non_empty_scalar_text(value: object, label: str) -> str:
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        raise AssertionError(f"{label} must be text or numeric")
    text = str(value).strip()
    if not text:
        raise AssertionError(f"{label} must not be empty")
    return text


def require_keys(value: dict[str, object], keys: set[str], label: str) -> None:
    missing = sorted(keys - set(value))
    if missing:
        raise AssertionError(f"{label} missing: {', '.join(missing)}")


def validate_variant(variant: object, label: str) -> None:
    item = require_object(variant, label)
    require_keys(item, REQUIRED_VARIANT_KEYS, label)
    require_non_empty_scalar_text(item.get("score"), f"{label}.score")
    require_non_empty_text(item.get("response_summary"), f"{label}.response_summary")
    require_non_empty_text(item.get("response"), f"{label}.response")
    require_non_empty_text(item.get("evaluation_summary"), f"{label}.evaluation_summary")
    require_non_empty_text(item.get("evaluation"), f"{label}.evaluation")
    evidence = item.get("evidence")
    if not isinstance(evidence, list):
        raise AssertionError(f"{label}.evidence must be a list")


def validate_evaluation_item(item: object, index: int) -> str:
    row = require_object(item, f"evaluation_items[{index}]")
    required = {
        "id",
        "title",
        "source_granularity",
        "test_content_ko",
        "score_type",
        "score_type_source",
        "baseline",
        "with_dddjango",
        "change",
    }
    require_keys(row, required, f"evaluation_items[{index}]")
    require_non_empty_text(row.get("id"), f"evaluation_items[{index}].id")
    require_non_empty_text(row.get("title"), f"evaluation_items[{index}].title")
    require_non_empty_text(row.get("test_content_ko"), f"evaluation_items[{index}].test_content_ko")

    source_granularity = require_non_empty_text(
        row.get("source_granularity"),
        f"evaluation_items[{index}].source_granularity",
    )
    if source_granularity not in SOURCE_GRANULARITIES:
        raise AssertionError(f"unsupported source_granularity: {source_granularity}")

    score_type = require_non_empty_text(row.get("score_type"), f"evaluation_items[{index}].score_type")
    if score_type not in SCORE_TYPES:
        raise AssertionError(f"unsupported score_type: {score_type}")

    score_type_source = require_non_empty_text(
        row.get("score_type_source"),
        f"evaluation_items[{index}].score_type_source",
    )
    if score_type_source not in SCORE_TYPE_SOURCES:
        raise AssertionError(f"unsupported score_type_source: {score_type_source}")

    change = require_object(row.get("change"), f"evaluation_items[{index}].change")
    direction = require_non_empty_text(change.get("direction"), f"evaluation_items[{index}].change.direction")
    if direction not in CHANGE_DIRECTIONS:
        raise AssertionError(f"unsupported change.direction: {direction}")

    for variant_key in VARIANT_KEYS:
        validate_variant(row.get(variant_key), f"evaluation_items[{index}].{variant_key}")
    return score_type


def validate_v2_contract(data: dict[str, object]) -> None:
    if data.get("schema_version") != V2_SCHEMA_VERSION:
        raise AssertionError(f"schema_version must be {V2_SCHEMA_VERSION}")

    summary = require_object(data.get("summary"), "summary")
    sections = summary.get("sections")
    if not isinstance(sections, list) or not sections:
        raise AssertionError("summary.sections must be a non-empty list")
    require_non_empty_text(summary.get("conclusion"), "summary.conclusion")
    risks = summary.get("risks")
    if not isinstance(risks, list):
        raise AssertionError("summary.risks must be a list")

    evaluation_items = data.get("evaluation_items")
    if not isinstance(evaluation_items, list) or not evaluation_items:
        raise AssertionError("evaluation_items must be a non-empty list")
    present_types = {validate_evaluation_item(item, index) for index, item in enumerate(evaluation_items)}

    section_types = set()
    for index, section in enumerate(sections):
        section_obj = require_object(section, f"summary.sections[{index}]")
        section_type = require_non_empty_text(section_obj.get("type"), f"summary.sections[{index}].type")
        if section_type not in SCORE_TYPES:
            raise AssertionError(f"unsupported summary section type: {section_type}")
        metrics = section_obj.get("metrics")
        if not isinstance(metrics, list) or not metrics:
            raise AssertionError(f"summary.sections[{index}].metrics must be a non-empty list")
        section_types.add(section_type)

    missing_sections = sorted(present_types - section_types)
    if missing_sections:
        raise AssertionError(f"missing summary section for score_type: {', '.join(missing_sections)}")


def evidence_link_targets(evidence: list[object]) -> set[str]:
    targets = set()
    link_fields = ("href", "path", "url", "artifact", "artifact_href", "artifact_path", "link")
    for entry in evidence:
        if isinstance(entry, str):
            targets.add(entry)
            continue
        if not isinstance(entry, dict):
            continue
        for field in link_fields:
            value = entry.get(field)
            if isinstance(value, str) and value.strip():
                targets.add(value)
    return {target.removeprefix("./") for target in targets}


def require_embedded_artifact(
    embedded: dict[str, object],
    targets: set[str],
    suffix: str,
    label: str,
) -> tuple[str, dict[str, object]]:
    for target in sorted(targets):
        artifact = embedded.get(target)
        if isinstance(artifact, dict) and target.endswith(suffix):
            return target, artifact
    raise AssertionError(f"{label} evidence must link to {suffix}")


def parse_changed_files_content(artifact: dict[str, object], label: str) -> dict[str, object]:
    content = artifact.get("content")
    if not isinstance(content, str) or not content.strip():
        raise AssertionError(f"{label} content must be a non-empty JSON object")
    try:
        payload = json.loads(content)
    except json.JSONDecodeError as error:
        raise AssertionError(f"{label} content must be valid JSON") from error
    if not isinstance(payload, dict) or not payload:
        raise AssertionError(f"{label} content must be a non-empty JSON object")
    return payload


def source_case_ids(item: dict[str, object]) -> set[str]:
    raw_ids = item.get("source_case_ids")
    if not isinstance(raw_ids, list):
        return set()
    return {case_id for case_id in raw_ids if isinstance(case_id, str) and case_id.strip()}


def validate_changed_files_artifact(
    artifact_path: str,
    artifact: dict[str, object],
    item: dict[str, object],
    variant_key: str,
    item_label: str,
) -> None:
    label = f"{item_label}.{variant_key} changed-files artifact"
    if artifact.get("kind") != "changed-files":
        raise AssertionError(f"{label} kind must be changed-files")

    payload = parse_changed_files_content(artifact, label)
    required_keys = {"caseId", "variant", "evidenceMode", "diffPath", "noCodeProduced", "files"}
    require_keys(payload, required_keys, label)

    evidence_mode = require_non_empty_text(payload.get("evidenceMode"), f"{label}.evidenceMode")
    if evidence_mode != "code-backed":
        raise AssertionError(f"{label}.evidenceMode must be code-backed")

    expected_variant = "with-dddjango" if variant_key == "with_dddjango" else variant_key
    path_parts = {part for part in artifact_path.split("/") if part}
    if expected_variant not in path_parts:
        raise AssertionError(f"{label} path must include {expected_variant}")
    artifact_variant = require_non_empty_text(payload.get("variant"), f"{label}.variant")
    if artifact_variant != expected_variant:
        raise AssertionError(f"{label}.variant must be {expected_variant}")

    case_id = require_non_empty_text(payload.get("caseId"), f"{label}.caseId")
    item_id = require_non_empty_text(item.get("id"), f"{item_label}.id")
    allowed_case_ids = source_case_ids(item)
    if re.fullmatch(r"case-\d+", item_id):
        allowed_case_ids.add(item_id)
    if allowed_case_ids and case_id not in allowed_case_ids:
        raise AssertionError(f"{label}.caseId must match item id or source_case_ids")

    files = payload.get("files")
    if not isinstance(files, list):
        raise AssertionError(f"{label}.files must be a list")
    no_code_produced = payload.get("noCodeProduced")
    if not isinstance(no_code_produced, bool):
        raise AssertionError(f"{label}.noCodeProduced must be a boolean")
    if not no_code_produced and not files:
        raise AssertionError(f"{label}.files must not be empty when code was produced")


def validate_diff_artifact(artifact: dict[str, object], label: str) -> None:
    if artifact.get("kind") != "diff":
        raise AssertionError(f"{label} kind must be diff")
    content = artifact.get("content")
    if not isinstance(content, str) or not content.strip():
        raise AssertionError(f"{label} content must not be empty")


def validate_required_code_artifacts(data: dict[str, object]) -> None:
    embedded = data.get("embeddedArtifacts")
    if not isinstance(embedded, dict) or not embedded:
        raise AssertionError("embeddedArtifacts must be a non-empty object")
    normalized_embedded = {str(key).removeprefix("./"): value for key, value in embedded.items()}

    evaluation_items = data.get("evaluation_items")
    if not isinstance(evaluation_items, list):
        raise AssertionError("evaluation_items must be a list")

    for item_index, raw_item in enumerate(evaluation_items):
        item_label = f"evaluation_items[{item_index}]"
        item = require_object(raw_item, item_label)
        for variant_key in VARIANT_KEYS:
            variant = require_object(item.get(variant_key), f"{item_label}.{variant_key}")
            evidence = variant.get("evidence")
            if not isinstance(evidence, list):
                raise AssertionError(f"{item_label}.{variant_key}.evidence must be a list")
            targets = evidence_link_targets(evidence)

            changed_files_path, changed_files_artifact = require_embedded_artifact(
                normalized_embedded,
                targets,
                "changed-files.json",
                f"{item_label}.{variant_key}",
            )
            validate_changed_files_artifact(
                changed_files_path,
                changed_files_artifact,
                item,
                variant_key,
                item_label,
            )

            _diff_path, diff_artifact = require_embedded_artifact(
                normalized_embedded,
                targets,
                "diff.patch",
                f"{item_label}.{variant_key}",
            )
            validate_diff_artifact(diff_artifact, f"{item_label}.{variant_key} diff artifact")


def validate_v2_template(html: str) -> None:
    required_tokens = [
        'id="report-summary"',
        'id="evaluation-filters"',
        'id="evaluation-items-table"',
        'id="comparison-modal"',
        "renderReportSummary",
        "renderEvaluationItems",
        "openComparisonModal",
        "closeComparisonModal",
        "상세 보기",
        "Baseline",
        "With dddjango",
    ]
    missing_tokens = [token for token in required_tokens if token not in html]
    if missing_tokens:
        raise AssertionError(f"missing v2 template tokens: {', '.join(missing_tokens)}")


def main() -> int:
    args = parse_args()
    html = args.report.read_text(encoding="utf-8")
    data = extract_report_data(html)

    validate_v2_contract(data)
    if args.require_code_artifacts:
        validate_required_code_artifacts(data)
    validate_v2_template(html)

    embedded = data.get("embeddedArtifacts", {})
    embedded_count = len(embedded) if isinstance(embedded, dict) else 0
    print(
        f"readability validation passed: {len(data['evaluation_items'])} evaluation items, "
        f"{embedded_count} embedded artifacts"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
