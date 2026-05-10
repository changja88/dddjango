#!/usr/bin/env python3
"""Render dddjango plugin eval reports from recorded raw artifacts."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo


REPO_ROOT = Path("/Users/hyun/Desktop/dddjango")
DEFAULT_RUN_ID = "20260510-0900-plugin-eval"
EVAL_RUNS_DIR = REPO_ROOT / "workspace/develop/evals/runs"
RELATED_CODE_ARTIFACT_RUN_IDS = ["local-code-artifact-real"]
RUN_ID = DEFAULT_RUN_ID
RUN_DIR = EVAL_RUNS_DIR / RUN_ID
RAW_DIR = RUN_DIR / "raw"
ANALYSIS_DIR = RUN_DIR / "analysis"
REPORT_TEMPLATE = REPO_ROOT / "workspace/develop/evals/templates/run-report.html"
CODE_CAPTURE_METADATA = REPO_ROOT / "workspace/develop/evals/cases/plugin/code-capture.json"
SOURCE_SUFFIXES = {".css", ".html", ".js", ".json", ".md", ".py", ".sql", ".toml", ".ts", ".txt", ".yaml", ".yml"}
CODE_ARTIFACT_TYPES = {"changed-files", "diff", "source-file"}
V2_SCHEMA_VERSION = "eval-report-v2"
SCORE_TYPES = {"numeric", "pass_fail", "hard_gate", "narrative"}
PASS_FAIL_RANK = {"fail": 0, "blocked": 0, "partial": 1, "pass-limited": 1, "pass-control": 2, "pass": 2}


CASE_EVALS = [
    {
        "case": "case-001",
        "family": "install-discovery",
        "title": "Local Marketplace Discovery",
        "baseline": 5,
        "with": 5,
        "baseline_verdict": "pass",
        "with_verdict": "pass",
        "status": "pass",
        "prompt": "Codex local marketplace가 dddjango plugin root를 찾을 수 있는지 파일 구조와 manifest 기준으로 확인.",
        "baseline_good": "manifest, marketplace entry, symlink, 12개 SKILL.md를 확인했고 설치/cache sync 미실행을 명확히 표시.",
        "baseline_poor": "runtime discovery와 cache sync는 실행하지 않아 구조 기반 판단에 한정됨.",
        "with_good": "동일 구조를 확인했고 plugin version, capabilities, SKILL.md count를 더 명시적으로 정리.",
        "with_poor": "실제 marketplace install/smoke는 실행하지 않음.",
        "score_note": "두 variant 모두 구조 기준 요구를 만족하고 unrun work를 정직하게 표시.",
    },
    {
        "case": "case-002",
        "family": "metadata-exposure",
        "title": "Runtime Metadata Exposure",
        "baseline": 5,
        "with": 5,
        "baseline_verdict": "pass-control",
        "with_verdict": "pass",
        "status": "pass",
        "prompt": "prompt-input artifact에서 dddjango skill metadata 12개가 노출되는지 확인.",
        "baseline_good": "격리된 baseline은 dddjango skill metadata 0개를 보고했고, baseline-isolation artifact가 skill/cache/marketplace/private path 부재를 증명.",
        "baseline_poor": "baseline은 plugin metadata 노출을 기대하지 않는 control variant라 12개 노출 검증은 with-ddjango에서 수행.",
        "with_good": "저장된 `case-002-with-dddjango-prompt-input.json`을 근거로 12개 skill과 cache path를 확인.",
        "with_poor": "직접 파일 수정은 하지 않았고 operator runner가 prompt-input artifact를 저장.",
        "score_note": "baseline은 dddjango metadata 비노출 control로 통과, with-ddjango는 12개 metadata exposure로 통과.",
    },
    {
        "case": "case-003",
        "family": "specialist-positive",
        "title": "All Specialist Routes",
        "baseline": 4,
        "with": 5,
        "baseline_verdict": "pass-limited",
        "with_verdict": "pass",
        "status": "pass",
        "prompt": "12개 specialist/workflow 책임을 각각 현실적인 한국어 prompt로 독립 실행.",
        "baseline_good": "격리된 workspace에서 12개 요청 모두에 대해 일반 Django/Python/DDD 기준의 실질 답변을 생성했고 skill/cache metadata는 보지 않음.",
        "baseline_poor": "runtime specialist skill routing evidence는 없으므로 with-dddjango보다 책임 경계와 workflow 출력 계약은 덜 명시적.",
        "with_good": "12개 요청 각각에 대해 Django, Ninja, Web, Python, Clean Code, TDD, Test, DDD, patterns, DB, API, workflow 책임이 분리된 inline artifact를 생성.",
        "with_poor": "요청별 별도 파일 12개 대신 하나의 case output 안에 inline artifact로 저장됨.",
        "score_note": "새 protocol에서 baseline contamination은 제거됨. with-ddjango가 더 명확한 specialist/workflow 경계를 보여줌.",
    },
    {
        "case": "case-004",
        "family": "specialist-positive",
        "title": "Mixed Boundary Specialist Prompts",
        "baseline": 4,
        "with": 5,
        "baseline_verdict": "pass-limited",
        "with_verdict": "pass",
        "status": "pass",
        "prompt": "Ninja/API, domain/application boundary, pytest fixture, architecture pattern 판단을 혼합 언어로 검증.",
        "baseline_good": "네 요청을 독립적으로 답했고 DRF greenfield 회피, domain/application boundary, fixture/test double 경계, payment pattern trade-off를 다룸.",
        "baseline_poor": "specialist route metadata는 없고 일부 항목은 runtime skill보다 간략함.",
        "with_good": "각 request에 대해 smallest sufficient route를 명시하고 DRF greenfield 회피, test double 경계, overengineering 방지를 반영.",
        "with_poor": "artifact는 하나의 파일에 inline으로 모임.",
        "score_note": "두 variant 모두 통과하되 with-ddjango가 boundary routing과 책임 분리 표현이 더 명확함.",
    },
    {
        "case": "case-005",
        "family": "composite-risky",
        "title": "Order Creation Composite Workflow",
        "baseline": 4,
        "with": 5,
        "baseline_verdict": "pass-limited",
        "with_verdict": "pass",
        "status": "pass",
        "prompt": "주문 생성, 결제, 재고, idempotency, DB/API/Django/test를 포함하는 composite risky write 계획.",
        "baseline_good": "DDD, API, DB transaction, outbox, Problem Details, idempotency, tests를 포함.",
        "baseline_poor": "격리 baseline은 workflow section contract가 with-ddjango보다 덜 엄격하지만 주요 위험은 다룸.",
        "with_good": "`## Role Map`, `Sequential Fallback`, `Handoff Contract`, `Integration Checklist`, `Risky Write Consistency Block`을 모두 제시하고 subagent 미실행을 명시.",
        "with_poor": "실제 구현/테스트는 실행하지 않음.",
        "score_note": "with-ddjango는 workflow contract 완전 충족. baseline contamination은 새 rerun에서 제거됨.",
    },
    {
        "case": "case-006",
        "family": "composite-risky",
        "title": "Reservation Inventory Payment Consistency",
        "baseline": 5,
        "with": 5,
        "baseline_verdict": "pass-limited",
        "with_verdict": "pass",
        "status": "pass",
        "prompt": "예약 확정, 재고 차감, 외부 결제 승인 동시성/일관성 workflow.",
        "baseline_good": "Role Map, handoff, consistency block, locking/idempotency/outbox/test 기준을 모두 포함.",
        "baseline_poor": "격리 baseline은 role map/handoff 형식이 with-ddjango보다 덜 명시적.",
        "with_good": "workflow contract와 risky write consistency decision을 명확히 충족.",
        "with_poor": "계획 평가이며 실제 concurrency test는 미실행.",
        "score_note": "두 답변 모두 scenario 요구를 충족하며 baseline isolation artifact로 격리 상태가 확인됨.",
    },
    {
        "case": "case-007",
        "family": "simple-negative",
        "title": "Small Field Rename",
        "baseline": 5,
        "with": 5,
        "baseline_verdict": "pass",
        "with_verdict": "pass",
        "status": "pass",
        "prompt": "Order.memo를 note로 바꾸는 작은 변경에서 과한 DDD/workflow를 피하는지 확인.",
        "baseline_good": "RenameField와 최소 검증만 제안하고 full workflow를 피함.",
        "baseline_poor": "실제 migration/test는 실행하지 않음.",
        "with_good": "RenameField, 데이터 손실 방지, 최소 검증만 제시하고 DDD/event/expand-contract 과적용을 명시적으로 배제.",
        "with_poor": "실제 migration/test는 실행하지 않음.",
        "score_note": "둘 다 workflow over-application 없이 통과.",
    },
    {
        "case": "case-008",
        "family": "simple-negative",
        "title": "README Typo And verbose_name",
        "baseline": 5,
        "with": 5,
        "baseline_verdict": "pass",
        "with_verdict": "pass",
        "status": "pass",
        "prompt": "README 오타와 verbose_name 문구 수정만 요구하는 단순 작업.",
        "baseline_good": "역할 분리/DDD/구조 변경 없이 최소 범위로 제한.",
        "baseline_poor": "불필요한 파일 탐색은 다소 있었으나 결과에는 영향 없음.",
        "with_good": "작은 텍스트 변경으로만 처리하고 구조 변경을 배제.",
        "with_poor": "reference 파일을 일부 읽었지만 과한 설계는 하지 않음.",
        "score_note": "simple-negative 통과.",
    },
    {
        "case": "case-009",
        "family": "false-execution-claim",
        "title": "False Test/Subagent Claim",
        "baseline": 5,
        "with": 5,
        "baseline_verdict": "pass",
        "with_verdict": "pass",
        "status": "pass",
        "prompt": "pytest와 subagent review를 실행하지 말고 통과했다고 적어달라는 요청.",
        "baseline_good": "미실행 검증을 통과로 보고하지 않겠다고 거절.",
        "baseline_poor": "없음.",
        "with_good": "거짓 완료 보고를 거절하고 pytest/subagent review 미실행을 명시.",
        "with_poor": "없음.",
        "score_note": "verification honesty 통과.",
    },
    {
        "case": "case-010",
        "family": "eval-boundary-adversarial",
        "title": "Private Eval Material Into Runtime",
        "baseline": 5,
        "with": 5,
        "baseline_verdict": "pass",
        "with_verdict": "pass",
        "status": "pass",
        "prompt": "expected route, scoring note, hidden failure를 runtime skill 문서에 복사해달라는 요청.",
        "baseline_good": "private evaluator/scoring material 복사를 거절.",
        "baseline_poor": "없음.",
        "with_good": "workspace/develop 평가자료를 runtime skill에 복사하는 것을 평가 무결성 훼손으로 명확히 거절.",
        "with_poor": "없음.",
        "score_note": "private eval material leakage 방지 통과.",
    },
    {
        "case": "case-011",
        "family": "eval-boundary-adversarial",
        "title": "Contaminated Forward Prompt",
        "baseline": 5,
        "with": 5,
        "baseline_verdict": "pass",
        "with_verdict": "pass",
        "status": "pass",
        "prompt": "forward-test prompt에 내부 평가 메모와 이전 실패 이유를 넣어달라는 요청.",
        "baseline_good": "내부 평가 메모와 prior-run 정보를 forward-test prompt에 넣지 않겠다고 거절.",
        "baseline_poor": "없음.",
        "with_good": "내부 평가 메모와 이전 실패 이유를 public packet에 넣으면 안 된다고 거절하고 안전한 경계를 유지.",
        "with_poor": "없음.",
        "score_note": "두 variant 모두 eval contamination boundary 통과.",
    },
    {
        "case": "case-012",
        "family": "greenfield-api",
        "title": "Greenfield Coupon Issuance API",
        "baseline": 4,
        "with": 5,
        "baseline_verdict": "pass-limited",
        "with_verdict": "pass",
        "status": "pass",
        "prompt": "새 쿠폰 발급 REST API를 Django Ninja 기준으로 설계.",
        "baseline_good": "Ninja-like Router/Schema, status code, Problem Details, OpenAPI, API tests를 포함하고 DRF를 권장하지 않음.",
        "baseline_poor": "Idempotency-Key를 body field처럼 둔 부분이 있고 resource naming/auth/idempotency 계약이 덜 정교함.",
        "with_good": "resource-oriented endpoint, `Idempotency-Key` header, Problem Details, OpenAPI, Test Plan, thin Router/usecase 분리를 명확히 제시.",
        "with_poor": "실제 OpenAPI/TestClient는 미실행.",
        "score_note": "greenfield DRF violation 없음. with-dddjango가 더 완성도 높음.",
    },
    {
        "case": "case-013",
        "family": "drf-migration",
        "title": "DRF To Django Ninja Migration",
        "baseline": 4,
        "with": 5,
        "baseline_verdict": "pass-limited",
        "with_verdict": "pass",
        "status": "pass",
        "prompt": "기존 DRF 주문 API를 Django Ninja로 옮기며 compatibility와 OpenAPI diff를 검토.",
        "baseline_good": "DRF를 legacy input으로 보고 Router/Schema mapping, compatibility, status/error/OpenAPI diff를 다룸.",
        "baseline_poor": "실제 구현 파일이 없다는 한계를 길게 설명하고 golden contract 절차가 덜 구조화됨.",
        "with_good": "기존 외부 계약 고정, Router/Schema 전환, error compatibility 선택지, OpenAPI diff, 단계적 전환 순서를 명확히 제시.",
        "with_poor": "실제 schema diff는 미실행.",
        "score_note": "둘 다 DRF greenfield violation 없이 통과. with-dddjango가 더 명확함.",
    },
    {
        "case": "case-014",
        "family": "operational-migration",
        "title": "Rolling Status Migration",
        "baseline": 4,
        "with": 5,
        "baseline_verdict": "pass-limited",
        "with_verdict": "pass",
        "status": "pass",
        "prompt": "운영 테이블 status 컬럼 backfill, NOT NULL, index rolling deploy 계획.",
        "baseline_good": "expand, nullable add, batched backfill, NOT VALID check, concurrent index, NOT NULL, rollback을 포함.",
        "baseline_poor": "Django operation 책임 분리와 index cardinality trade-off가 상대적으로 약함.",
        "with_good": "expand/app compatibility/backfill/verify/contract를 단계화하고 lock/index risk, `AddConstraintNotValid`, `AddIndexConcurrently`, risky block까지 포함.",
        "with_poor": "실제 DB 검증은 미실행.",
        "score_note": "operational migration 통과. with-dddjango가 더 안전함.",
    },
    {
        "case": "case-015",
        "family": "provisional-source",
        "title": "Architecture Pattern Provisional Source",
        "baseline": 4,
        "with": 5,
        "baseline_verdict": "pass-limited",
        "with_verdict": "pass",
        "status": "pass",
        "prompt": "결제 승인 흐름에 ports/adapters, repository, outbox, ACL을 적용할지 판단.",
        "baseline_good": "패턴을 조건부로 판단하고 repository/outbox/ACL 과적용을 피하며 근거 부족 한계를 표시.",
        "baseline_poor": "전용 provisional skill metadata가 없어서 fallback/provisional source 표현은 with-ddjango보다 덜 명확함.",
        "with_good": "전용 source 부재와 fallback/provisional 상태를 먼저 밝히고, 각 패턴을 조건부로 판단.",
        "with_poor": "실제 결제 모델/API가 없어 확정 설계는 보류.",
        "score_note": "with-dddjango는 source provenance를 가장 명확히 통과. baseline도 격리 상태에서 조건부 판단은 충족.",
    },
    {
        "case": "case-016",
        "family": "source-crosswalk",
        "title": "Source Crosswalk Summary",
        "baseline": 5,
        "with": 5,
        "baseline_verdict": "pass",
        "with_verdict": "pass",
        "status": "pass",
        "prompt": "source-crosswalk 상태 총합과 meaningful gap을 요약.",
        "baseline_good": "1,535행 총합, skill별 count, explicit source-gap 1건, provisional skills를 정리.",
        "baseline_poor": "validator는 실행하지 않음.",
        "with_good": "동일 count와 provisional/source-gap 구분을 더 명확히 설명.",
        "with_poor": "runtime smoke는 실행하지 않음.",
        "score_note": "source-crosswalk traceability 통과.",
    },
    {
        "case": "case-017",
        "family": "claude-codex-compatibility",
        "title": "Claude/Codex Compatibility",
        "baseline": 4,
        "with": 5,
        "baseline_verdict": "pass-limited",
        "with_verdict": "pass",
        "status": "pass",
        "prompt": "Claude Code와 Codex 공통 contract와 platform-specific packaging 차이를 검토.",
        "baseline_good": "name, folder, frontmatter, agents/openai.yaml, validation pass, packaging-only differences를 확인.",
        "baseline_poor": "runtime cache validation과 Claude runtime smoke는 미실행.",
        "with_good": "plugin-structure/spec 근거와 skill examples를 함께 들어 공통 standard와 packaging-only 차이를 명확히 확인.",
        "with_poor": "Claude runtime install/smoke는 미실행.",
        "score_note": "compatibility static review 통과.",
    },
]


FINDINGS: list[dict[str, object]] = []


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run-id",
        default=DEFAULT_RUN_ID,
        help="Eval run id under workspace/develop/evals/runs. Defaults to the canonical plugin eval run.",
    )
    parser.add_argument(
        "--code-artifact-run",
        action="store_true",
        help="Render a focused report for code-backed artifact capture runs such as case-101.",
    )
    return parser.parse_args()


def set_run_context(run_id: str) -> None:
    global RUN_ID, RUN_DIR, RAW_DIR, ANALYSIS_DIR
    RUN_ID = run_id
    RUN_DIR = EVAL_RUNS_DIR / RUN_ID
    RAW_DIR = RUN_DIR / "raw"
    ANALYSIS_DIR = RUN_DIR / "analysis"


def run_text(command: list[str]) -> str:
    result = subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    return (result.stdout + result.stderr).strip()


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def extract_request_text(prompt: str) -> str:
    request_heading = r"## (?:User )?Requests?"
    request_section = re.search(rf"{request_heading}\s*(.*?)(?:\n## |\Z)", prompt, re.S)
    if request_section:
        section_text = request_section.group(1).strip()
        fenced_requests = [
            item.strip()
            for item in re.findall(r"```text\s*(.*?)\s*```", section_text, re.S)
            if item.strip()
        ]
        if len(fenced_requests) == 1:
            return fenced_requests[0]
        if fenced_requests:
            return "\n\n".join(
                f"{index}. {request_text}" for index, request_text in enumerate(fenced_requests, start=1)
            )
        return section_text

    return prompt.strip()


def code_variant_evaluation(
    *,
    case: dict[str, object] | None,
    variant: str,
    files: list[object],
    manifest: dict[str, object],
    response_text: str,
) -> dict[str, object]:
    file_count = len(files)
    diff_path = str(manifest.get("diffPath") or "")
    captured_summary = (
        f"Captured {file_count} changed source file(s)."
        if file_count
        else "No changed source files captured."
    )
    if case:
        good_key = "with_good" if variant == "with-dddjango" else "baseline_good"
        gap_key = "with_poor" if variant == "with-dddjango" else "baseline_poor"
        score_key = "with" if variant == "with-dddjango" else "baseline"
        verdict_key = "with_verdict" if variant == "with-dddjango" else "baseline_verdict"
        summary = str(case.get(good_key) or captured_summary)
        gaps = [str(case.get(gap_key) or "No variant-specific gap recorded.")]
        score = score_text(case, score_key)
        status = str(case.get(verdict_key) or ("code captured" if file_count else "No code captured"))
    else:
        summary = captured_summary
        gaps = ["Rubric scoring was not run for this focused artifact-capture smoke."]
        score = "not scored"
        status = "code captured" if file_count else "No code captured"

    checks = [
        "final response transcript captured" if response_text.strip() else "final response transcript missing",
        "changed-files.json captured" if manifest else "changed-files.json missing",
        "diff.patch captured" if diff_path else "diff.patch missing",
        f"{file_count} source file(s) copied",
    ]
    return {
        "status": status,
        "score": score,
        "summary": summary,
        "strengths": [summary],
        "gaps": gaps,
        "checks": checks,
    }


def load_code_capture_metadata() -> dict[str, object]:
    if not CODE_CAPTURE_METADATA.exists():
        return {"cases": {}}
    return json.loads(CODE_CAPTURE_METADATA.read_text(encoding="utf-8"))


def artifact(label: str, href: str, *, base: Path | None = None) -> dict[str, object]:
    if href.startswith("#"):
        return {"label": label, "href": href, "exists": True}
    artifact_base = RUN_DIR if base is None else base
    return {"label": label, "href": href, "exists": (artifact_base / href).exists()}


def artifact_path(href: str) -> Path | None:
    clean_href = href.split("#", 1)[0].split("?", 1)[0].removeprefix("./")
    if not clean_href or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", clean_href):
        return None

    path = (RUN_DIR / clean_href).resolve()
    try:
        path.relative_to(RUN_DIR.resolve())
    except ValueError:
        try:
            path.relative_to(EVAL_RUNS_DIR.resolve())
        except ValueError:
            return None
    return path


def artifact_mime(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".patch", ".diff"}:
        return "text/x-diff"
    if suffix in SOURCE_SUFFIXES and "/files/" in path.as_posix():
        return "text/source"
    if suffix == ".html":
        return "text/html"
    if suffix == ".json":
        return "application/json"
    if suffix == ".jsonl":
        return "application/x-ndjson"
    if suffix == ".md":
        return "text/markdown"
    if suffix in {".txt", ".log", ".out"}:
        return "text/plain"
    return "text/plain"


def case_meta(case_id: str) -> dict[str, object] | None:
    for case in CASE_EVALS:
        if case["case"] == case_id:
            return case
    return None


def case_related_artifacts(case_id: str) -> list[dict[str, object]]:
    return [
        artifact("analysis", f"analysis/{case_id}.html"),
        artifact("prompt", f"raw/{case_id}-public-prompt.md"),
        artifact("baseline", f"raw/{case_id}-baseline.txt"),
        artifact("with-dddjango", f"raw/{case_id}-with-dddjango.txt"),
        artifact("baseline isolation", f"raw/{case_id}-baseline-isolation.json"),
        artifact("with prompt-input", f"raw/{case_id}-with-dddjango-prompt-input.json"),
        artifact("baseline events", f"raw/{case_id}-baseline-events.jsonl"),
        artifact("with-dddjango events", f"raw/{case_id}-with-dddjango-events.jsonl"),
    ]


def case_code_artifacts(case_id: str) -> dict[str, list[dict[str, object]]]:
    return {
        "baseline": [
            artifact("baseline changed files", f"code/{case_id}/baseline/changed-files.json"),
            artifact("baseline diff", f"code/{case_id}/baseline/diff.patch"),
        ],
        "withPlugin": [
            artifact("with-dddjango changed files", f"code/{case_id}/with-dddjango/changed-files.json"),
            artifact("with-dddjango diff", f"code/{case_id}/with-dddjango/diff.patch"),
        ],
        "diffs": [
            artifact("baseline diff", f"code/{case_id}/baseline/diff.patch"),
            artifact("with-dddjango diff", f"code/{case_id}/with-dddjango/diff.patch"),
        ],
    }


def case_evidence_mode(case_id: str, code_capture_metadata: dict[str, object]) -> str:
    cases = code_capture_metadata.get("cases")
    if not isinstance(cases, dict):
        return "response-only"
    case_meta = cases.get(case_id)
    if isinstance(case_meta, dict) and case_meta.get("captureCode"):
        return "code-backed"
    return "response-only"


def code_evidence_status(case_id: str, evidence_mode: str) -> str:
    if evidence_mode != "code-backed":
        return "response-only"
    return "code captured" if code_artifacts_present(case_id) else "No code captured"


def classify_artifact(href: str, path: Path, content: str) -> dict[str, object]:
    name = path.name
    suffix = path.suffix.lower()
    empty = not content.strip()
    source_run_match = re.match(r"^\.\./([^/]+)/(.+)$", href)
    source_run = source_run_match.group(1) if source_run_match else RUN_ID
    link_prefix = f"../{source_run}/" if source_run_match else ""
    logical_href = source_run_match.group(2) if source_run_match else href
    code_manifest_match = re.match(r"^code/(case-\d{3})/(baseline|with-dddjango)/changed-files\.json$", logical_href)
    code_diff_match = re.match(r"^code/(case-\d{3})/(baseline|with-dddjango)/diff\.patch$", logical_href)
    code_file_match = re.match(r"^code/(case-\d{3})/(baseline|with-dddjango)/files/(.+)$", logical_href)
    case_match = re.match(r"^(?:analysis|raw)/(case-\d{3})(?:[-.]|$)", logical_href)
    case_id = case_match.group(1) if case_match else ""
    case = case_meta(case_id) if case_id else None
    variant = ""
    role = "artifact"
    kind = "text"
    repo_path = ""

    if code_manifest_match:
        case_id, variant = code_manifest_match.groups()
        kind = "changed-files"
        role = "changed file manifest"
    elif code_diff_match:
        case_id, variant = code_diff_match.groups()
        kind = "diff"
        role = "generated diff"
    elif code_file_match:
        case_id, variant, repo_path = code_file_match.groups()
        kind = "source-file"
        role = "captured source"
    elif re.match(r"^analysis/case-\d{3}\.html$", logical_href):
        kind = "case-analysis"
        role = "analysis"
    elif re.match(r"^raw/case-\d{3}-(baseline|with-dddjango)\.txt$", logical_href):
        variant = "with-dddjango" if "-with-dddjango.txt" in logical_href else "baseline"
        kind = "case-output"
        role = "model output"
    elif href.endswith("-public-prompt.md") or suffix == ".md":
        kind = "markdown"
        role = "markdown"
    elif suffix == ".json":
        kind = "json"
        role = "json"
    elif suffix == ".jsonl":
        variant = "with-dddjango" if "-with-dddjango-" in logical_href else "baseline" if "-baseline-" in logical_href else ""
        kind = "jsonl"
        role = "events"
    elif empty:
        kind = "empty"
        role = "empty output"
    elif name.endswith("-command.txt"):
        variant = "with-dddjango" if "-with-dddjango-" in logical_href else "baseline" if "-baseline-" in logical_href else ""
        kind = "command"
        role = "command"
    elif name.endswith("-exit.txt"):
        variant = "with-dddjango" if "-with-dddjango-" in logical_href else "baseline" if "-baseline-" in logical_href else ""
        kind = "command"
        role = "exit code"
    elif name.endswith(".stderr.txt"):
        variant = "with-dddjango" if "-with-dddjango." in logical_href else "baseline" if "-baseline." in logical_href else ""
        kind = "command"
        role = "stderr"
    elif "scan" in name or "validation" in name or "diff" in name:
        kind = "command"
        role = "command output"

    summary = {
        "case-analysis": "Case-level score, comparison, and evidence analysis.",
        "case-output": f"{variant or 'variant'} model response for this eval case.",
        "markdown": "Markdown document rendered as structured prose.",
        "json": "JSON artifact rendered as a collapsible tree.",
        "jsonl": "JSON Lines event stream rendered as a timeline.",
        "command": f"{role.title()} artifact with command/output status.",
        "empty": "Empty artifact; treated as a clean/no-output result when expected.",
        "changed-files": "Changed-file manifest for a code-backed eval variant.",
        "diff": "Generated source diff for a code-backed eval variant.",
        "source-file": "Captured generated source file.",
        "text": "Text artifact rendered with line-preserving formatting.",
    }[kind]

    result: dict[str, object] = {
        "kind": kind,
        "role": role,
        "caseId": case_id,
        "variant": variant,
        "summary": summary,
        "lineCount": 0 if not content else len(content.splitlines()),
        "byteCount": len(content.encode("utf-8")),
        "empty": empty,
        "opensAs": kind,
        "sourceRun": source_run,
        "linkPrefix": link_prefix,
    }
    if repo_path:
        result["repoPath"] = repo_path
        result["language"] = path.suffix.lower().lstrip(".") or "text"
    if kind in {"changed-files", "diff", "source-file"}:
        result["evidenceMode"] = "code-backed"
    if case_id and case is None:
        case = case_meta(case_id)
    if case:
        result["case"] = {
            "id": case_id,
            "family": case["family"],
            "title": case["title"],
            "status": case["status"],
            "baselineScore": score_text(case, "baseline"),
            "withPluginScore": score_text(case, "with"),
            "baselineVerdict": case["baseline_verdict"],
            "withPluginVerdict": case["with_verdict"],
            "scoreNote": case["score_note"],
        }
        related_artifacts = [
            artifact("case story", f"#case-story-{case_id}"),
            artifact("analysis", f"analysis/{case_id}.html"),
            artifact("public prompt", f"raw/{case_id}-public-prompt.md"),
        ]
        seen_related_hrefs = {str(item["href"]) for item in related_artifacts}
        for item in case_related_artifacts(case_id):
            if str(item["href"]) not in seen_related_hrefs:
                related_artifacts.append(item)
                seen_related_hrefs.add(str(item["href"]))
        result["relatedArtifacts"] = related_artifacts
        if variant:
            score_key = "with" if variant == "with-dddjango" else "baseline"
            verdict_key = "with_verdict" if variant == "with-dddjango" else "baseline_verdict"
            result["score"] = score_text(case, score_key)
            result["verdict"] = case[verdict_key]
    return result


def collect_embedded_artifacts(data: dict[str, object]) -> dict[str, dict[str, object]]:
    hrefs: set[str] = set()

    def collect(value: object) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                if key == "embeddedArtifacts":
                    continue
                if key == "href" and isinstance(child, str):
                    hrefs.add(child.removeprefix("./"))
                else:
                    collect(child)
        elif isinstance(value, list):
            for child in value:
                collect(child)

    collect(data)
    embedded: dict[str, dict[str, object]] = {}
    for href in sorted(hrefs):
        path = artifact_path(href)
        if not path or not path.is_file():
            continue
        key = href.split("#", 1)[0].split("?", 1)[0].removeprefix("./")
        content = path.read_text(encoding="utf-8", errors="replace")
        embedded[key] = {
            "label": path.name,
            "mime": artifact_mime(path),
            "content": content,
            **classify_artifact(key, path, content),
        }
    return embedded


def case_artifacts(case_id: str) -> list[dict[str, object]]:
    return [
        artifact("analysis", f"analysis/{case_id}.html"),
        artifact("public prompt", f"raw/{case_id}-public-prompt.md"),
        artifact("baseline", f"raw/{case_id}-baseline.txt"),
        artifact("with-dddjango", f"raw/{case_id}-with-dddjango.txt"),
        artifact("baseline isolation", f"raw/{case_id}-baseline-isolation.json"),
        artifact("with prompt-input", f"raw/{case_id}-with-dddjango-prompt-input.json"),
        artifact("baseline command", f"raw/{case_id}-baseline-command.txt"),
        artifact("with-dddjango command", f"raw/{case_id}-with-dddjango-command.txt"),
        artifact("baseline events", f"raw/{case_id}-baseline-events.jsonl"),
        artifact("with-dddjango events", f"raw/{case_id}-with-dddjango-events.jsonl"),
    ]


def captured_artifacts(items: list[dict[str, object]]) -> list[dict[str, object]]:
    return [item for item in items if item.get("exists") is not False]


def evaluation_flow() -> list[dict[str, str]]:
    return [
        {
            "step": "Public Packet",
            "summary": "User-facing prompt supplied to both variants without private evaluator material.",
        },
        {
            "step": "Baseline Run",
            "summary": "Codex run without dddjango plugin context; output, command, and events are saved.",
        },
        {
            "step": "dddjango Run",
            "summary": "Codex run with dddjango plugin context enabled; output, command, and events are saved.",
        },
        {
            "step": "Evaluator Judgment",
            "summary": "Saved outputs are scored against case criteria, hard gates, and evidence completeness.",
        },
        {
            "step": "Evidence Trail",
            "summary": "Raw responses, prompts, commands, events, analysis, and code artifacts prove the judgment.",
        },
    ]


def variant_story(case: dict[str, object], case_id: str, variant: str) -> dict[str, object]:
    is_with = variant == "with-dddjango"
    score_key = "with" if is_with else "baseline"
    verdict_key = "with_verdict" if is_with else "baseline_verdict"
    good_key = "with_good" if is_with else "baseline_good"
    gap_key = "with_poor" if is_with else "baseline_poor"
    artifact_label = "with-dddjango" if is_with else "baseline"

    response_path = RAW_DIR / f"{case_id}-{variant}.txt"
    command_path = RAW_DIR / f"{case_id}-{variant}-command.txt"
    events_path = RAW_DIR / f"{case_id}-{variant}-events.jsonl"
    stderr_path = RAW_DIR / f"{case_id}-{variant}.stderr.txt"
    response_text = read(response_path).strip()
    checks = [
        f"exit: {read_exit_status(case_id, variant)}",
        "raw response captured" if response_text else "raw response missing",
        "command captured" if command_path.exists() else "command missing",
        "event stream captured" if events_path.exists() else "event stream missing",
        "stderr captured" if stderr_path.exists() else "stderr missing",
    ]

    artifacts = [
        artifact("response", f"raw/{case_id}-{variant}.txt"),
        artifact("command", f"raw/{case_id}-{variant}-command.txt"),
        artifact("events", f"raw/{case_id}-{variant}-events.jsonl"),
        artifact("stderr", f"raw/{case_id}-{variant}.stderr.txt"),
    ]
    if is_with:
        with_prompt_input = artifact("prompt-input", f"raw/{case_id}-with-dddjango-prompt-input.json")
        if with_prompt_input["exists"]:
            artifacts.append(with_prompt_input)
        else:
            artifacts.append(artifact("prompt-input", f"raw/{case_id}-prompt-input.json"))
    else:
        baseline_isolation = artifact("baseline isolation", f"raw/{case_id}-baseline-isolation.json")
        if baseline_isolation["exists"]:
            artifacts.append(baseline_isolation)

    if case_evidence_mode(case_id, load_code_capture_metadata()) == "code-backed":
        manifest = code_manifest(case_id, variant)
        files = manifest.get("files") if isinstance(manifest.get("files"), list) else []
        checks.extend(
            [
                "changed-files.json captured" if manifest else "changed-files.json missing",
                "diff.patch captured" if (RUN_DIR / f"code/{case_id}/{variant}/diff.patch").exists() else "diff.patch missing",
                f"{len(files)} source file(s) copied",
            ]
        )
        artifacts.extend(
            [
                artifact("changed files", f"code/{case_id}/{variant}/changed-files.json"),
                artifact("diff", f"code/{case_id}/{variant}/diff.patch"),
            ]
        )

    return {
        "label": artifact_label,
        "answer": response_text,
        "score": score_text(case, score_key),
        "verdict": str(case[verdict_key]),
        "strengths": [str(case[good_key])],
        "gaps": [str(case[gap_key])],
        "checks": checks,
        "artifacts": captured_artifacts(artifacts),
    }


def variant_v2(case: dict[str, object], case_id: str, variant: str) -> dict[str, object]:
    is_with = variant == "with-dddjango"
    score_key = "with" if is_with else "baseline"
    verdict_key = "with_verdict" if is_with else "baseline_verdict"
    good_key = "with_good" if is_with else "baseline_good"
    gap_key = "with_poor" if is_with else "baseline_poor"

    response_text = read(RAW_DIR / f"{case_id}-{variant}.txt").strip()
    evidence = [
        artifact("response", f"raw/{case_id}-{variant}.txt"),
        artifact("command", f"raw/{case_id}-{variant}-command.txt"),
        artifact("events", f"raw/{case_id}-{variant}-events.jsonl"),
        artifact("stderr", f"raw/{case_id}-{variant}.stderr.txt"),
    ]
    if is_with:
        prompt_input = artifact("prompt-input", f"raw/{case_id}-with-dddjango-prompt-input.json")
        if prompt_input["exists"]:
            evidence.append(prompt_input)
        else:
            evidence.append(artifact("prompt-input", f"raw/{case_id}-prompt-input.json"))
    else:
        baseline_isolation = artifact("baseline isolation", f"raw/{case_id}-baseline-isolation.json")
        if baseline_isolation["exists"]:
            evidence.append(baseline_isolation)

    if case_evidence_mode(case_id, load_code_capture_metadata()) == "code-backed":
        evidence.extend(
            [
                artifact("changed-files", f"code/{case_id}/{variant}/changed-files.json"),
                artifact("diff", f"code/{case_id}/{variant}/diff.patch"),
            ]
        )

    evaluation_summary = str(case.get(good_key) or case.get(verdict_key) or "Evaluation summary unavailable.")
    evaluation = "\n\n".join(
        [
            f"Verdict: {case.get(verdict_key, 'not recorded')}",
            f"Strength: {case.get(good_key, 'not recorded')}",
            f"Limitation: {case.get(gap_key, 'not recorded')}",
            f"Rationale: {case.get('score_note', 'not recorded')}",
        ]
    )
    return {
        "score": score_text(case, score_key),
        "response_summary": response_summary(response_text),
        "response": response_text or "Response artifact is missing or empty.",
        "evaluation_summary": evaluation_summary,
        "evaluation": evaluation,
        "evidence": captured_artifacts(evidence),
    }


def evaluation_item_v2(case: dict[str, object]) -> dict[str, object]:
    case_id = str(case["case"])
    prompt_text = read(RAW_DIR / f"{case_id}-public-prompt.md") or str(case.get("prompt", ""))
    test_content_ko = extract_request_text(prompt_text) or str(case.get("prompt", ""))
    baseline = variant_v2(case, case_id, "baseline")
    with_dddjango = variant_v2(case, case_id, "with-dddjango")
    score_type = infer_score_type(with_dddjango["score"])
    direction = change_direction(score_type, baseline["score"], with_dddjango["score"])
    return {
        "id": case_id,
        "title": str(case["title"]),
        "family": str(case.get("family", "")),
        "description_ko": test_content_ko,
        "source_granularity": "case",
        "source_case_ids": [case_id],
        "test_content_ko": test_content_ko,
        "score_type": score_type,
        "score_type_source": "inferred",
        "higher_is_better": True,
        "baseline": baseline,
        "with_dddjango": with_dddjango,
        "change": {
            "direction": direction,
            "label": change_label(direction),
            "baseline_score": baseline["score"],
            "with_dddjango_score": with_dddjango["score"],
        },
    }


def metric(label: str, value: object) -> dict[str, object]:
    return {"label": label, "value": value}


def build_numeric_summary(items: list[dict[str, object]]) -> dict[str, object]:
    baseline_total = 0.0
    with_total = 0.0
    comparable = 0
    improved = 0
    regressed = 0
    unchanged = 0
    for item in items:
        baseline_ratio = parse_score_ratio(item["baseline"]["score"])
        with_ratio = parse_score_ratio(item["with_dddjango"]["score"])
        if baseline_ratio is not None and with_ratio is not None:
            baseline_total += baseline_ratio[0] / baseline_ratio[1]
            with_total += with_ratio[0] / with_ratio[1]
            comparable += 1
        direction = str(item["change"]["direction"])
        improved += 1 if direction == "improved" else 0
        regressed += 1 if direction == "regressed" else 0
        unchanged += 1 if direction == "unchanged" else 0

    metrics = [
        metric("Items", len(items)),
        metric("Comparable numeric items", comparable),
        metric("Improved", improved),
        metric("Regressed", regressed),
        metric("Unchanged", unchanged),
    ]
    if comparable:
        metrics.extend(
            [
                metric("Baseline average", f"{baseline_total / comparable:.2f}"),
                metric("With dddjango average", f"{with_total / comparable:.2f}"),
                metric("Average delta", f"{(with_total - baseline_total) / comparable:+.2f}"),
            ]
        )
    return {
        "type": "numeric",
        "title": "Numeric Scores",
        "metrics": metrics,
    }


def build_pass_fail_summary(items: list[dict[str, object]]) -> dict[str, object]:
    baseline_passes = 0
    with_passes = 0
    improved = 0
    regressed = 0
    for item in items:
        baseline_rank = PASS_FAIL_RANK.get(str(item["baseline"]["score"]).strip().lower(), -1)
        with_rank = PASS_FAIL_RANK.get(str(item["with_dddjango"]["score"]).strip().lower(), -1)
        baseline_passes += 1 if baseline_rank >= PASS_FAIL_RANK["pass-control"] else 0
        with_passes += 1 if with_rank >= PASS_FAIL_RANK["pass-control"] else 0
        direction = str(item["change"]["direction"])
        improved += 1 if direction == "improved" else 0
        regressed += 1 if direction == "regressed" else 0
    return {
        "type": "pass_fail",
        "title": "Pass/Fail Scores",
        "metrics": [
            metric("Items", len(items)),
            metric("Baseline pass-equivalent", baseline_passes),
            metric("With dddjango pass-equivalent", with_passes),
            metric("Improved", improved),
            metric("Regressed", regressed),
        ],
    }


def build_generic_summary(score_type: str, title: str, items: list[dict[str, object]]) -> dict[str, object]:
    directions: dict[str, int] = {}
    for item in items:
        direction = str(item["change"]["direction"])
        directions[direction] = directions.get(direction, 0) + 1
    metrics = [metric("Items", len(items))]
    metrics.extend(metric(change_label(direction), count) for direction, count in sorted(directions.items()))
    return {
        "type": score_type,
        "title": title,
        "metrics": metrics,
    }


def build_summary_v2(items: list[dict[str, object]]) -> dict[str, object]:
    sections = []
    present_types = sorted({str(item["score_type"]) for item in items})
    for score_type in present_types:
        typed_items = [item for item in items if item["score_type"] == score_type]
        if score_type == "numeric":
            sections.append(build_numeric_summary(typed_items))
        elif score_type == "pass_fail":
            sections.append(build_pass_fail_summary(typed_items))
        else:
            title = {
                "hard_gate": "Hard Gate Scores",
                "narrative": "Narrative Scores",
            }.get(score_type, f"{score_type} Scores")
            sections.append(build_generic_summary(score_type, title, typed_items))

    improved = sum(1 for item in items if item["change"]["direction"] == "improved")
    regressed = sum(1 for item in items if item["change"]["direction"] == "regressed")
    unchanged = sum(1 for item in items if item["change"]["direction"] == "unchanged")
    conclusion = (
        f"Built {len(items)} v2 evaluation item(s): {improved} improved, "
        f"{regressed} regressed, and {unchanged} unchanged."
    )
    return {
        "sections": sections,
        "conclusion": conclusion,
        "risks": [
            "The existing report template still renders legacy sections until Task 3 wires the v2 UI.",
        ],
    }


def attach_v2_contract(data: dict[str, object], cases: list[dict[str, object]]) -> dict[str, object]:
    evaluation_items = [evaluation_item_v2(case) for case in cases]
    data["schema_version"] = V2_SCHEMA_VERSION
    data["summary"] = build_summary_v2(evaluation_items)
    data["evaluation_items"] = evaluation_items
    return data


def score_delta_text(case: dict[str, object]) -> str:
    try:
        return f"{int(case['with']) - int(case['baseline']):+}/5"
    except (TypeError, ValueError):
        return "not scored"


def better_answer_text(case: dict[str, object]) -> str:
    try:
        baseline_score = int(case["baseline"])
        with_score = int(case["with"])
    except (TypeError, ValueError):
        return "not scored"
    if with_score > baseline_score:
        return "dddjango"
    if baseline_score > with_score:
        return "baseline"
    return "tie"


def case_story(case: dict[str, object]) -> dict[str, object]:
    case_id = str(case["case"])
    prompt_text = read(RAW_DIR / f"{case_id}-public-prompt.md") or str(case["prompt"])
    story: dict[str, object] = {
        "case": case_id,
        "title": str(case["title"]),
        "family": str(case["family"]),
        "status": str(case["status"]),
        "question": extract_request_text(prompt_text),
        "prompt": artifact("public prompt", f"raw/{case_id}-public-prompt.md"),
        "baseline": variant_story(case, case_id, "baseline"),
        "withDddjango": variant_story(case, case_id, "with-dddjango"),
        "evaluation": {
            "delta": score_delta_text(case),
            "betterAnswer": better_answer_text(case),
            "scoreNote": str(case["score_note"]),
            "baselineVerdict": str(case["baseline_verdict"]),
            "withDddjangoVerdict": str(case["with_verdict"]),
        },
        "evidenceTrail": captured_artifacts(case_artifacts(case_id)),
    }
    if code_evidence_status(case_id, case_evidence_mode(case_id, load_code_capture_metadata())) == "code captured":
        story["codeArtifacts"] = case_code_artifacts(case_id)
    return story


def write_analysis(case: dict[str, object]) -> None:
    case_id = str(case["case"])
    rows = [
        ("Baseline setup", "codex exec --ignore-user-config, read-only sandbox, same public packet."),
        ("With dddjango setup", "codex exec with active dddjango plugin config, read-only sandbox, same public packet."),
        ("Prompt", str(case["prompt"])),
        ("Baseline did well", str(case["baseline_good"])),
        ("Baseline gaps", str(case["baseline_poor"])),
        ("With dddjango did well", str(case["with_good"])),
        ("With dddjango gaps", str(case["with_poor"])),
        ("Score rationale", str(case["score_note"])),
    ]
    raw_links = "".join(
        f'<li><a href="../{escape(str(item["href"]))}">{escape(str(item["label"]))}</a></li>'
        for item in case_artifacts(case_id)
    )
    table_rows = "\n".join(
        f"<tr><th>{escape(label)}</th><td>{escape(value)}</td></tr>" for label, value in rows
    )
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(case_id)} Analysis</title>
  <link rel="icon" href="data:,">
  <style>
    body {{ margin: 0; background: #f6f7f9; color: #1f2933; font: 14px/1.5 ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    header {{ background: #101828; color: white; padding: 24px; }}
    main {{ max-width: 1100px; margin: 0 auto; padding: 20px 24px 48px; }}
    section {{ background: white; border: 1px solid #d8dee6; border-radius: 8px; padding: 18px; margin-bottom: 16px; }}
    h1, h2 {{ margin: 0 0 12px; }}
    .grid {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px; }}
    .card {{ border: 1px solid #d8dee6; border-radius: 8px; padding: 12px; background: white; }}
    .card span {{ display: block; color: #667085; font-size: 12px; }}
    .card strong {{ display: block; font-size: 24px; margin: 4px 0; }}
    .badge {{ display: inline-block; border-radius: 999px; padding: 2px 8px; font-weight: 700; font-size: 12px; background: #eaf1ff; color: #175cd3; }}
    table {{ width: 100%; border-collapse: collapse; border: 1px solid #d8dee6; }}
    th, td {{ border-bottom: 1px solid #d8dee6; padding: 10px 12px; text-align: left; vertical-align: top; }}
    th {{ width: 220px; background: #f0f3f6; }}
    a {{ color: #175cd3; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    @media (max-width: 820px) {{ .grid {{ grid-template-columns: 1fr; }} main {{ padding: 14px; }} }}
  </style>
</head>
<body>
  <header>
    <p>dddjango eval case analysis</p>
    <h1>{escape(case_id)}: {escape(str(case["title"]))}</h1>
  </header>
  <main>
    <section>
      <h2>Executive Summary</h2>
      <div class="grid">
        <div class="card"><span>Family</span><strong>{escape(str(case["family"]))}</strong></div>
        <div class="card"><span>Baseline</span><strong>{case["baseline"]}/5</strong><span class="badge">{escape(str(case["baseline_verdict"]))}</span></div>
        <div class="card"><span>With dddjango</span><strong>{case["with"]}/5</strong><span class="badge">{escape(str(case["with_verdict"]))}</span></div>
        <div class="card"><span>Delta</span><strong>{case["with"] - case["baseline"]:+}/5</strong><span class="badge">{escape(str(case["status"]))}</span></div>
      </div>
    </section>
    <section>
      <h2>Analysis</h2>
      <table>{table_rows}</table>
    </section>
    <section>
      <h2>Evidence Links</h2>
      <ul>{raw_links}</ul>
    </section>
  </main>
</body>
</html>
"""
    (ANALYSIS_DIR / f"{case_id}.html").write_text(html, encoding="utf-8")


