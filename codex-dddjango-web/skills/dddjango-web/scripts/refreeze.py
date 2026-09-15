#!/usr/bin/env python3
"""재동결 — 기존 동결물을 전량 폐기하고 staging에서 새로 동결해 교체한다.

Usage: refreeze.py begin  --build BUILD --project-root ROOT --quote TEXT
       refreeze.py check  --build BUILD [--staging DIR] [--render-audit-skipped REASON]
       refreeze.py commit --build BUILD [--staging DIR] [--resume] [--stop-after PHASE]
       refreeze.py abort  --build BUILD [--staging DIR]

재동결은 차이를 대조하지 않는다. `begin`이 staging과 journal을 만들고 폐기 집합을 확정하며,
재수집은 그 staging을 대상으로 수행하고, `check`가 완전성을 본 뒤 `commit`이 파일 단위
트랜잭션으로 교체한다. live 빌드 폴더는 교체 순간까지 손대지 않는다 — 다만 이미지 도구는
프로젝트 트리(`web/static/images/`)에 직접 쓰므로 실패 시 `abort`가 그 차집합을 되돌린다.

폐기 집합은 `design-input.json`의 포인터를 3겹으로 순회해 정한다. 어느 포인터에도 없는
`captures/**`는 «고아»이며 지우지 않고 journal에 기록해 보고한다.

되감기는 **phase에 의존하지 않는다** — `_prev`에 실제로 들어 있는 것을 전부 되돌린다.
단계 도중 중단돼도(phase는 단계 끝에서만 갱신된다) 원본이 사라지지 않게 하기 위함이다.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

FIXED_DISCARD_FILES = (
    'source-manifest.json', 'design-tokens.json', 'asset-manifest.json', 'screen-meta.json',
    'render-audit.json', 'design-input.json', 'coverage-review.md', 'scope.md',
    'refreeze-diff.json',
)
FIXED_DISCARD_TREES = ('design-ref',)
INPUT_GLOBS = ('scope.md', '*-declared.json', '*excluded-regions*.json')
REQUIRED_STAGING = ('source-manifest.json', 'design-tokens.json', 'asset-manifest.json',
                    'screen-meta.json', 'design-input.json')
IMAGES_SUBDIR = Path('web') / 'static' / 'images'
PHASES = ('planned', 'discarded', 'installed', 'verified', 'done')
STAGING_PREFIX = '_refreeze-'
PREV_PREFIX = '_prev-'
DISCARDED_PREFIX = '_discarded-'
JOURNAL = 'journal.json'
PLAN = 'swap-plan.json'
BOOKKEEPING = (JOURNAL, PLAN)
# 렌더 실측 생략이 합법인 사유 — commands 의 enum 과 같은 닫힌 목록.
SKIP_REASONS = ('원본 열람 불가', '필요한 인증 상태 접근 불가', '브라우저 채널 부재')


class RefreezeError(Exception):
    """호출부가 exit 1로 옮기는 오류."""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> object:
    # BOM 붙은 산출물이 같은 트리에 실재한다 — utf-8 로 읽으면 조용히 «없는 것»이 된다.
    return json.loads(path.read_text(encoding='utf-8-sig'))


def dump_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=1), encoding='utf-8')


def now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec='seconds')


def confined(build: Path, value: object) -> str | None:
    """빌드 폴더 안을 가리키는 상대 경로만 받는다 — 절대 경로·탈출은 None."""
    if not isinstance(value, str) or not value or Path(value).is_absolute():
        return None
    target = (build / value).resolve()
    if not target.is_relative_to(build.resolve()):
        return None
    return Path(value).as_posix()


def pointer_paths(build: Path, value: object) -> list[str]:
    if not isinstance(value, dict):
        return []
    local = confined(build, value.get('path'))
    return [local] if local else []


def _read_document(build: Path, rel: str, errors: list[str]) -> dict | None:
    """읽을 수 없는 증거 문서는 조용히 넘기지 않는다 — 폐기 집합이 줄어든다."""
    path = build / rel
    if not path.is_file():
        errors.append(f'{rel}: 파일이 없다')
        return None
    try:
        document = load_json(path)
    except (OSError, ValueError) as error:
        errors.append(f'{rel}: {type(error).__name__}: {error}')
        return None
    if not isinstance(document, dict):
        errors.append(f'{rel}: object required')
        return None
    return document


def _walk_observation(build: Path, rel: str, found: list[str], errors: list[str]) -> None:
    """2겹·3겹 — 관찰 문서 안의 capture·trace·interactions, 그 안의 상태 캡처."""
    document = _read_document(build, rel, errors)
    if document is None:
        return
    for key in ('capture', 'trace', 'interactions'):
        found.extend(pointer_paths(build, document.get(key)))
    local = (pointer_paths(build, document.get('interactions')) or [None])[0]
    if local is None:
        return
    states = _read_document(build, local, errors)
    if states is None:
        return
    initial = states.get('initial')
    if isinstance(initial, dict):
        found.extend(pointer_paths(build, initial.get('capture')))
    steps = states.get('steps')
    if isinstance(steps, list):
        for step in steps:
            after = step.get('after') if isinstance(step, dict) else None
            if isinstance(after, dict):
                found.extend(pointer_paths(build, after.get('capture')))


def evidence_pointers(build: Path, errors: list[str] | None = None) -> list[str]:
    """design-input.json에서 3겹으로 순회한 원본 증거 경로."""
    errors = errors if errors is not None else []
    spec_path = build / 'design-input.json'
    if not spec_path.is_file():
        return []
    try:
        spec = load_json(spec_path)
    except (OSError, ValueError) as error:
        errors.append(f'design-input.json: {type(error).__name__}: {error}')
        return []
    if not isinstance(spec, dict) or not isinstance(spec.get('cases'), list):
        errors.append('design-input.json: cases 목록이 없다')
        return []
    found: list[str] = []
    for case in spec['cases']:
        if not isinstance(case, dict):
            continue
        found.extend(pointer_paths(build, case.get('reference_capture')))
        for rel in pointer_paths(build, case.get('source_observation')):
            found.append(rel)
            _walk_observation(build, rel, found, errors)
    return found


def preserved_set(build: Path) -> set[str]:
    """visual-evidence.json이 가리키는 구현 증거 — 재동결이 만들지 않으므로 보존한다."""
    path = build / 'visual-evidence.json'
    if not path.is_file():
        return set()
    try:
        evidence = load_json(path)
    except (OSError, ValueError):
        return set()
    found: set[str] = set()

    def visit(node: object) -> None:
        if isinstance(node, dict):
            if isinstance(node.get('path'), str) and 'sha256' in node:
                found.update(pointer_paths(build, node))
            for value in node.values():
                visit(value)
        elif isinstance(node, list):
            for value in node:
                visit(value)

    visit(evidence)
    return found


def discard_set(build: Path, errors: list[str] | None = None) -> list[str]:
    """폐기·교체 대상 — 실재하는 파일만, 파일 단위로 전개한다."""
    build = Path(build)
    found: set[str] = set()
    for name in FIXED_DISCARD_FILES:
        if (build / name).is_file():
            found.add(name)
    for tree in FIXED_DISCARD_TREES:
        root = build / tree
        if root.is_dir():
            found.update(item.relative_to(build).as_posix()
                         for item in root.rglob('*') if item.is_file())
    for pattern in INPUT_GLOBS:
        found.update(item.name for item in build.glob(pattern) if item.is_file())
    for rel in evidence_pointers(build, errors):
        if (build / rel).is_file():
            found.add(rel)
    return sorted(found - preserved_set(build))


def orphan_set(build: Path) -> list[str]:
    """captures/** 중 어느 포인터에도 없는 파일 — 지우지 않고 보고한다."""
    build = Path(build)
    captures = build / 'captures'
    if not captures.is_dir():
        return []
    known = set(discard_set(build)) | preserved_set(build)
    return sorted(item.relative_to(build).as_posix()
                  for item in captures.rglob('*')
                  if item.is_file() and item.relative_to(build).as_posix() not in known)


def images_listing(project_root: Path) -> list[str]:
    root = project_root / IMAGES_SUBDIR
    if not root.is_dir():
        return []
    return sorted(item.relative_to(project_root).as_posix()
                  for item in root.rglob('*') if item.is_file())


def _single(build: Path, prefix: str, explicit: Path | None = None) -> Path | None:
    if explicit is not None:
        resolved = explicit if explicit.is_absolute() else (build / explicit)
        resolved = resolved.resolve()
        if not resolved.is_relative_to(build.resolve()) or not resolved.is_dir():
            raise RefreezeError(f'--staging 은 빌드 폴더 안의 디렉터리여야 한다: {explicit}')
        return resolved
    found = sorted(p for p in build.glob(f'{prefix}*') if p.is_dir())
    if len(found) > 1:
        raise RefreezeError(f'{prefix}* 가 여럿이다 — --staging 으로 고른다: '
                            + ', '.join(p.name for p in found))
    return found[0] if found else None


def read_state(build: Path) -> dict:
    path = build / 'build-state.json'
    if not path.is_file():
        return {}
    value = load_json(path)
    return value if isinstance(value, dict) else {}


def write_state(build: Path, state: dict) -> None:
    dump_json(build / 'build-state.json', state)


def current_debt_cases(build: Path) -> int:
    """부채 case 수 — evidence_debt 술어와 단일 출처를 쓴다."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        import evidence_debt
    except ImportError:  # pragma: no cover - 미러 배치 오류만 해당
        return 0
    debt = evidence_debt.build_debt(build)
    return debt.cases_debt if debt is not None else 0


def pointer_health(build: Path) -> list[str]:
    """3겹 포인터가 실재·sha 일치하는지 — verify_inputs의 시험용 대역이자 check의 축."""
    issues: list[str] = []
    spec_path = build / 'design-input.json'
    if not spec_path.is_file():
        return ['design-input.json: 없다']
    try:
        spec = load_json(spec_path)
    except (OSError, ValueError) as error:
        return [f'design-input.json: {type(error).__name__}: {error}']
    for key in ('scope', 'coverage_review'):
        issues.extend(_pointer_issue(build, spec.get(key), key))
    cases = spec.get('cases') if isinstance(spec, dict) else None
    for case in cases if isinstance(cases, list) else []:
        label = case.get('id') if isinstance(case, dict) else '?'
        for key in ('reference_capture', 'source_observation'):
            issues.extend(_pointer_issue(build, case.get(key), f'{label}.{key}'))
        for rel in pointer_paths(build, case.get('source_observation')):
            issues.extend(_observation_issue(build, rel, str(label)))
    return issues


def _pointer_issue(build: Path, value: object, label: str) -> list[str]:
    if not isinstance(value, dict):
        return [f'{label}: 포인터가 아니다']
    local = confined(build, value.get('path'))
    if local is None:
        return [f'{label}: 경로가 빌드 밖이다 ({value.get("path")!r})']
    target = build / local
    if not target.is_file():
        return [f'{label}: 파일이 없다 ({local})']
    if sha256(target) != value.get('sha256'):
        return [f'{label}: sha256 불일치 ({local})']
    return []


def _observation_issue(build: Path, rel: str, label: str) -> list[str]:
    errors: list[str] = []
    document = _read_document(build, rel, errors)
    if document is None:
        return [f'{label}.source_observation: {errors[0]}']
    issues: list[str] = []
    for key in ('capture', 'trace'):
        if key in document:
            issues.extend(_pointer_issue(build, document[key], f'{label}.{key}'))
    interactions = document.get('interactions')
    if interactions is None:
        return issues
    issues.extend(_pointer_issue(build, interactions, f'{label}.interactions'))
    local = (pointer_paths(build, interactions) or [None])[0]
    if local is None or not (build / local).is_file():
        return issues
    states = _read_document(build, local, errors)
    if states is None:
        return issues + [f'{label}.interactions: {errors[-1]}']
    initial = states.get('initial')
    if isinstance(initial, dict) and 'capture' in initial:
        issues.extend(_pointer_issue(build, initial['capture'], f'{label}.initial.capture'))
    steps = states.get('steps')
    for index, step in enumerate(steps if isinstance(steps, list) else []):
        after = step.get('after') if isinstance(step, dict) else None
        if isinstance(after, dict) and 'capture' in after:
            issues.extend(_pointer_issue(build, after['capture'],
                                         f'{label}.steps[{index}].after.capture'))
    return issues


def verify_inputs(build: Path, project_root: Path) -> tuple[bool, str]:
    """교체 후 live 재확인 — check_design_evidence.py --phase inputs."""
    checker = Path(__file__).resolve().parent / 'check_design_evidence.py'
    result = subprocess.run(
        [sys.executable, str(checker), '--build', str(build),
         '--project-root', str(project_root), '--phase', 'inputs'],
        capture_output=True, text=True)
    detail = (result.stdout + result.stderr).strip()
    return result.returncode == 0, detail


# --- begin -----------------------------------------------------------------

def cmd_begin(build: Path, project_root: Path, quote: str) -> int:
    existing = sorted(p for p in build.glob(f'{STAGING_PREFIX}*')) + \
        sorted(p for p in build.glob(f'{PREV_PREFIX}*'))
    if existing:
        print(f'[refreeze] 진행 중인 재동결이 있다: {", ".join(p.name for p in existing)} — '
              'commit --resume 또는 abort 로 정리한 뒤 다시 시작한다')
        return 2
    errors: list[str] = []
    discard = discard_set(build, errors)
    for issue in errors:
        # 재동결이 고칠 대상이 재동결을 막으면 안 된다 — 사실을 journal 에 적고 진행한다.
        # 되감기 안전성은 `_prev` 가 지므로 폐기 집합이 불완전해도 되돌릴 수 있다.
        print(f'[refreeze] 증거 문서를 읽을 수 없다 — 폐기 집합이 불완전하다(기록하고 진행): {issue}')
    staging = build / f'{STAGING_PREFIX}{time.strftime("%Y%m%d-%H%M%S")}'
    staging.mkdir()
    try:
        copied: list[str] = []
        for pattern in INPUT_GLOBS:
            for item in sorted(build.glob(pattern)):
                if item.is_file():
                    shutil.copy2(item, staging / item.name)
                    copied.append(item.name)
        state = read_state(build)
        spec = build / 'design-input.json'
        exclusions = []
        if spec.is_file():
            try:
                value = load_json(spec)
            except Exception as error:   # 폐기 집합과 같은 이유로 여기서도 막으면 안 된다
                errors.append(f'design-input.json: {type(error).__name__}: {error}')
                print(f'[refreeze] 예외 목록을 읽을 수 없다(기록하고 진행): {error}')
                value = None
            if isinstance(value, dict) and isinstance(value.get('interaction_exclusions'), list):
                exclusions = value['interaction_exclusions']
        journal = {
            'version': 1,
            'build': str(build.resolve()),
            'project_root': str(project_root.resolve()),
            'started_at': now(),
            'checked_at': None,
            'completed_at': None,
            'quote': quote,
            'discard_set': discard,
            'orphans': orphan_set(build),
            'scope_sha256_at_begin': (sha256(build / 'scope.md')
                                      if (build / 'scope.md').is_file() else None),
            'has_render_audit': bool(state.get('has_render_audit')),
            'render_audit_skip_reason': None,
            'images_before': images_listing(project_root),
            'interaction_exclusions': exclusions,
            'evidence_debt_before': state.get('evidence_debt'),
            'copied_inputs': sorted(copied),
            # 판독 실패는 «막지 않되 지우지도 않는다» — check·commit 이 매번 표면화한다.
            'unreadable': errors,
        }
        dump_json(staging / JOURNAL, journal)
        state['evidence_debt'] = {
            'decision': 'observe',
            'at': journal['started_at'],
            'quote': quote,
            'reason': '재동결 = 조작 상태 전량 재수집',
            'cases': current_debt_cases(build),
        }
        write_state(build, state)
    except Exception:
        # journal 없는 staging 은 어느 서브커맨드도 치우지 못한다 — 만들다 실패하면 지운다.
        shutil.rmtree(staging, ignore_errors=True)
        raise
    print(f'[refreeze] staging {staging.name} · 폐기 {len(discard)}건 · '
          f'고아 {len(journal["orphans"])}건(지우지 않음)'
          + (f' · 판독 실패 {len(errors)}건(폐기 집합 불완전 — journal 에 기록)' if errors else ''))
    return 0


# --- check -----------------------------------------------------------------

def cmd_check(build: Path, staging: Path | None, skip_reason: str | None,
              observation_skip: str | None = None) -> int:
    staging = _single(build, STAGING_PREFIX, staging)
    if staging is None:
        raise RefreezeError('staging 이 없다 — begin 을 먼저 실행한다')
    journal_path = staging / JOURNAL
    if not journal_path.is_file():
        raise RefreezeError(f'{staging.name} 에 {JOURNAL} 이 없다 — abort 로 치운 뒤 다시 시작한다')
    journal = load_json(journal_path)
    if skip_reason is not None:
        if skip_reason not in SKIP_REASONS:
            raise RefreezeError('렌더 실측 생략 사유는 enum 이다: ' + ' · '.join(SKIP_REASONS))
        journal['has_render_audit'] = False
        journal['render_audit_skip_reason'] = skip_reason
        dump_json(journal_path, journal)
    if observation_skip is not None:
        if observation_skip not in SKIP_REASONS:
            raise RefreezeError('조작 상태 관찰 생략 사유는 enum 이다: ' + ' · '.join(SKIP_REASONS))
        journal['observation_skip_reason'] = observation_skip
        dump_json(journal_path, journal)
    missing: list[str] = []
    design_ref = staging / 'design-ref'
    if not design_ref.is_dir() or not any(design_ref.rglob('*')):
        missing.append('design-ref/')
    for name in REQUIRED_STAGING:
        if not (staging / name).is_file():
            missing.append(name)
    if journal.get('has_render_audit') and not (staging / 'render-audit.json').is_file():
        missing.append('render-audit.json')
    errors: list[str] = []
    issues = missing + pointer_health(staging)
    observation_issues = _archive_observation_issues(staging)
    if observation_issues and journal.get('observation_skip_reason'):
        # 브라우저 채널이 없으면 이 축은 어떤 행동으로도 못 닫힌다 — 렌더 실측 축과 같은 등급의
        # 명시 사유로 통과시키고, «무엇이 미검증인지» 는 journal·build-state 에 남긴다.
        for issue in observation_issues:
            print(f'[refreeze] 조작 상태 관찰 생략({journal["observation_skip_reason"]}): {issue}')
    else:
        issues.extend(observation_issues)
    covered = set(journal.get('discard_set') or ())
    live = [rel for rel in evidence_pointers(build, errors) if (build / rel).is_file()]
    for issue in errors:
        print(f'[refreeze] 경고 — 증거 문서를 읽을 수 없다(차단하지 않는다): {issue}')
    for issue in journal.get('unreadable') or ():
        print(f'[refreeze] 경고 — begin 시점 판독 실패가 기록돼 있다: {issue}')
    uncovered = sorted(set(live) - covered - preserved_set(build))
    if uncovered and (journal.get('unreadable') or errors):
        # begin 때 증거를 못 읽어 폐기 집합이 불완전했던 것뿐이다. 지금은 읽히니 **보정한다** —
        # 여기서 막으면 벽이 begin 에서 check 로 한 칸 밀린 것일 뿐이다(불변식 I).
        journal['discard_set'] = sorted(covered | set(uncovered))
        journal['discard_amended'] = uncovered
        dump_json(journal_path, journal)
        for rel in uncovered:
            print(f'[refreeze] 폐기 집합을 보정했다(begin 시점 판독 실패분): {rel}')
    else:
        issues.extend(f'폐기 집합 자기 검사: 포인터가 빠졌다 ({rel})' for rel in uncovered)
    if issues:
        for issue in issues:
            print(f'[refreeze] {issue}')
        return 3
    if not journal.get('has_render_audit') and journal.get('render_audit_skip_reason') is None:
        # 상속된 false 를 그대로 통과시키면 렌더 실측 축이 사유 없이 영구 침묵한다(§4.1 «유일한 주체»).
        print('[refreeze] 렌더 실측이 이 빌드에서 꺼져 있는데 사유 기록이 없다 — '
              'staging 에 render-audit.json 을 수집하거나 --render-audit-skipped <사유> 로 이번 결정을 남긴다')
        return 3
    journal['checked_at'] = now()
    dump_json(journal_path, journal)
    print(f'[refreeze] staging 완전 · 폐기 {len(covered)}건 · '
          f'고아 {len(journal.get("orphans") or ())}건')
    return 0


def _archive_observation_issues(staging: Path) -> list[str]:
    """archive 원본이면 case 마다 v2 조작 상태 관찰이 있어야 한다."""
    manifest = staging / 'source-manifest.json'
    if not manifest.is_file():
        return []
    try:
        value = load_json(manifest)
    except (OSError, ValueError):
        return []
    if not isinstance(value, dict) or value.get('collection') != 'archive':
        return []
    spec_path = staging / 'design-input.json'
    if not spec_path.is_file():
        return []
    spec = load_json(spec_path)
    issues: list[str] = []
    for case in spec.get('cases') if isinstance(spec.get('cases'), list) else []:
        label = case.get('id')
        rels = pointer_paths(staging, case.get('source_observation'))
        if not rels or not (staging / rels[0]).is_file():
            issues.append(f'{label}: 관찰 문서가 없다')
            continue
        document = load_json(staging / rels[0])
        if not isinstance(document, dict) or document.get('version') != 2 \
                or 'interactions' not in document:
            issues.append(f'{label}: 조작 상태 관찰(v2)이 없다')
    return issues


# --- commit ----------------------------------------------------------------

def _staging_payload(staging: Path) -> list[str]:
    return sorted(item.relative_to(staging).as_posix()
                  for item in staging.rglob('*')
                  if item.is_file() and item.name not in BOOKKEEPING)


def _move(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dst))


def cmd_commit(build: Path, staging: Path | None, resume: bool, stop_after: str | None) -> int:
    staging = _single(build, STAGING_PREFIX, staging)
    prev = _single(build, PREV_PREFIX)
    if prev is not None and not resume:
        raise RefreezeError(f'교체가 중단된 상태다({prev.name}) — commit --resume 또는 abort')
    if staging is None and prev is None:
        raise RefreezeError('staging 이 없다 — begin 을 먼저 실행한다')
    journal_path = (staging / JOURNAL) if staging else (prev / JOURNAL)
    if not journal_path.is_file():
        raise RefreezeError(f'{JOURNAL} 이 없다 — abort 로 치운 뒤 다시 시작한다')
    journal = load_json(journal_path)
    project_root = Path(journal['project_root'])

    if prev is None:
        if not journal.get('checked_at'):
            raise RefreezeError('check 를 통과하지 않았다 — 전량 폐기 전에 staging 완전성을 먼저 본다')
        scope = build / 'scope.md'
        expected = journal.get('scope_sha256_at_begin')
        if expected is not None and (not scope.is_file() or sha256(scope) != expected):
            raise RefreezeError('live scope.md 가 재동결 중에 바뀌었다 — staging 사본이 정본이므로 '
                                '교체하면 그 줄이 조용히 사라진다. live 변경을 staging 으로 옮긴 뒤 다시 실행한다')
        prev = build / f'{PREV_PREFIX}{time.strftime("%Y%m%d-%H%M%S")}'
        prev.mkdir()
        shutil.copy2(journal_path, prev / JOURNAL)
        dump_json(prev / PLAN, {
            'version': 1, 'phase': 'planned', 'created_at': now(),
            'staging': staging.name, 'prev': prev.name,
            'discard': list(journal.get('discard_set') or ()),
            'install': _staging_payload(staging),
        })
    plan = load_json(prev / PLAN)
    staging = staging or (build / plan['staging'])

    if plan['phase'] == 'done':  # _finish 도중 중단 — 남은 정리만 한다.
        _cleanup(staging, prev)
        print('[refreeze] 교체 완료(정리만 이어서 했다)')
        return 0

    for phase in PHASES[PHASES.index(plan['phase']) + 1:]:
        if phase == 'discarded':
            for rel in plan['discard']:
                src, dst = build / rel, prev / rel
                if src.is_file():
                    _move(src, dst)
                elif not dst.is_file():
                    raise RefreezeError(f'폐기 대상이 live 에도 _prev 에도 없다 ({rel})')
        elif phase == 'installed':
            for rel in plan['install']:
                src, dst = staging / rel, build / rel
                if src.is_file():
                    if dst.is_file():
                        # 폐기 집합 밖(보존·고아)의 동명 파일 — 먼저 _prev 로 피신시켜야 되감을 수 있다.
                        # 이미 _prev 에 원본이 있으면 그것이 진짜다 — 덮지 않고 live 쪽만 버린다.
                        if (prev / rel).exists():
                            dst.unlink()
                        else:
                            _move(dst, prev / rel)
                    _move(src, dst)
                elif not dst.is_file():
                    raise RefreezeError(f'설치 대상이 staging 에도 live 에도 없다 ({rel})')
        elif phase == 'verified':
            ok, detail = verify_inputs(build, project_root)
            if not ok:
                _rewind(build, staging, prev, journal, project_root)
                print(f'[refreeze] 교체 후 검증 실패 — 되감았다\n{detail}')
                return 3
        elif phase == 'done':
            _finish(build, staging, prev, journal)
            print('[refreeze] 교체 완료')
            return 0
        plan['phase'] = phase
        dump_json(prev / PLAN, plan)
        if stop_after == phase:
            print(f'[refreeze] {phase} 직후 중단 — commit --resume 으로 이어간다')
            return 3
    raise RefreezeError('교체 단계가 done 에 이르지 못했다')


def _rewind(build: Path, staging: Path, prev: Path, journal: dict, project_root: Path) -> None:
    """phase에 의존하지 않고 되감는다 — 단계 도중 중단돼도 원본이 사라지지 않게.

    ① live 에 있고 staging 에 없는 «설치분»을 staging 으로 돌려보낸다
    ② `_prev` 에 실제로 들어 있는 것을 전부 live 로 되돌린다(폐기분 + 덮어쓰기 피신분)
    ③ 이미지 차집합과 `evidence_debt` 를 원상 복구한다
    """
    plan_path = prev / PLAN
    install = []
    if plan_path.is_file():
        try:
            install = list(load_json(plan_path).get('install') or ())
        except (OSError, ValueError):
            install = []
    if staging.is_dir():
        for rel in install:
            live, back = build / rel, staging / rel
            if live.is_file() and not back.is_file():
                _move(live, back)
    for item in sorted(prev.rglob('*'), reverse=True):
        if not item.is_file() or item.name in BOOKKEEPING:
            continue
        _move(item, build / item.relative_to(prev))
    _restore_images(project_root, journal)
    _restore_debt(build, journal)
    shutil.rmtree(prev, ignore_errors=True)


def _restore_images(project_root: Path, journal: dict) -> None:
    before = set(journal.get('images_before') or ())
    for rel in images_listing(project_root):
        if rel not in before:
            (project_root / rel).unlink(missing_ok=True)


def _restore_debt(build: Path, journal: dict) -> None:
    state = read_state(build)
    before = journal.get('evidence_debt_before')
    if before is None:
        state.pop('evidence_debt', None)
    else:
        state['evidence_debt'] = before
    write_state(build, state)


def _preserve(folder: Path, why: str) -> None:
    """지우기 직전에 한 세대만 복사해 둔다 — `_discarded-<ts>/`.

    **개명이 아니라 복사다.** `_prev-` 는 되감기 저장소이면서 «commit 진행 중» 표식을 겸하므로
    (`cmd_commit` 의 `_single(build, PREV_PREFIX)`), 이름을 바꾸면 표식이 사라져 재개가 완료된
    재동결을 새 교체로 오인하고 방금 설치된 live 산출물을 다시 폐기한다(실측으로 재현됐다).
    복사는 `_prev` 의 생성·소멸 시점과 의미를 전혀 건드리지 않는다.

    백업은 차단 사유가 아니다 — 실패하면 경고만 내고 정리를 계속한다."""
    if not folder.is_dir():
        return
    stamp = time.strftime('%Y%m%d-%H%M%S')
    target = folder.parent / f'{DISCARDED_PREFIX}{stamp}'
    serial = 2
    while target.exists():
        target = folder.parent / f'{DISCARDED_PREFIX}{stamp}-{serial}'
        serial += 1
    try:
        shutil.copytree(folder, target)
    except OSError as error:
        shutil.rmtree(target, ignore_errors=True)   # 부분본을 완전본처럼 남기지 않는다
        print(f'[refreeze] 폐기분 백업 실패(정리는 계속한다): {folder.name} — {error}')
        return
    print(f'[refreeze] 폐기분을 {target.name}/ 에 한 세대 남겼다 ({why} · 확인 뒤 직접 지운다)')


def _cleanup(staging: Path, prev: Path) -> None:
    _preserve(prev, '재동결 완료')
    shutil.rmtree(staging, ignore_errors=True)
    shutil.rmtree(prev, ignore_errors=True)


def _unverified(journal: dict) -> dict:
    """이번 재동결이 «막지 않고 넘어간» 것들 — 벽을 없앤 자리에는 표면이 있어야 한다.

    벽만 걷어내고 기록을 어디에도 남기지 않으면 «열린 길이 무엇이 미검증인지 지운다»
    (불변식 II 위반). journal 은 완료와 함께 `_discarded-` 로 들어가므로 build-state 로 승격한다."""
    facts: dict = {}
    if journal.get('unreadable'):
        facts['unreadable'] = list(journal['unreadable'])
    if journal.get('discard_amended'):
        facts['discard_amended'] = list(journal['discard_amended'])
    if journal.get('observation_skip_reason'):
        facts['observation_skipped'] = journal['observation_skip_reason']
    if journal.get('render_audit_skip_reason'):
        facts['render_audit_skipped'] = journal['render_audit_skip_reason']
    return facts


def _finish(build: Path, staging: Path, prev: Path, journal: dict) -> None:
    state = read_state(build)
    facts = _unverified(journal)
    if facts:
        facts['at'] = now()
        state['refreeze_unverified'] = facts
        print('[refreeze] 이번 재동결에서 막지 않고 넘어간 것 — build-state.refreeze_unverified 에 남긴다:')
        for key, value in sorted(facts.items()):
            if key != 'at':
                print(f'  · {key}: {value}')
    else:
        state.pop('refreeze_unverified', None)
    if state.get('g2_approved') is True or state.get('implementation_visual') == 'verified':
        state['implementation_visual'] = 'pending'
    state['has_render_audit'] = bool(journal.get('has_render_audit'))
    if current_debt_cases(build) == 0:
        state.pop('evidence_debt', None)
    write_state(build, state)
    journal['completed_at'] = now()
    dump_json(prev / JOURNAL, journal)
    plan_path = prev / PLAN
    if plan_path.is_file():
        plan = load_json(plan_path)
        plan['phase'] = 'done'
        dump_json(plan_path, plan)
    _cleanup(staging, prev)


# --- abort -----------------------------------------------------------------

def cmd_abort(build: Path, staging: Path | None) -> int:
    staging = _single(build, STAGING_PREFIX, staging)
    prev = _single(build, PREV_PREFIX)
    journal_path = next((p for p in ((staging / JOURNAL) if staging else None,
                                     (prev / JOURNAL) if prev else None)
                         if p is not None and p.is_file()), None)
    if journal_path is None:
        if staging is None and prev is None:
            raise RefreezeError('되돌릴 재동결 상태가 없다')
        # journal 을 만들다 실패한 껍데기 — 지워야 hook·backstop 의 영구 BLOCKER가 풀린다.
        for leftover in (staging, prev):
            if leftover is not None:
                _preserve(leftover, 'journal 없는 잔존물 정리')
                shutil.rmtree(leftover, ignore_errors=True)
        print('[refreeze] journal 없는 잔존물을 치웠다 — live 빌드 폴더와 이미지는 손대지 않았다')
        return 0
    journal = load_json(journal_path)
    if journal.get('completed_at'):
        raise RefreezeError('이미 완료된 재동결이다 — abort 로 되돌리지 않는다')
    project_root = Path(journal['project_root'])
    if prev is not None:
        _rewind(build, staging or (build / load_json(prev / PLAN)['staging']), prev,
                journal, project_root)
    else:
        _restore_images(project_root, journal)
        _restore_debt(build, journal)
    if staging is not None:
        # staging 은 백업이 아니라 **재동결 산출물이 쌓이는 자리**다 — `cmd_begin` 이 넣는 것은
        # `INPUT_GLOBS` 뿐이지만 `cmd_check` 는 `REQUIRED_STAGING`·`design-ref/`·관찰 문서를
        # 여기서 찾는다. 그리고 `_rewind` 는 되감으면서 설치분을 여기로 되돌려 놓는다.
        # 그래서 이 자리가 한 번에 가장 많이 버리는 자리인데, 완료 폐기(`_cleanup`)와
        # journal 없는 잔존물은 보존하면서 여기만 보존하지 않던 것이 비대칭이었다.
        _preserve(staging, '재동결 중단')
        shutil.rmtree(staging, ignore_errors=True)
    print('[refreeze] 되돌렸다 — live 빌드 폴더와 이미지가 재동결 이전 상태다')
    return 0


# --- cli -------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='재동결 — 전량 폐기 후 재동결')
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('begin', 'check', 'commit', 'abort'):
        child = sub.add_parser(name)
        child.add_argument('--build', required=True, type=Path)
        if name == 'begin':
            child.add_argument('--project-root', required=True, type=Path)
            child.add_argument('--quote', required=True)
        else:
            child.add_argument('--staging', type=Path, default=None)
        if name == 'check':
            child.add_argument('--render-audit-skipped', default=None, metavar='REASON',
                               help='렌더 실측 생략 사유(enum): ' + ' · '.join(SKIP_REASONS))
            child.add_argument('--observation-skipped', default=None, metavar='REASON',
                               help='조작 상태 관찰 생략 사유(enum): ' + ' · '.join(SKIP_REASONS))
        if name == 'commit':
            child.add_argument('--resume', action='store_true')
            child.add_argument('--stop-after', choices=PHASES, default=None)
    args = parser.parse_args(argv)
    build = args.build.resolve()
    try:
        if args.command == 'begin':
            return cmd_begin(build, args.project_root.resolve(), args.quote)
        if args.command == 'check':
            return cmd_check(build, args.staging, args.render_audit_skipped,
                             args.observation_skipped)
        if args.command == 'commit':
            return cmd_commit(build, args.staging, args.resume, args.stop_after)
        return cmd_abort(build, args.staging)
    except RefreezeError as error:
        print(f'[refreeze] {error}')
        return 1
    except (OSError, ValueError) as error:
        print(f'[refreeze] {type(error).__name__}: {error}')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
