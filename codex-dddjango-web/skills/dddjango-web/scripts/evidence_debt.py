"""증거 부채 술어 — 조작 상태 증거(관찰 문서 version 2 + interactions)가 없는 archive case를 구조로 센다.

hook(evidence_debt_hook.py)과 검사기(check_design_evidence.py)가 같은 필드 집합·같은 판정을 쓴다(단일 출처).
메시지 grep 없음·바이트 해시 없음·manifest 대조 없음·의존성 파싱 없음 — 매 프롬프트마다 실행되므로
stdlib json으로 design-input.json·build-state.json·case별 관찰 문서만 읽는다.

대상 한정: `build-state.json.design_status == "ready"`인 archive 빌드만 부채 판정 대상이다.
진행 중 빌드는 입력 게이트가 경로 위에 있고, 완료 이력 빌드가 규칙 개정으로 부채가 된 사례가 이 술어의 대상이다.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

DECISIONS = ('observe', 'defer')
POINTER_FIELDS = frozenset({'path', 'sha256'})
# 관찰 문서(source-observation.json) 필드 집합 — 검사기 `_source_observation`과 공유.
# (검사기의 `INTERACTION_FIELDS`는 별개 문서 interactions.json의 집합이라 이름을 겹치지 않게 둔다.)
OBSERVATION_V1_FIELDS = frozenset({'version', 'archive_sha256', 'entrypoint', 'case_id', 'screen', 'state',
                                   'viewport', 'url', 'observed_at', 'capture', 'trace'})
OBSERVATION_V2_FIELDS = OBSERVATION_V1_FIELDS | {'interactions'}
CASE_REASONS = ('static_only', 'missing', 'unreadable', 'malformed')


def is_interaction_observation(observed: Any) -> bool:
    """검사기가 정확 필드 검사 뒤에 쓰는 느슨한 판정 — version 2이고 `interactions` 키가 있다."""
    return isinstance(observed, dict) and observed.get('version') == 2 and 'interactions' in observed


def has_interaction_evidence(observed: Any) -> bool:
    """hook이 쓰는 엄격 판정 — 검사기가 exit 2로 거부할 문서를 «증거 있음»으로 세지 않는다."""
    return (is_interaction_observation(observed)
            and set(observed) == OBSERVATION_V2_FIELDS
            and isinstance(observed.get('interactions'), dict)
            and set(observed['interactions']) == POINTER_FIELDS)


@dataclass(frozen=True)
class BuildDebt:
    build: Path
    cases_total: int
    cases_debt: int
    decision: dict | None
    error: str | None = None
    reasons: dict[str, int] = field(default_factory=dict)

    @property
    def status(self) -> str:
        if self.error is not None:
            return 'error'
        if self.cases_debt == 0:
            return 'clear'
        if self.decision is None:
            return 'undecided'
        return 'deferred' if self.decision['decision'] == 'defer' else 'observing'


class _Unreadable(Exception):
    pass


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def _confined(build: Path, value: Any) -> Path | None:
    """빌드 폴더 안을 가리키는 상대 경로만 받는다 — 절대 경로·탈출(`..`)은 None."""
    if not isinstance(value, str) or not value or Path(value).is_absolute():
        return None
    try:
        resolved = (build / value).resolve()
        if not resolved.is_relative_to(build.resolve()):
            return None
    except OSError:
        return None
    return resolved


def _is_archive(build: Path, spec: dict) -> bool:
    manifests = spec.get('manifests')
    if not isinstance(manifests, list):
        raise _Unreadable('design-input.json.manifests: list required')
    archive = False
    for index, value in enumerate(manifests):
        path = _confined(build, value)
        if path is None:
            raise _Unreadable(f'design-input.json.manifests[{index}]: path inside build required')
        try:
            manifest = _load(path)
        except (OSError, ValueError) as error:
            raise _Unreadable(f'manifests[{index}]: {type(error).__name__}: {error}') from error
        if isinstance(manifest, dict) and manifest.get('collection') == 'archive':
            archive = True
    return archive


def _decision(state: dict) -> dict | None:
    value = state.get('evidence_debt')
    if isinstance(value, dict) and value.get('decision') in DECISIONS:
        return value
    return None


def case_reason(build: Path, case: Any) -> str:
    """'ok' 또는 CASE_REASONS 중 하나 — static_only(v1 정적 관찰만) · missing(포인터/파일 없음) ·
    unreadable(읽기·JSON 실패) · malformed(필드 집합 불량 — 검사기도 거부)."""
    if not isinstance(case, dict):
        return 'malformed'
    pointer = case.get('source_observation')
    if not isinstance(pointer, dict) or set(pointer) != POINTER_FIELDS:
        return 'missing'
    path = _confined(build, pointer.get('path'))
    if path is None or not path.is_file():
        return 'missing'
    try:
        observed = _load(path)
    except (OSError, ValueError):
        return 'unreadable'
    if has_interaction_evidence(observed):
        return 'ok'
    if isinstance(observed, dict) and observed.get('version') == 1 and set(observed) == OBSERVATION_V1_FIELDS:
        return 'static_only'
    return 'malformed'


def build_debt(build: Path) -> BuildDebt | None:
    """None = 판정 대상 아님(design-input 없음 · 정적 시안 · ready 아님). error = 읽을 수 없어 판정 불가."""
    build = Path(build)
    input_path = build / 'design-input.json'
    if not input_path.is_file():
        return None
    state_path = build / 'build-state.json'
    try:
        state = _load(state_path) if state_path.is_file() else None
    except (OSError, ValueError) as error:
        return BuildDebt(build, 0, 0, None, f'build-state.json: {type(error).__name__}: {error}')
    if not isinstance(state, dict) or state.get('design_status') != 'ready':
        return None
    try:
        spec = _load(input_path)
    except (OSError, ValueError) as error:
        return BuildDebt(build, 0, 0, None, f'design-input.json: {type(error).__name__}: {error}')
    if not isinstance(spec, dict):
        return BuildDebt(build, 0, 0, None, 'design-input.json: object required')
    try:
        if not _is_archive(build, spec):
            return None
    except _Unreadable as error:
        return BuildDebt(build, 0, 0, None, str(error))
    cases = spec.get('cases')
    if not isinstance(cases, list):
        return BuildDebt(build, 0, 0, None, 'design-input.json.cases: list required')
    reasons = {reason: 0 for reason in CASE_REASONS}
    for case in cases:
        reason = case_reason(build, case)
        if reason != 'ok':
            reasons[reason] += 1
    debt = sum(reasons.values())
    return BuildDebt(build, len(cases), debt, _decision(state), reasons=reasons)