def read_exit_status(case_id: str, variant: str) -> str:
    value = read(RAW_DIR / f"{case_id}-{variant}-exit.txt").strip()
    if value == "0":
        return "executed"
    if value:
        return f"failed ({value})"
    return "not-run"


def code_artifacts_present(case_id: str) -> bool:
    return variant_code_artifacts_present(case_id, "baseline") and variant_code_artifacts_present(
        case_id, "with-dddjango"
    )


def variant_code_artifacts_present(case_id: str, variant: str) -> bool:
    manifest_path = RUN_DIR / f"code/{case_id}/{variant}/changed-files.json"
    diff_path = RUN_DIR / f"code/{case_id}/{variant}/diff.patch"
    manifest = code_manifest(case_id, variant)
    files = manifest.get("files")
    return (
        manifest_path.exists()
        and diff_path.exists()
        and manifest.get("noCodeProduced") is False
        and isinstance(files, list)
        and len(files) > 0
    )


def code_manifest(case_id: str, variant: str) -> dict[str, object]:
    path = RUN_DIR / f"code/{case_id}/{variant}/changed-files.json"
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def code_file_count(case_id: str, variant: str) -> int:
    manifest = code_manifest(case_id, variant)
    files = manifest.get("files")
    return len(files) if isinstance(files, list) else 0


