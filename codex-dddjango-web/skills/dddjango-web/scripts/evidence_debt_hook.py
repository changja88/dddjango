#!/usr/bin/env python3
"""dddjango-web 증거 부채 hook — SessionStart·UserPromptSubmit에서 시안 빌드의 조작 상태 증거 부채를 고지한다.

Coordinator가 어떤 경로(재동결만·조회만·구현)를 고르든 그보다 먼저 하네스가 이 스크립트를 실행한다.
판정은 evidence_debt.build_debt(구조 술어)가 하고, 여기서는 프로젝트 탐색·이벤트별 출력만 한다.

인자: `session-start` | `user-prompt`(기본). stdin: 하네스 JSON(`cwd`).
출력: 단일 JSON 문서 — `hookSpecificOutput.additionalContext`(모델 컨텍스트) + `systemMessage`(사용자 화면).
  session-start: `.dddjango-web/`가 있는 프로젝트면 빌드 0개여도 항상 «evidence hook active …» 1줄
  (이 줄이 없으면 hook 미작동) + 상태 줄(undecided·deferred·observing·error).
  user-prompt: 미결정(undecided) 빌드가 있을 때만. 결정된 빌드·판정 불가 빌드는 SessionStart에서만
  상태 줄을 낸다 — 매 프롬프트 같은 문장을 반복하지 않는다(재질문·무시 학습 방지).
exit는 항상 0(UserPromptSubmit exit 2는 프롬프트를 지운다). 어떤 예외도 삼킨다 — session-start에서는
오류를 additionalContext·systemMessage로 알리고, user-prompt에서는 stderr 1줄만 낸다.
"""
from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import json  # noqa: E402
import os  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from evidence_debt import BuildDebt, build_debt  # noqa: E402

ANCHOR = '[dddjango-web] evidence debt — '
ACTIVE = '[dddjango-web] evidence hook active — '
EVENTS = {'session-start': 'SessionStart', 'user-prompt': 'UserPromptSubmit'}
SKIP_DIRS = {'node_modules', '_history', '__pycache__', 'venv'}
QUOTE_CHARS = 20
DECISION_LINE = ('[dddjango-web] evidence debt: {count} undecided build(s). Record the user\'s decision in '
                 'build-state.json evidence_debt (ⓐ observe = re-collect chain: observe ≤90 min → independent '
                 'review → inputs → visual re-evidence → backstop · ⓑ defer = non-implementation runs only '
                 '(refreeze, inspection, reporting); implementation re-entry requires ⓐ) before any run on that '
                 'folder, including refreeze-only or scope-only runs. Quote the folder line verbatim in the banner.')


def _stdin_cwd() -> Path | None:
    try:
        if sys.stdin is None or sys.stdin.isatty():
            return None
        raw = sys.stdin.read()
    except (OSError, ValueError):
        return None
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except ValueError:
        return None
    cwd = payload.get('cwd') if isinstance(payload, dict) else None
    return Path(cwd) if isinstance(cwd, str) and cwd else None


def _candidates() -> list[Path]:
    env = os.environ.get('CLAUDE_PROJECT_DIR')
    found: list[Path] = []
    for value in (Path(env) if env else None, _stdin_cwd(), Path(os.getcwd())):
        try:
            if value is not None and value.is_dir():
                found.append(value)
        except OSError:
            continue
    return found


def _has_builds(directory: Path) -> bool:
    try:
        return (directory / '.dddjango-web').is_dir()
    except OSError:
        return False


def _subdirs(directory: Path) -> list[Path]:
    try:
        entries = list(os.scandir(directory))
    except OSError:
        return []
    out: list[Path] = []
    for entry in entries:
        try:
            if entry.is_dir(follow_symlinks=False) and not entry.name.startswith('.') and entry.name not in SKIP_DIRS:
                out.append(Path(entry.path))
        except OSError:
            continue
    return sorted(out)


