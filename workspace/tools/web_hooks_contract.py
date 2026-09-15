#!/usr/bin/env python3
"""dddjango-web hooks.json 계약 — Claude·Codex 플러그인의 증거 부채 hook 배선을 대조한다.

두 hooks.json은 byte 미러가 아니다(플러그인 루트 변수·스크립트 경로가 런타임마다 다름) — 대신 이 도구가
이벤트 2종·matcher·command 문자열·timeout·스크립트 실재를 리터럴로 대조한다. verify-web이 실행한다.
`--self-test`는 tempdir 정상 fixture와 변이(명령 문자열 변경)의 validate 결과를 검사한다.
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

EVENTS = {'SessionStart': 'session-start', 'UserPromptSubmit': 'user-prompt'}
SESSION_MATCHER = 'startup|resume|clear|compact'
TARGETS = (
    ('dddjango-web/hooks/hooks.json', 'dddjango-web', '${CLAUDE_PLUGIN_ROOT}', 'scripts/evidence_debt_hook.py'),
    ('codex-dddjango-web/hooks/hooks.json', 'codex-dddjango-web', '${PLUGIN_ROOT}',
     'skills/dddjango-web/scripts/evidence_debt_hook.py'),
)


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    for rel, plugin, var, script in TARGETS:
        path = root / rel
        if not path.is_file():
            issues.append(f'{rel}: missing')
            continue
        try:
            doc = json.loads(path.read_text(encoding='utf-8'))
        except ValueError as error:
            issues.append(f'{rel}: invalid JSON ({error})')
            continue
        hooks = doc.get('hooks') if isinstance(doc, dict) else None
        if not isinstance(hooks, dict):
            issues.append(f'{rel}: hooks object required')
            continue
        if set(hooks) != set(EVENTS):
            issues.append(f'{rel}: events must be exactly {sorted(EVENTS)}')
        if not (root / plugin / script).is_file():
            issues.append(f'{rel}: script {script} missing under {plugin}/')
        for event, arg in EVENTS.items():
            groups = hooks.get(event)
            if not isinstance(groups, list) or len(groups) != 1 or not isinstance(groups[0], dict):
                issues.append(f'{rel}.{event}: exactly one matcher group required')
                continue
            group = groups[0]
            if event == 'SessionStart' and group.get('matcher') != SESSION_MATCHER:
                issues.append(f'{rel}.{event}: matcher must be {SESSION_MATCHER!r}')
            if event == 'UserPromptSubmit' and 'matcher' in group:
                issues.append(f'{rel}.{event}: matcher not allowed (fires on every prompt)')
            entries = group.get('hooks')
            if not isinstance(entries, list) or len(entries) != 1 or not isinstance(entries[0], dict):
                issues.append(f'{rel}.{event}: exactly one command hook required')
                continue
            entry = entries[0]
            expected = f'python3 "{var}/{script}" {arg}'
            if entry.get('type') != 'command' or entry.get('command') != expected:
                issues.append(f'{rel}.{event}: command must be {expected!r}, got {entry.get("command")!r}')
            timeout = entry.get('timeout')
            if not isinstance(timeout, int) or isinstance(timeout, bool) or not 1 <= timeout <= 30:
                issues.append(f'{rel}.{event}: integer timeout 1..30 required')
    return issues


def self_test(root: Path) -> int:
    with tempfile.TemporaryDirectory() as tmp:
        fake = Path(tmp)
        for rel, plugin, _var, script in TARGETS:
            (fake / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(root / rel, fake / rel)
            (fake / plugin / script).parent.mkdir(parents=True, exist_ok=True)
            (fake / plugin / script).write_text('# stub\n', encoding='utf-8')
        if validate(fake):
            print(f'[web-hooks] self-test FAIL: 정상 fixture에서 결함 {validate(fake)}', file=sys.stderr)
            return 1
        mutated = fake / TARGETS[1][0]
        doc = json.loads(mutated.read_text(encoding='utf-8'))
        doc['hooks']['UserPromptSubmit'][0]['hooks'][0]['command'] = 'python3 other.py'
        mutated.write_text(json.dumps(doc), encoding='utf-8')
        found = validate(fake)
        if len(found) != 1 or 'command must be' not in found[0]:
            print(f'[web-hooks] self-test FAIL: 변이 검출 기대 1건, 실제 {found}', file=sys.stderr)
            return 1
        (fake / TARGETS[0][1] / TARGETS[0][3]).unlink()
        if not any('script' in issue and 'missing' in issue for issue in validate(fake)):
            print('[web-hooks] self-test FAIL: 스크립트 부재 미검출', file=sys.stderr)
            return 1
    print('[web-hooks] self-test PASS')
    return 0


def main(argv: list[str]) -> int:
    root = Path(__file__).resolve().parents[2]
    if argv and argv[0] == '--self-test':
        return self_test(root)
    issues = validate(root)
    for issue in issues:
        print(f'[web-hooks] ERROR: {issue}', file=sys.stderr)
    if issues:
        return 1
    print('[web-hooks] PASS: Claude·Codex hooks.json 계약(이벤트 2종·command·timeout·스크립트 실재)')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