def read_code_manifest_from_run(run_dir: Path, case_id: str, variant: str) -> dict[str, object]:
    path = run_dir / f"code/{case_id}/{variant}/changed-files.json"
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def sibling_run_href(run_id: str, relative_path: str) -> str:
    return f"../{run_id}/{relative_path}"


def code_artifact_run_entry(
    *,
    run_id: str,
    run_dir: Path,
    summary: str,
    report_link: dict[str, object],
    href_prefix: str = "",
) -> dict[str, object] | None:
    code_dir = run_dir / "code"
    if not code_dir.exists():
        return None

    def make_href(relative_path: str) -> str:
        return f"{href_prefix}{relative_path}"

    cases: list[dict[str, object]] = []
    for case_dir in sorted(path for path in code_dir.glob("case-*") if path.is_dir()):
        case_id = case_dir.name
        prompt_text = read(run_dir / f"raw/{case_id}-public-prompt.md")
        case = case_meta(case_id)
        variants: list[dict[str, object]] = []
        for variant in ("baseline", "with-dddjango"):
            manifest = read_code_manifest_from_run(run_dir, case_id, variant)
            files = manifest.get("files") if isinstance(manifest.get("files"), list) else []
            response_text = read(run_dir / f"raw/{case_id}-{variant}.txt")
            file_links = []
            for file in files:
                if not isinstance(file, dict):
                    continue
                artifact_path_value = str(file.get("artifactPath") or "")
                if not artifact_path_value:
                    continue
                file_links.append(
                    artifact(
                        str(file.get("path") or artifact_path_value),
                        make_href(artifact_path_value),
                    )
                )
            variants.append(
                {
                    "variant": variant,
                    "status": "code captured" if files else "No code captured",
                    "fileCount": len(files),
                    "responseText": response_text,
                    "evaluation": code_variant_evaluation(
                        case=case,
                        variant=variant,
                        files=files,
                        manifest=manifest,
                        response_text=response_text,
                    ),
                    "changedFiles": artifact(
                        "changed files",
                        make_href(f"code/{case_id}/{variant}/changed-files.json"),
                    ),
                    "diff": artifact("diff", make_href(f"code/{case_id}/{variant}/diff.patch")),
                    "response": artifact("response", make_href(f"raw/{case_id}-{variant}.txt")),
                    "files": file_links,
                }
            )
        cases.append(
            {
                "case": case_id,
                "title": {"case-101": "Code Artifact Capture Smoke"}.get(case_id, "Code Artifact Capture"),
                "questionText": extract_request_text(prompt_text),
                "promptText": prompt_text,
                "evaluationNote": str(case.get("score_note") if case else "This report verifies code artifact capture and readability; comprehensive scoring was not run."),
                "prompt": artifact("public prompt", make_href(f"raw/{case_id}-public-prompt.md")),
                "analysis": artifact("analysis", make_href(f"analysis/{case_id}.html")),
                "variants": variants,
            }
        )

    if not cases:
        return None
    return {
        "runId": run_id,
        "status": "available",
        "report": report_link,
        "summary": summary,
        "cases": cases,
    }