def _project_roots(candidates: list[Path]) -> list[Path]:
    """후보마다 상위 탐색(첫 `.dddjango-web` 보유 조상) + 깊이 ≤2 하향 스캔 — 합집합."""
    roots: dict[Path, None] = {}
    for candidate in candidates:
        for ancestor in (candidate, *candidate.parents):
            if _has_builds(ancestor):
                roots.setdefault(ancestor.resolve(), None)
                break
        for depth1 in _subdirs(candidate):
            if _has_builds(depth1):
                roots.setdefault(depth1.resolve(), None)
            for depth2 in _subdirs(depth1):
                if _has_builds(depth2):
                    roots.setdefault(depth2.resolve(), None)
    return sorted(roots)


def _builds(root: Path) -> list[Path]:
    try:
        folders = sorted(p for p in (root / '.dddjango-web').iterdir() if p.is_dir())
    except OSError:
        return []
    return [p for p in folders if (p / 'design-input.json').is_file()]


def _quote(decision: dict) -> str:
    text = str(decision.get('quote', ''))
    return text if len(text) <= QUOTE_CHARS else text[:QUOTE_CHARS] + '…'


def _line(debt: BuildDebt) -> str:
    name = debt.build.name
    status = debt.status
    if status == 'error':
        return f'{ANCHOR}{name}: cannot evaluate ({debt.error})'
    if status == 'undecided':
        r = debt.reasons
        return (f'{ANCHOR}{name}: {debt.cases_debt}/{debt.cases_total} archive case(s) have no interaction-state '
                f'observation — static-only {r.get("static_only", 0)} · missing {r.get("missing", 0)} · '
                f'unreadable {r.get("unreadable", 0) + r.get("malformed", 0)}; dropdown/dialog/toggle states were '
                'never driven (not a file-format issue) · decision required before any run on this folder')
    at = str(debt.decision.get('at', '?')) if debt.decision else '?'
    if status == 'deferred':
        return f'{ANCHOR}{name}: deferred since {at} — "{_quote(debt.decision)}"'
    return f'{ANCHOR}{name}: observation pending since {at}'


def _emit(event: str, context: list[str], system: str) -> None:
    document = {'hookSpecificOutput': {'hookEventName': event, 'additionalContext': '\n'.join(context)},
                'systemMessage': system}
    sys.stdout.buffer.write((json.dumps(document, ensure_ascii=False) + '\n').encode('utf-8'))
    sys.stdout.buffer.flush()


def run(event: str) -> int:
    roots = _project_roots(_candidates())
    if not roots:
        return 0
    builds = [build for root in roots for build in _builds(root)]
    debts = [debt for debt in (build_debt(build) for build in builds) if debt is not None]
    by_status: dict[str, list[BuildDebt]] = {}
    for debt in debts:
        by_status.setdefault(debt.status, []).append(debt)
    undecided = by_status.get('undecided', [])
    deferred = by_status.get('deferred', [])
    observing = by_status.get('observing', [])
    errors = by_status.get('error', [])
    counts = f'undecided {len(undecided)} · deferred {len(deferred)} · observing {len(observing)}'
    if errors:
        counts += f' · error {len(errors)}'
    if event == 'SessionStart':
        active = f'{ACTIVE}scanned {len(builds)} build(s): {counts}'
        context = [active] + [_line(debt) for debt in undecided + deferred + observing + errors]
        if undecided:
            context.append(DECISION_LINE.format(count=len(undecided)))
        _emit(event, context, active)
        return 0
    if not undecided:
        return 0
    context = [_line(debt) for debt in undecided] + [DECISION_LINE.format(count=len(undecided))]
    _emit(event, context, f'[dddjango-web] evidence debt: {counts}')
    return 0


def main(argv: list[str]) -> int:
    event = EVENTS.get(argv[0] if argv else 'user-prompt', 'UserPromptSubmit')
    try:
        return run(event)
    except Exception as error:  # noqa: BLE001 — hook은 어떤 경우에도 프롬프트를 막지 않는다
        message = f'[dddjango-web] evidence hook error: {type(error).__name__}: {error}'
        sys.stderr.write(message + '\n')
        if event == 'SessionStart':
            try:
                _emit(event, [message], message)
            except Exception:  # noqa: BLE001
                pass
        return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
