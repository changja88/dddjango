"""증거 부채 술어 — 조작 상태 증거(관찰 문서 version 2 + interactions)가 없는 archive case를 구조로 센다.

hook(evidence_debt_hook.py)과 검사기(check_design_evidence.py)가 같은 판정을 쓴다(단일 출처).
메시지 grep 없음·바이트 해시 없음·manifest 대조 없음·의존성 파싱 없음 — 매 프롬프트마다 실행되므로
stdlib json으로 design-input.json·build-state.json·case별 관찰 문서 헤더만 읽는다.

대상 한정: `build-state.json.design_status == "ready"`인 archive 빌드만 부채 판정 대상이다.
진행 중 빌드는 입력 게이트가 경로 위에 있고, 완료 이력 빌드가 규칙 개정으로 부채가 된 사례가 이 술어의 대상이다.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DECISIONS = ('observe', 'defer')


def has_interaction_evidence(observed: Any) -> bool:
    """관찰 문서가 조작 상태 증거를 실었는가 — version 2이고 `interactions` 포인터가 있다."""
    return isinstance(observed, dict) and observed.get('version') == 2 and 'interactions' in observed


@dataclass(frozen=True)
class BuildDebt:
    build: Path
    cases_total: int
    cases_debt: int
    decision: dict | None
    error: str | None = None

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


def _case_has_evidence(build: Path, case: Any) -> bool:
    if not isinstance(case, dict):
        return False
    pointer = case.get('source_observation')
    if not isinstance(pointer, dict):
        return False
    path = _confined(build, pointer.get('path'))
    if path is None:
        return False
    try:
        observed = _load(path)
    except (OSError, ValueError):
        return False
    return has_interaction_evidence(observed)


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
    debt = sum(0 if _case_has_evidence(build, case) else 1 for case in cases)
    return BuildDebt(build, len(cases), debt, _decision(state))