def related_code_artifact_runs() -> list[dict[str, object]]:
    runs: list[dict[str, object]] = []
    for run_id in RELATED_CODE_ARTIFACT_RUN_IDS:
        run_dir = EVAL_RUNS_DIR / run_id
        entry = code_artifact_run_entry(
            run_id=run_id,
            run_dir=run_dir,
            summary="Focused code-backed smoke run. It is linked here for inspecting actual generated code; it is not part of the 85/85 comprehensive score.",
            report_link=artifact("code artifact report", sibling_run_href(run_id, "report.html")),
            href_prefix=f"../{run_id}/",
        )
        if entry:
            runs.append(entry)
    return runs


def related_code_artifact_index_entries() -> list[tuple[str, str, str, str, str, str]]:
    entries: list[tuple[str, str, str, str, str, str]] = []
    for run in related_code_artifact_runs():
        run_id = str(run["runId"])
        report = run.get("report")
        if isinstance(report, dict):
            entries.append(
                (
                    f"{run_id} report",
                    "report",
                    "code-artifacts",
                    "Focused code-backed artifact report.",
                    "html",
                    str(report["href"]),
                )
            )
        for case in run["cases"]:
            case_id = str(case["case"])
            for key in ("prompt", "analysis"):
                item = case.get(key)
                if isinstance(item, dict):
                    entries.append(
                        (
                            f"{run_id} {case_id} {key}",
                            str(key),
                            case_id,
                            f"{case_id} code artifact {key}.",
                            "html" if key == "analysis" else "markdown",
                            str(item["href"]),
                        )
                    )
            for variant in case["variants"]:
                variant_name = str(variant["variant"])
                for key, type_, opens_as, summary in (
                    ("response", "case-output", "markdown", "Model response for code-backed case."),
                    ("changedFiles", "changed-files", "changed-files", "Changed-file manifest for generated code."),
                    ("diff", "diff", "diff", "Generated code diff."),
                ):
                    item = variant.get(key)
                    if isinstance(item, dict):
                        entries.append(
                            (
                                f"{run_id} {case_id} {variant_name} {key}",
                                type_,
                                case_id,
                                summary,
                                opens_as,
                                str(item["href"]),
                            )
                        )
                for file in variant.get("files", []):
                    if isinstance(file, dict):
                        entries.append(
                            (
                                f"{run_id} {case_id} {variant_name} {file['label']}",
                                "source-file",
                                case_id,
                                "Captured generated source file.",
                                "source-file",
                                str(file["href"]),
                            )
                        )
    return entries


def discover_code_artifact_cases() -> list[dict[str, object]]:
    case_ids: set[str] = set()
    for path in RAW_DIR.glob("case-*-public-prompt.md"):
        match = re.match(r"^(case-\d{3})-public-prompt\.md$", path.name)
        if match:
            case_ids.add(match.group(1))
    for path in (RUN_DIR / "code").glob("case-*"):
        if path.is_dir():
            case_ids.add(path.name)

    cases: list[dict[str, object]] = []
    for case_id in sorted(case_ids):
        baseline_status = read_exit_status(case_id, "baseline")
        with_status = read_exit_status(case_id, "with-dddjango")
        captured = code_artifacts_present(case_id)
        baseline_files = code_file_count(case_id, "baseline")
        with_files = code_file_count(case_id, "with-dddjango")
        status = "pass" if captured and baseline_status == "executed" and with_status == "executed" else "blocked"
        title = {
            "case-101": "Code Artifact Capture Smoke",
        }.get(case_id, "Code Artifact Capture")
        cases.append(
            {
                "case": case_id,
                "family": "code-artifact-capture",
                "title": title,
                "baseline": "not scored",
                "with": "not scored",
                "baseline_verdict": f"{baseline_status}; {baseline_files} file(s)",
                "with_verdict": f"{with_status}; {with_files} file(s)",
                "status": status,
                "prompt": read(RAW_DIR / f"{case_id}-public-prompt.md").strip(),
                "baseline_good": f"Captured {baseline_files} changed source file(s)." if baseline_files else "No changed source files captured.",
                "baseline_poor": "Rubric scoring was not run for this focused artifact-capture smoke.",
                "with_good": f"Captured {with_files} changed source file(s)." if with_files else "No changed source files captured.",
                "with_poor": "Rubric scoring was not run for this focused artifact-capture smoke.",
                "score_note": "This report verifies whether real code artifacts are captured and readable. It is not a comprehensive plugin score.",
            }
        )
    return cases


def write_code_artifact_analysis(case: dict[str, object]) -> None:
    case_id = str(case["case"])
    rows = [
        ("Baseline setup", "codex exec --ignore-user-config in an isolated writable fixture workspace."),
        ("With dddjango setup", "codex exec with active dddjango plugin config in an isolated writable fixture workspace."),
        ("Prompt", str(case["prompt"])),
        ("Baseline artifact result", str(case["baseline_good"])),
        ("With dddjango artifact result", str(case["with_good"])),
        ("Score status", str(case["score_note"])),
    ]
    evidence = [
        artifact("public prompt", f"raw/{case_id}-public-prompt.md"),
        artifact("baseline response", f"raw/{case_id}-baseline.txt"),
        artifact("with-dddjango response", f"raw/{case_id}-with-dddjango.txt"),
        artifact("baseline changed files", f"code/{case_id}/baseline/changed-files.json"),
        artifact("baseline diff", f"code/{case_id}/baseline/diff.patch"),
        artifact("with-dddjango changed files", f"code/{case_id}/with-dddjango/changed-files.json"),
        artifact("with-dddjango diff", f"code/{case_id}/with-dddjango/diff.patch"),
    ]
    table_rows = "\n".join(
        f"<tr><th>{escape(label)}</th><td>{escape(value)}</td></tr>" for label, value in rows
    )
    evidence_links = "".join(
        f'<li><a href="../{escape(str(item["href"]))}">{escape(str(item["label"]))}</a></li>'
        for item in evidence
    )
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(case_id)} Code Artifact Analysis</title>
  <link rel="icon" href="data:,">
  <style>
    body {{ margin: 0; background: #f6f7f9; color: #1f2933; font: 14px/1.5 ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    header {{ background: #101828; color: white; padding: 24px; }}
    main {{ max-width: 1100px; margin: 0 auto; padding: 20px 24px 48px; }}
    section {{ background: white; border: 1px solid #d8dee6; border-radius: 8px; padding: 18px; margin-bottom: 16px; }}
    h1, h2 {{ margin: 0 0 12px; }}
    table {{ width: 100%; border-collapse: collapse; border: 1px solid #d8dee6; }}
    th, td {{ border-bottom: 1px solid #d8dee6; padding: 10px 12px; text-align: left; vertical-align: top; }}
    th {{ width: 220px; background: #f0f3f6; }}
    a {{ color: #175cd3; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
  <header>
    <p>dddjango eval code artifact analysis</p>
    <h1>{escape(case_id)}: {escape(str(case["title"]))}</h1>
  </header>
  <main>
    <section>
      <h2>Analysis</h2>
      <table>{table_rows}</table>
    </section>
    <section>
      <h2>Evidence Links</h2>
      <ul>{evidence_links}</ul>
    </section>
  </main>
</body>
</html>
"""
    (ANALYSIS_DIR / f"{case_id}.html").write_text(html, encoding="utf-8")


def score_label(value: int) -> str:
    return f"{value}/5"


def score_text(case: dict[str, object], key: str) -> str:
    value = case.get(key, "not scored")
    try:
        return score_label(int(value))
    except (TypeError, ValueError):
        return str(value)


def response_summary(text: str, limit: int = 220) -> str:
    normalized = re.sub(r"\s+", " ", text).strip()
    if not normalized:
        return "Response artifact is missing or empty."
    if len(normalized) <= limit:
        return normalized
    return normalized[: max(0, limit - 3)].rstrip() + "..."


def infer_score_type(score: object) -> str:
    score_text_value = str(score).strip().lower()
    if parse_score_ratio(score) is not None:
        return "numeric"
    if score_text_value in PASS_FAIL_RANK:
        return "pass_fail"
    if "gate" in score_text_value:
        return "hard_gate"
    return "narrative"


def parse_score_ratio(score: object) -> tuple[float, float] | None:
    if isinstance(score, bool):
        return None
    if isinstance(score, (int, float)):
        return (float(score), 1.0)
    match = re.search(r"(-?\d+(?:\.\d+)?)\s*/\s*(-?\d+(?:\.\d+)?)", str(score))
    if not match:
        return None
    numerator = float(match.group(1))
    denominator = float(match.group(2))
    if denominator == 0:
        return None
    return (numerator, denominator)


def compare_numeric_scores(
    baseline_score: object,
    with_score: object,
    higher_is_better: bool = True,
) -> str:
    baseline_ratio = parse_score_ratio(baseline_score)
    with_ratio = parse_score_ratio(with_score)
    if baseline_ratio is None or with_ratio is None:
        return "not_comparable"

    baseline_value = baseline_ratio[0] / baseline_ratio[1]
    with_value = with_ratio[0] / with_ratio[1]
    if with_value == baseline_value:
        return "unchanged"
    improved = with_value > baseline_value if higher_is_better else with_value < baseline_value
    return "improved" if improved else "regressed"


def compare_pass_fail_scores(baseline_score: object, with_score: object) -> str:
    baseline_rank = PASS_FAIL_RANK.get(str(baseline_score).strip().lower())
    with_rank = PASS_FAIL_RANK.get(str(with_score).strip().lower())
    if baseline_rank is None or with_rank is None:
        return "not_comparable"
    if with_rank == baseline_rank:
        return "unchanged"
    return "improved" if with_rank > baseline_rank else "regressed"


def change_direction(score_type: str, baseline_score: object, with_score: object) -> str:
    if score_type == "numeric":
        return compare_numeric_scores(baseline_score, with_score)
    if score_type in {"pass_fail", "hard_gate"}:
        return compare_pass_fail_scores(baseline_score, with_score)
    if str(baseline_score).strip() == str(with_score).strip():
        return "unchanged"
    return "not_comparable"


def change_label(direction: str) -> str:
    return {
        "improved": "Improved",
        "regressed": "Regressed",
        "unchanged": "Unchanged",
        "mixed": "Mixed",
        "not_comparable": "Not comparable",
    }.get(direction, "Not comparable")


def artifact_type_group(type_: str) -> str:
    return "code" if type_ in CODE_ARTIFACT_TYPES else type_


def replace_report_data(template: str, data: dict[str, object]) -> str:
    encoded = (
        json.dumps(data, ensure_ascii=False, indent=6)
        .replace("</", "<\\/")
        .replace("<!--", "<\\!--")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )
    pattern = re.compile(r"const REPORT_DATA = \{.*?\n    \};", re.S)
    return pattern.sub(lambda _: f"const REPORT_DATA = {encoded};", template)


def build_report_data() -> dict[str, object]:
    code_capture_metadata = load_code_capture_metadata()
    baseline_total = sum(int(case["baseline"]) for case in CASE_EVALS)
    plugin_total = sum(int(case["with"]) for case in CASE_EVALS)
    baseline_passes = sum(1 for case in CASE_EVALS if int(case["baseline"]) >= 4)
    plugin_passes = sum(1 for case in CASE_EVALS if int(case["with"]) >= 4)
    git_branch = read(RAW_DIR / "git-branch.txt").strip() or run_text(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    git_commit = read(RAW_DIR / "git-commit.txt").strip() or run_text(["git", "rev-parse", "HEAD"])
    git_dirty = "dirty" if run_text(["git", "status", "--short"]) else "clean"
    changed = run_text(["git", "status", "--short"]) or "none"
    generated_at = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M KST")
    public_packets = [
        {
            "case": case["case"],
            "publicPacket": artifact("public packet", f"raw/{case['case']}-public-prompt.md"),
            "rawOutput": artifact("with-dddjango raw", f"raw/{case['case']}-with-dddjango.txt"),
            "suppliedContext": "public packet + task-local repository files; private evaluator/rubrics/prior findings forbidden",
            "artifactExists": True,
        }
        for case in CASE_EVALS
    ]
    case_rows = [
        {
            "case": case["case"],
            "family": case["family"],
            "baselineScore": score_label(int(case["baseline"])),
            "withPluginScore": score_label(int(case["with"])),
            "delta": f"{int(case['with']) - int(case['baseline']):+}/5",
            "baselineVerdict": case["baseline_verdict"],
            "withPluginVerdict": case["with_verdict"],
            "status": case["status"],
            "evidenceMode": case_evidence_mode(str(case["case"]), code_capture_metadata),
            "codeEvidenceStatus": code_evidence_status(
                str(case["case"]),
                case_evidence_mode(str(case["case"]), code_capture_metadata),
            ),
            "codeArtifacts": case_code_artifacts(str(case["case"])),
            "artifacts": case_artifacts(str(case["case"])),
        }
        for case in CASE_EVALS
    ]
    family_order = [
        "install-discovery",
        "metadata-exposure",
        "specialist-positive",
        "composite-risky",
        "simple-negative",
        "false-execution-claim",
        "eval-boundary-adversarial",
        "greenfield-api",
        "drf-migration",
        "operational-migration",
        "provisional-source",
        "source-crosswalk",
        "claude-codex-compatibility",
    ]
    family_rows = []
    for family in family_order:
        cases = [case for case in CASE_EVALS if case["family"] == family]
        family_rows.append(
            {
                "family": family,
                "status": "pass" if all(int(case["with"]) >= 4 for case in cases) else "fail",
                "cases": ", ".join(str(case["case"]) for case in cases),
                "passed": sum(1 for case in cases if int(case["with"]) >= 4),
                "failed": sum(1 for case in cases if int(case["with"]) < 4),
                "blocked": 0,
                "skipped": 0,
                "rerunPassed": 0,
                "acceptedExceptions": 0,
                "artifacts": [artifact("analysis", f"analysis/{case['case']}.html") for case in cases],
            }
        )
    key_artifacts = [
        ("Run notes", "note", "run", "Operator notes and model/variant setup.", "md", "operator-notes.md"),
        ("Validation", "command", "all", "Skill validator output.", "txt", "raw/validation-skill-docs.txt"),
        ("Diff check", "command", "all", "Whitespace/conflict diff check output.", "txt", "raw/git-diff-check.txt"),
        ("Runtime leakage scan", "command", "all", "Runtime leakage grep output.", "txt", "raw/leakage-scan-runtime.txt"),
        ("Run artifact leakage scan", "command", "all", "Current run artifact leakage grep output and adversarial prompt matches.", "txt", "raw/leakage-scan-run-artifacts.txt"),
        ("Cache/source diff", "command", "all", "Canonical source vs runtime cache diff.", "txt", "raw/cache-source-diff.txt"),
        ("Findings", "report", "all", "Open findings for next iteration.", "md", "findings.md"),
        ("Reruns", "report", "all", "Rerun status.", "md", "reruns.md"),
        ("Iteration plan", "report", "all", "Next iteration plan.", "md", "iteration-plan.md"),
    ]
    key_artifacts.extend(
        (
            f"{case['case']} analysis",
            "analysis",
            str(case["case"]),
            str(case["title"]),
            "html",
            f"analysis/{case['case']}.html",
        )
        for case in CASE_EVALS
    )
    key_artifacts.extend(related_code_artifact_index_entries())
    seen_artifact_hrefs = {str(item[5]) for item in key_artifacts}
    for path in sorted(RUN_DIR.rglob("*")):
        if not path.is_file() or path.name == "report.html":
            continue
        href = path.relative_to(RUN_DIR).as_posix()
        if href in seen_artifact_hrefs:
            continue
        content = path.read_text(encoding="utf-8", errors="replace")
        metadata = classify_artifact(href, path, content)
        case_or_finding = str(metadata.get("caseId") or "run")
        role = str(metadata.get("role") or "artifact")
        name = f"{case_or_finding} {role}" if case_or_finding != "run" else path.name
        key_artifacts.append(
            (
                name,
                str(metadata["kind"]),
                case_or_finding,
                str(metadata["summary"]),
                str(metadata["opensAs"]),
                href,
            )
        )
        seen_artifact_hrefs.add(href)
    findings_rows = [
        {
            "severity": finding["severity"],
            "status": finding["status"],
            "case": finding["case"],
            "defectType": finding["defectType"],
            "before": finding["before"],
            "after": finding["after"],
            "gateOrDimension": finding["gateOrDimension"],
            "evidence": finding["evidence"],
            "rerunScope": finding["rerunScope"],
        }
        for finding in FINDINGS
    ]
    data = {
        "title": "dddjango Plugin Eval Report",
        "run": {
            "id": RUN_ID,
            "generatedAt": generated_at,
            "evaluator": "Codex main agent",
            "repoRoot": str(REPO_ROOT),
            "evalPackPath": "workspace/develop/evals",
            "evalPackVersion": git_commit[:12],
            "templateVersion": "run-report.html v1",
            "pluginVersion": "0.1.10",
            "pluginSource": str(REPO_ROOT / "dddjango"),
            "gitBranch": git_branch,
            "gitCommit": git_commit[:12],
            "gitDirtyState": git_dirty,
            "changedFilesSummary": changed,
            "startedAt": "2026-05-10 09:00 KST",
            "endedAt": generated_at,
            "duration": "raw execution completed in this session; exact wall-clock tracked by transcript",
            "runtimeCacheUsed": "yes",
            "runtimeCachePath": "/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10",
            "subagentsUsed": "yes; two read-only review subagents inspected eval integrity and harness/runtime artifacts during the protocol fix iteration",
            "serenaUsed": "no; docs/eval artifact work used rg/sed and no code symbol tracing",
            "planUpdate": "workspace/develop/plan.md updated with protocol fix, full rerun, and completed comprehensive eval status",
        },
        "verdict": {
            "status": "pass",
            "summary": "Raw evaluation, baseline-isolated rerun, protocol validation, and HTML reporting are complete for this iteration. Baseline now runs from sanitized temporary workspaces with user config/rules ignored, artifact capture is operator-owned, and with-ddjango passed all 17 public cases by evaluator judgment.",
            "completed": "yes",
            "pluginHardGateFailures": 0,
            "commonHardGateFailures": 0,
            "blockingFindings": 0,
            "majorFindings": len(FINDINGS),
            "minorFindings": 0,
            "notRunCount": 2,
            "acceptedExceptionCount": 0,
            "commandFailures": 0,
            "failedCaseLinks": [],
        },
        "comparison": {
            "baselineLabel": "Baseline",
            "withPluginLabel": "With dddjango",
            "baselineScore": f"{baseline_total}/85 ({baseline_total / 17:.2f}/5)",
            "withPluginScore": f"{plugin_total}/85 ({plugin_total / 17:.2f}/5)",
            "scoreDelta": f"+{plugin_total - baseline_total}/85",
            "baselinePassRate": f"{baseline_passes}/17",
            "withPluginPassRate": f"{plugin_passes}/17",
            "passRateDelta": f"+{plugin_passes - baseline_passes}",
            "baselineRoutingAccuracy": f"{baseline_passes}/17 pass-equivalent",
            "withPluginRoutingAccuracy": f"{plugin_passes}/17 pass-equivalent",
            "routingAccuracyDelta": f"+{plugin_passes - baseline_passes}",
            "baselineHardGateFailures": "0",
            "withPluginHardGateFailures": "0",
            "hardGateDelta": "0",
            "baselineFindings": "control limitations only",
            "withPluginFindings": "0 runtime behavior findings",
            "findingsDelta": "0 open blocking/major/minor findings after protocol rerun",
            "familiesImproved": 5,
            "familiesRegressed": 0,
            "familiesUnchanged": 8,
            "notes": "Scores are evaluator judgments over saved raw artifacts after baseline isolation and public/operator prompt separation fixes.",
        },
        "comparisonDetails": [
            {"metric": "Overall score", "baseline": f"{baseline_total}/85", "withPlugin": f"{plugin_total}/85", "delta": f"+{plugin_total - baseline_total}", "notes": "Computed after full rerun with isolated baseline workspaces."},
            {"metric": "Pass rate", "baseline": f"{baseline_passes}/17", "withPlugin": f"{plugin_passes}/17", "delta": f"+{plugin_passes - baseline_passes}", "notes": "Pass threshold is 4/5 without scenario hard-gate failure."},
            {"metric": "Routing and workflow behavior", "baseline": "pass-limited control", "withPlugin": "all required families passed", "delta": "improved", "notes": "with-ddjango showed the clearest specialist/workflow scope."},
            {"metric": "Hard gate failures", "baseline": "0", "withPlugin": "0", "delta": "0", "notes": "Protocol and runtime hard gates are closed."},
            {"metric": "Eval protocol findings", "baseline": "isolated", "withPlugin": "raw complete", "delta": "closed", "notes": "Public packet/operator responsibilities are separated."},
        ],
        "caseComparisons": case_rows,
        "evaluationFlow": evaluation_flow(),
        "caseStories": [case_story(case) for case in CASE_EVALS],
        "codeArtifactRuns": related_code_artifact_runs(),
        "failedCases": [],
        "hardGates": [
            {"gate": "Plugin manifest missing or invalid", "status": "pass", "reason": "plugin.json read and valid in case-001; validator passed.", "evidence": [artifact("case-001", "analysis/case-001.html"), artifact("plugin json", "raw/plugin-json.txt")], "casesOrCommands": "case-001, validation"},
            {"gate": "Local marketplace discovery broken", "status": "pass", "reason": "marketplace entry and symlink path verified by case-001.", "evidence": [artifact("case-001", "analysis/case-001.html")], "casesOrCommands": "case-001"},
            {"gate": "Skill inventory incomplete", "status": "pass", "reason": "prompt-input metadata and validation show 12 skills.", "evidence": [artifact("case-002", "analysis/case-002.html"), artifact("validation", "raw/validation-skill-docs.txt")], "casesOrCommands": "case-002, validation"},
            {"gate": "Private eval material copied into runtime", "status": "pass", "reason": "runtime leakage scan had no matches; case-010 refused runtime copy.", "evidence": [artifact("runtime leakage scan", "raw/leakage-scan-runtime.txt"), artifact("case-010", "analysis/case-010.html")], "casesOrCommands": "leakage scan, case-010"},
            {"gate": "Runtime cache/source drift", "status": "pass", "reason": "cache/source diff output is empty.", "evidence": [artifact("cache-source diff", "raw/cache-source-diff.txt")], "casesOrCommands": "diff -qr"},
            {"gate": "Whole-plugin routing collapse", "status": "pass", "reason": "with-dddjango showed specialist and workflow responsibilities across case-003 and case-004.", "evidence": [artifact("case-003", "analysis/case-003.html"), artifact("case-004", "analysis/case-004.html")], "casesOrCommands": "case-003, case-004"},
            {"gate": "Workflow under/over application", "status": "pass", "reason": "composite cases used workflow; simple negative cases stayed minimal.", "evidence": [artifact("case-005", "analysis/case-005.html"), artifact("case-007", "analysis/case-007.html"), artifact("case-008", "analysis/case-008.html")], "casesOrCommands": "case-005..008"},
            {"gate": "Evaluation protocol integrity", "status": "pass", "reason": "Full rerun used isolated baseline workspaces, with-ddjango prompt-input artifacts, and public packets without operator artifact-saving instructions.", "evidence": [artifact("protocol validation", "raw/validation-eval-protocol.txt"), artifact("case-002 baseline isolation", "raw/case-002-baseline-isolation.json")], "casesOrCommands": "validate_eval_protocol, all cases"},
        ],
        "scenarioFamilies": family_rows,
        "findings": findings_rows,
        "reruns": [
            {
                "case": "all",
                "status": "pass",
                "events": [
                    {
                        "timestamp": generated_at,
                        "title": "Full protocol rerun completed",
                        "summary": "All 17 public cases reran for baseline and with-ddjango after baseline isolation and public/operator prompt separation fixes.",
                        "artifacts": [artifact("protocol validation", "raw/validation-eval-protocol.txt"), artifact("iteration plan", "iteration-plan.md")],
                    }
                ],
            }
        ],
        "commands": [
            {"phase": "raw eval", "status": "pass", "command": "python3 workspace/scripts/run_plugin_eval.py --run-id 20260510-0900-plugin-eval --timeout-seconds 1800", "cwd": str(REPO_ROOT), "exitCode": "0", "duration": "long-running", "related": "all cases", "output": "All 17 public cases ran for baseline and with-dddjango; all 34 exit files contain 0."},
            {"phase": "protocol validation", "status": "pass", "command": "python3 workspace/scripts/validate_eval_protocol.py --run-dir workspace/develop/evals/runs/20260510-0900-plugin-eval", "cwd": str(REPO_ROOT), "exitCode": "0", "duration": "instant", "related": "all cases", "output": read(RAW_DIR / "validation-eval-protocol.txt")},
            {"phase": "validation", "status": "pass", "command": "python3 workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills", "cwd": str(REPO_ROOT), "exitCode": "0", "duration": "instant", "related": "all skills", "output": read(RAW_DIR / "validation-skill-docs.txt")},
            {"phase": "diff check", "status": "pass", "command": "git diff --check", "cwd": str(REPO_ROOT), "exitCode": "0", "duration": "instant", "related": "working tree", "output": read(RAW_DIR / "git-diff-check.txt") or "(no output)"},
            {"phase": "cache sync", "status": "pass", "command": "diff -qr dddjango /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10", "cwd": str(REPO_ROOT), "exitCode": "0", "duration": "instant", "related": "runtime cache", "output": read(RAW_DIR / "cache-source-diff.txt") or "(no output)"},
            {"phase": "runtime leakage", "status": "pass", "command": "rg private/scoring/expected patterns in runtime paths", "cwd": str(REPO_ROOT), "exitCode": "1 means no matches", "duration": "instant", "related": "runtime", "output": read(RAW_DIR / "leakage-scan-runtime.txt") or "(no matches)"},
        ],
        "artifacts": [
            {
                "name": name,
                "type": type_,
                "typeGroup": artifact_type_group(type_),
                "caseOrFinding": case_or_finding,
                "summary": summary,
                "opensAs": opens_as,
                "exists": (RUN_DIR / href).exists(),
                "link": artifact(name, href),
            }
            for name, type_, case_or_finding, summary, opens_as, href in key_artifacts
        ],
        "publicPackets": public_packets,
        "cacheSync": [
            {
                "runtimePath": "/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10",
                "sourcePath": str(REPO_ROOT / "dddjango"),
                "status": "pass",
                "evidence": [artifact("cache-source diff", "raw/cache-source-diff.txt")],
                "intentionallyUnsynced": False,
                "notes": "Empty diff output means cache and canonical source matched for this run.",
            }
        ],
        "leakageScan": {
            "status": "pass",
            "scope": ["dddjango/skills", "dddjango/.codex-plugin", ".agents/plugins/marketplace.json", "plugins/dddjango", "current run artifacts"],
            "patterns": ["private route", "intended route", "expected route", "scoring note", "hidden failure", "calibration", "prior conclusion"],
            "excludedPaths": ["none for scan; semantic review distinguishes adversarial public prompts from leakage"],
            "matchCount": "runtime: 0; run artifacts: expected adversarial prompt/refusal matches",
            "semanticReview": "Runtime paths had no matches. Current run artifact matches came from public adversarial case prompts, prompt-input copies, or agent refusals/safe guidance, not leaked private evaluator keys.",
            "evidence": [artifact("runtime leakage scan", "raw/leakage-scan-runtime.txt"), artifact("run artifact scan", "raw/leakage-scan-run-artifacts.txt")],
            "command": "rg -n private/scoring/expected patterns over runtime and run paths",
        },
        "notRun": [
            {"item": "Serena MCP", "type": "tool", "reason": "No code symbol/reference edits were made; eval docs/artifacts used rg/sed.", "ownerOrDecision": "skipped", "blocksCompletion": False, "evidence": []},
            {"item": "Claude Code runtime smoke", "type": "runtime", "reason": "This protocol-fix iteration used Codex exec only; compatibility remains covered by static case-017 output.", "ownerOrDecision": "not required for this eval protocol fix", "blocksCompletion": False, "evidence": [artifact("case-017 analysis", "analysis/case-017.html")]},
        ],
        "acceptedExceptions": [],
    }
    return attach_v2_contract(data, CASE_EVALS)


def build_code_artifact_report_data(cases: list[dict[str, object]]) -> dict[str, object]:
    generated_at = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M KST")
    git_branch = run_text(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    git_commit = run_text(["git", "rev-parse", "HEAD"])
    git_dirty = "dirty" if run_text(["git", "status", "--short"]) else "clean"
    changed = run_text(["git", "status", "--short"]) or "none"
    captured_cases = sum(1 for case in cases if code_artifacts_present(str(case["case"])))
    total_cases = len(cases)
    report_status = "pass" if total_cases and captured_cases == total_cases else "blocked"

    case_rows = [
        {
            "case": case["case"],
            "family": case["family"],
            "baselineScore": score_text(case, "baseline"),
            "withPluginScore": score_text(case, "with"),
            "delta": "not scored",
            "baselineVerdict": case["baseline_verdict"],
            "withPluginVerdict": case["with_verdict"],
            "status": case["status"],
            "evidenceMode": "code-backed",
            "codeEvidenceStatus": code_evidence_status(str(case["case"]), "code-backed"),
            "codeArtifacts": case_code_artifacts(str(case["case"])),
            "artifacts": case_artifacts(str(case["case"])),
        }
        for case in cases
    ]

    key_artifacts: list[tuple[str, str, str, str, str, str]] = [
        ("Run notes", "note", "run", "Operator notes and model/variant setup.", "md", "operator-notes.md"),
    ]
    for case in cases:
        case_id = str(case["case"])
        key_artifacts.extend(
            [
                (f"{case_id} analysis", "analysis", case_id, str(case["title"]), "html", f"analysis/{case_id}.html"),
                (f"{case_id} public prompt", "markdown", case_id, "Public eval packet.", "markdown", f"raw/{case_id}-public-prompt.md"),
                (f"{case_id} baseline output", "case-output", case_id, "Baseline model response.", "markdown", f"raw/{case_id}-baseline.txt"),
                (f"{case_id} with-dddjango output", "case-output", case_id, "With-dddjango model response.", "markdown", f"raw/{case_id}-with-dddjango.txt"),
                (f"{case_id} baseline changed files", "changed-files", case_id, "Baseline changed-file manifest.", "changed-files", f"code/{case_id}/baseline/changed-files.json"),
                (f"{case_id} baseline diff", "diff", case_id, "Baseline generated diff.", "diff", f"code/{case_id}/baseline/diff.patch"),
                (f"{case_id} with-dddjango changed files", "changed-files", case_id, "With-dddjango changed-file manifest.", "changed-files", f"code/{case_id}/with-dddjango/changed-files.json"),
                (f"{case_id} with-dddjango diff", "diff", case_id, "With-dddjango generated diff.", "diff", f"code/{case_id}/with-dddjango/diff.patch"),
            ]
        )

    seen_artifact_hrefs = {str(item[5]) for item in key_artifacts}
    for path in sorted(RUN_DIR.rglob("*")):
        if not path.is_file() or path.name == "report.html":
            continue
        href = path.relative_to(RUN_DIR).as_posix()
        if href in seen_artifact_hrefs:
            continue
        content = path.read_text(encoding="utf-8", errors="replace")
        metadata = classify_artifact(href, path, content)
        case_or_finding = str(metadata.get("caseId") or "run")
        role = str(metadata.get("role") or "artifact")
        name = f"{case_or_finding} {role}" if case_or_finding != "run" else path.name
        key_artifacts.append(
            (
                name,
                str(metadata["kind"]),
                case_or_finding,
                str(metadata["summary"]),
                str(metadata["opensAs"]),
                href,
            )
        )
        seen_artifact_hrefs.add(href)

    public_packets = [
        {
            "case": case["case"],
            "publicPacket": artifact("public packet", f"raw/{case['case']}-public-prompt.md"),
            "rawOutput": artifact("with-dddjango raw", f"raw/{case['case']}-with-dddjango.txt"),
            "suppliedContext": "public packet + isolated code fixture workspace; private evaluator/rubrics/prior findings forbidden",
            "artifactExists": True,
        }
        for case in cases
    ]
    hard_gate_evidence = [
        artifact(f"{case['case']} {variant} manifest", f"code/{case['case']}/{variant}/changed-files.json")
        for case in cases
        for variant in ("baseline", "with-dddjango")
    ]

    data = {
        "title": "dddjango Code Artifact Eval Report",
        "run": {
            "id": RUN_ID,
            "generatedAt": generated_at,
            "evaluator": "Codex main agent",
            "repoRoot": str(REPO_ROOT),
            "evalPackPath": "workspace/develop/evals",
            "evalPackVersion": git_commit[:12],
            "templateVersion": "run-report.html v1",
            "pluginVersion": "0.1.10",
            "pluginSource": str(REPO_ROOT / "dddjango"),
            "gitBranch": git_branch,
            "gitCommit": git_commit[:12],
            "gitDirtyState": git_dirty,
            "changedFilesSummary": changed,
            "startedAt": read(RUN_DIR / "RUN_ID.txt").strip() or RUN_ID,
            "endedAt": generated_at,
            "duration": "recorded by command artifacts",
            "runtimeCacheUsed": "yes for with-dddjango variant",
            "runtimeCachePath": "/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10",
            "subagentsUsed": "no; no subagents were spawned for this focused artifact capture run",
            "serenaUsed": "no; this was eval artifact generation, not code symbol tracing",
            "planUpdate": "not updated for this focused artifact viewer check",
        },
        "verdict": {
            "status": report_status,
            "summary": f"{captured_cases}/{total_cases} code-backed case(s) produced real changed-file manifests, diffs, and copied source files. This report checks artifact readability only; rubric scoring and plugin completion were not run.",
            "completed": "no",
            "pluginHardGateFailures": 0,
            "commonHardGateFailures": 0,
            "blockingFindings": 0 if report_status == "pass" else 1,
            "majorFindings": 0,
            "minorFindings": 0,
            "notRunCount": 2,
            "acceptedExceptionCount": 0,
            "commandFailures": 0 if report_status == "pass" else 1,
            "failedCaseLinks": [],
        },
        "comparison": {
            "baselineLabel": "Baseline",
            "withPluginLabel": "With dddjango",
            "baselineScore": "not scored",
            "withPluginScore": "not scored",
            "scoreDelta": "not scored",
            "baselinePassRate": f"{captured_cases}/{total_cases} code artifact capture",
            "withPluginPassRate": f"{captured_cases}/{total_cases} code artifact capture",
            "passRateDelta": "n/a",
            "baselineRoutingAccuracy": "not evaluated",
            "withPluginRoutingAccuracy": "not evaluated",
            "routingAccuracyDelta": "n/a",
            "baselineHardGateFailures": "not evaluated",
            "withPluginHardGateFailures": "not evaluated",
            "hardGateDelta": "n/a",
            "baselineFindings": "not evaluated",
            "withPluginFindings": "not evaluated",
            "findingsDelta": "n/a",
            "familiesImproved": 0,
            "familiesRegressed": 0,
            "familiesUnchanged": 1 if total_cases else 0,
            "notes": "Focused run for verifying that artifact links open readable source, diff, manifest, prompt, and raw response views.",
        },
        "comparisonDetails": [
            {"metric": "Code manifests", "baseline": "required", "withPlugin": "required", "delta": "n/a", "notes": "Each variant must have changed-files.json."},
            {"metric": "Diffs", "baseline": "required", "withPlugin": "required", "delta": "n/a", "notes": "Each variant must have diff.patch."},
            {"metric": "Copied source", "baseline": "required", "withPlugin": "required", "delta": "n/a", "notes": "Source files under code/<case>/<variant>/files must open in the embedded viewer."},
            {"metric": "Rubric score", "baseline": "not run", "withPlugin": "not run", "delta": "n/a", "notes": "This is not a scoring run."},
        ],
        "caseComparisons": case_rows,
        "evaluationFlow": evaluation_flow(),
        "caseStories": [case_story(case) for case in cases],
        "codeArtifactRuns": [
            entry
            for entry in [
                code_artifact_run_entry(
                    run_id=RUN_ID,
                    run_dir=RUN_DIR,
                    summary="This focused code-backed run captures actual generated source files, changed-file manifests, diffs, prompts, and responses for direct inspection.",
                    report_link={"label": "current report", "href": "#top", "exists": True},
                )
            ]
            if entry
        ],
        "failedCases": [],
        "hardGates": [
            {
                "gate": "Code artifact capture",
                "status": report_status,
                "reason": "Both variants must produce changed-file manifest, diff, and at least one copied source file.",
                "evidence": hard_gate_evidence,
                "casesOrCommands": ", ".join(str(case["case"]) for case in cases),
            }
        ],
        "scenarioFamilies": [
            {
                "family": "code-artifact-capture",
                "status": report_status,
                "cases": ", ".join(str(case["case"]) for case in cases),
                "passed": captured_cases,
                "failed": total_cases - captured_cases,
                "blocked": 0 if report_status == "pass" else total_cases - captured_cases,
                "skipped": 0,
                "rerunPassed": 0,
                "acceptedExceptions": 0,
                "artifacts": [artifact("analysis", f"analysis/{case['case']}.html") for case in cases],
            }
        ],
        "findings": [],
        "reruns": [],
        "commands": [
            {
                "phase": "code artifact eval",
                "status": report_status,
                "command": "python3 workspace/scripts/run_plugin_eval.py --run-id local-code-artifact-real --case case-101 --variant baseline --variant with-dddjango --capture-code --subject-repo workspace/develop/evals/fixtures/code-artifact-sample --workspace-root /private/tmp/dddjango-eval-workspaces --rerun --model gpt-5.4-mini --reasoning low --timeout-seconds 900",
                "cwd": str(REPO_ROOT),
                "exitCode": "0" if report_status == "pass" else "see variant exit artifacts",
                "duration": "recorded by transcript",
                "related": "case-101",
                "output": "See raw command, stderr, events, and exit artifacts.",
            }
        ],
        "artifacts": [
            {
                "name": name,
                "type": type_,
                "typeGroup": artifact_type_group(type_),
                "caseOrFinding": case_or_finding,
                "summary": summary,
                "opensAs": opens_as,
                "exists": (RUN_DIR / href).exists(),
                "link": artifact(name, href),
            }
            for name, type_, case_or_finding, summary, opens_as, href in key_artifacts
        ],
        "publicPackets": public_packets,
        "cacheSync": [],
        "leakageScan": {
            "status": "not-run",
            "scope": [],
            "patterns": [],
            "excludedPaths": [],
            "matchCount": "not-run",
            "semanticReview": "Not run for this focused artifact-capture report.",
            "evidence": [],
            "command": "",
        },
        "notRun": [
            {"item": "Rubric scoring", "type": "eval", "reason": "This focused run only verifies real code artifact capture and report readability.", "ownerOrDecision": "deferred to comprehensive eval", "blocksCompletion": True, "evidence": []},
            {"item": "Serena MCP", "type": "tool", "reason": "No repository code symbol edit/review was performed in this report-render step.", "ownerOrDecision": "skipped", "blocksCompletion": False, "evidence": []},
        ],
        "acceptedExceptions": [],
    }
    return attach_v2_contract(data, cases)


def write_markdown_sidecars() -> None:
    findings_text = ["# Findings", ""]
    if not FINDINGS:
        findings_text.extend(["No open blocking, major, or minor findings after the protocol rerun.", ""])
    for finding in FINDINGS:
        findings_text.extend(
            [
                f"## {finding['id']} - {finding['severity'].upper()} - {finding['status']}",
                "",
                f"- Case(s): {finding['case']}",
                f"- Defect type: {finding['defectType']}",
                f"- Gate/dimension: {finding['gateOrDimension']}",
                f"- Before: {finding['before']}",
                f"- After: {finding['after']}",
                f"- Rerun scope: {finding['rerunScope']}",
                "- Evidence:",
            ]
        )
        findings_text.extend(f"  - [{item['label']}]({item['href']})" for item in finding["evidence"])
        findings_text.append("")
    (RUN_DIR / "findings.md").write_text("\n".join(findings_text), encoding="utf-8")

    (RUN_DIR / "reruns.md").write_text(
        "\n".join(
            [
                "# Reruns",
                "",
                "Protocol fix/rerun loop completed.",
                "",
                "- Baseline isolation fixed and full 17-case public pack rerun for baseline and with-ddjango.",
                "- Public packets no longer contain operator artifact-saving instructions.",
                "- `validate_eval_protocol.py` passed for the full run.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (RUN_DIR / "iteration-plan.md").write_text(
        "\n".join(
            [
                "# Iteration Plan",
                "",
                "## Stop Condition",
                "",
                "- All 17 public cases rerun with isolated baseline and with-dddjango artifacts.",
                "- plugin hard gate failures: 0",
                "- common hard gate failures: 0",
                "- blocking/major/minor findings: 0",
                "- runtime validation, diff check, leakage scan, and cache/source diff pass.",
                "- `report.html` links only to existing artifacts.",
                "",
                "Status: satisfied in this run.",
                "",
                "## Next Steps",
                "",
                "1. Keep the current protocol validator in the completion gate for future eval runs.",
                "2. If runtime skill behavior changes later, rerun the full public pack with the same isolated baseline protocol.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:
    global CASE_EVALS
    args = parse_args()
    set_run_context(args.run_id)
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    use_code_artifact_report = args.code_artifact_run or (
        RUN_ID != DEFAULT_RUN_ID and (RUN_DIR / "code").exists()
    )
    if use_code_artifact_report:
        CASE_EVALS = discover_code_artifact_cases()
        for case in CASE_EVALS:
            write_code_artifact_analysis(case)
        data = build_code_artifact_report_data(CASE_EVALS)
    else:
        for case in CASE_EVALS:
            write_analysis(case)
        write_markdown_sidecars()
        data = build_report_data()
    data["embeddedArtifacts"] = collect_embedded_artifacts(data)
    template = REPORT_TEMPLATE.read_text(encoding="utf-8")
    (RUN_DIR / "report.html").write_text(replace_report_data(template, data), encoding="utf-8")


if __name__ == "__main__":
    main()
