#!/usr/bin/env python3
"""dddjango-web 재동결 계약 — 규범 편집의 «완전성»을 사람 대신 기계가 정의한다.

손으로 만든 편집 대상 목록은 두 번 샜다(설계 v3·v4). 이 도구는 목록 대신 불변식을 본다:
A 유보(defer)가 재동결을 허용하지 않는다 · B 폐기된 대조 체계의 잔존 0 ·
C `refreeze.py` 4 서브커맨드 실재 · D1 수집 인자의 빌드 자리표시자가 재동결 중 staging을
가리키도록 치환됐다 · D2 보존 대상 경로는 치환되지 않았다 · D3 `scope.md` 쓰기 지시가
대상 폴더를 수식한다 · D4 `<대상 폴더>` 정의가 «산출물 위치» 절에 있다.

verify-web이 실행한다. `--self-test`는 합성 입력으로 각 검사가 red/green을 내는지 자기 확인한다.
"""
from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

CLAUDE_COMMANDS = 'dddjango-web/commands/dddjango-web.md'
CODEX_SKILL = 'codex-dddjango-web/skills/dddjango-web/SKILL.md'
ACQUISITION = ('dddjango-web/skills/implementation-ui/references/design-acquisition.md',
               'codex-dddjango-web/skills/implementation-ui/references/design-acquisition.md')
GUIDES = ('dddjango-web/REQUEST_GUIDE.md', 'codex-dddjango-web/REQUEST_GUIDE.md')
HOOK_SCRIPTS = ('dddjango-web/scripts/evidence_debt_hook.py',
                'codex-dddjango-web/skills/dddjango-web/scripts/evidence_debt_hook.py')
REFREEZE_SCRIPTS = ('dddjango-web/scripts/refreeze.py',
                    'codex-dddjango-web/skills/dddjango-web/scripts/refreeze.py')

# A — «유보/defer 가 허용하는 것» 열거 안에 재동결이 들어 있으면 red.
# 줄 단위로는 못 잡는다 — 규범은 한 문단이 한 줄이고, hook 스크립트는 문자열이 여러 줄로 쪼개져 있다.
# 그래서 파일 전체를 한 줄로 펴서 «허용 열거 시작 어휘» 뒤 창 안에 재동결 어휘가 오는지 본다.
ALLOW_WINDOWS = (
    ('defer가 허용하는 것', '재동결', 140),
    ('defer =', 'refreeze', 80),
    ('defer =', '재동결', 80),
    ('defer는', '재동결', 60),
    ('"decision": "observe | defer"', '재동결', 400),
    ('유보는', '재동결', 60),
    ('유보(', '재동결', 60),
    ('유보 =', '재동결', 60),
)

# B — 폐기된 대조 체계의 잔존.
DEAD_TOKENS = ('--compare-build', 'compare-build', '--compare-out', '--carried',
               'compare_manifests', 'refreeze-diff', 'carried_from')
# 유일한 정당한 잔존 — refreeze.py는 남아 있는 `refreeze-diff.json`을 폐기 대상으로 «명명»해야 한다.
DEAD_ALLOWED = {('scripts/refreeze.py', 'refreeze-diff')}

# D — 폐기·교체 대상(치환 필요) / 보존 대상(치환 금지).
DISCARD_NAMES = ('design-ref', 'source-manifest.json', 'design-tokens.json', 'asset-manifest.json',
                 'screen-meta.json', 'render-audit.json', 'design-input.json', 'coverage-review.md',
                 'scope.md', 'captures')
# 이름이 화면마다 다른 폐기·교체 대상 — 설계 §2.1의 선언·예외 영역 입력.
DISCARD_PATTERNS = (r'[^/`\s]*-declared\.json', r'[^/`\s]*excluded-regions[^/`\s]*')
PRESERVED_NAMES = ('motion-notes.md', 'build-state.json', 'visual-check.md', 'design-spec.md',
                   'visual-evidence.json')
WRITE_VERBS = ('기록한다', '기록하며', '기록해', '적는다', '적어', '단다', '추가한다', '쓴다')
SUBCOMMANDS = ('cmd_begin', 'cmd_check', 'cmd_commit', 'cmd_abort')


def _read(root: Path, rel: str) -> str | None:
    path = root / rel
    return path.read_text(encoding='utf-8') if path.is_file() else None


def _lines(text: str) -> list[tuple[int, str]]:
    return list(enumerate(text.splitlines(), start=1))


def _flatten(text: str) -> str:
    """파이썬 문자열 이어붙이기와 줄바꿈을 지워 한 줄로 편다."""
    joined = re.sub(r"['\"]\s*\n\s*['\"]", '', text)
    return re.sub(r'\s+', ' ', joined)


def check_a(root: Path) -> list[str]:
    """유보가 재동결을 허용으로 열거하지 않는다."""
    issues: list[str] = []
    for rel in (CLAUDE_COMMANDS, CODEX_SKILL, *GUIDES, *HOOK_SCRIPTS):
        text = _read(root, rel)
        if text is None:
            issues.append(f'A {rel}: missing')
            continue
        flat = _flatten(text)
        for start, token, width in ALLOW_WINDOWS:
            for match in re.finditer(re.escape(start), flat):
                # 열거는 문장 경계(— · 마침표)에서 끝난다 — 그 뒤의 «재동결은 허용하지 않는다»는 열거가 아니다.
                window = re.split(r'—|\.\s', flat[match.end():match.end() + width])[0]
                if token in window:
                    issues.append(f'A {rel}: 유보 허용 열거에 재동결이 있다 '
                                  f'({start!r} … {window[:width].strip()!r})')
                    break
    return issues


def check_b(root: Path) -> list[str]:
    """폐기된 대조 체계의 잔존 0 — 플러그인 정본·미러 전체."""
    issues: list[str] = []
    for plugin in ('dddjango-web', 'codex-dddjango-web'):
        base = root / plugin
        if not base.is_dir():
            issues.append(f'B {plugin}: missing')
            continue
        for path in sorted(base.rglob('*')):
            if not path.is_file() or path.suffix not in ('.md', '.py', '.sh', '.json', '.mjs', '.js'):
                continue
            if '__pycache__' in path.parts:
                continue
            try:
                text = path.read_text(encoding='utf-8')
            except (OSError, UnicodeDecodeError):
                continue
            rel = path.relative_to(root).as_posix()
            for number, line in _lines(text):
                for token in DEAD_TOKENS:
                    if token not in line:
                        continue
                    if any(rel.endswith(tail) and token == allowed
                           for tail, allowed in DEAD_ALLOWED):
                        continue  # 허용 토큰이 같은 줄의 다른 폐기 토큰을 가리지 않게 한다
                    issues.append(f'B {rel}:{number}: 폐기된 어휘 {token!r} 잔존')
    return issues


def check_c(root: Path) -> list[str]:
    issues: list[str] = []
    for rel in REFREEZE_SCRIPTS:
        text = _read(root, rel)
        if text is None:
            issues.append(f'C {rel}: missing')
            continue
        for name in SUBCOMMANDS:
            if f'def {name}(' not in text:
                issues.append(f'C {rel}: {name} 없음')
    return issues


LOCATION_SECTION = '산출물 위치'


def _definition_lines(text: str) -> set[int]:
    """«산출물 위치» 절은 산출물이 어디 사는가의 정의다 — 치환 대상이 아니다."""
    inside, found = False, set()
    for number, line in _lines(text):
        if line.startswith('## '):
            inside = line[3:].strip().startswith(LOCATION_SECTION)
        if inside:
            found.add(number)
    return found


def _placeholder_issues(root: Path, rel: str, placeholder: str, names: tuple[str, ...],
                        code: str, message: str, *, check_build_arg: bool = True) -> list[str]:
    text = _read(root, rel)
    if text is None:
        return [f'{code} {rel}: missing']
    alternatives = [re.escape(n) for n in names]
    if names is DISCARD_NAMES:
        alternatives += list(DISCARD_PATTERNS)
    pattern = re.compile(re.escape(placeholder) + r'/(' + '|'.join(alternatives) + r')\b')
    build_arg = re.compile(r'--build\s+' + re.escape(placeholder))
    skip = _definition_lines(text)
    issues: list[str] = []
    for number, line in _lines(text):
        if number in skip:
            continue
        hit = pattern.search(line)
        if hit is None and check_build_arg:
            for candidate in build_arg.finditer(line):
                # `refreeze.py` 자신의 --build 는 live 빌드 폴더를 가리키는 것이 맞다.
                if 'refreeze.py' in line[max(0, candidate.start() - 60):candidate.start()]:
                    continue
                hit = candidate
                break
        if hit:
            issues.append(f'{code} {rel}:{number}: {message} ({hit.group(0)})')
    return issues


def check_d1(root: Path) -> list[str]:
    """수집·검사 인자의 빌드 자리표시자가 폐기·교체 대상을 가리키면 red — 치환 미완."""
    issues: list[str] = []
    for rel in (CLAUDE_COMMANDS, CODEX_SKILL):
        issues += _placeholder_issues(root, rel, '<산출물 폴더>', DISCARD_NAMES, 'D1',
                                      '재동결 중 staging을 가리켜야 한다 — <대상 폴더>로 바꾼다')
    for rel in ACQUISITION:
        issues += _placeholder_issues(root, rel, 'BUILD', DISCARD_NAMES, 'D1',
                                      '재동결 중 staging을 가리켜야 한다 — TARGET으로 바꾼다')
    return issues


def check_d2(root: Path) -> list[str]:
    """보존 대상은 치환하지 않는다 — staging에 쓰이면 교체 단계가 보존 규정을 위반한다."""
    issues: list[str] = []
    for rel in (CLAUDE_COMMANDS, CODEX_SKILL):
        issues += _placeholder_issues(root, rel, '<대상 폴더>', PRESERVED_NAMES, 'D2',
                                      '보존 대상은 치환 금지 — <산출물 폴더>로 되돌린다',
                                      check_build_arg=False)
    for rel in ACQUISITION:
        issues += _placeholder_issues(root, rel, 'TARGET', PRESERVED_NAMES, 'D2',
                                      '보존 대상은 치환 금지 — BUILD로 되돌린다',
                                      check_build_arg=False)
    return issues


REGION_START = '화면 디자인 출처 해소'
REGION_END = '준비 판정'
VERB_WINDOW = 60


def _collection_region(text: str) -> list[tuple[int, str]]:
    """재수집 구간(출처 해소 ~ 준비 판정)만 — 그 밖의 scope.md 쓰기는 재동결 전에 일어난다."""
    inside, rows = False, []
    for number, line in _lines(text):
        if REGION_START in line:
            inside = True
        elif inside and REGION_END in line:
            break
        if inside:
            rows.append((number, line))
    return rows


def check_d3(root: Path) -> list[str]:
    """재수집 구간의 `scope.md` 쓰기는 대상 폴더를 수식한다 — 무수식이면 규범이 live에 쓰라고 지시한다.

    문단 하나가 한 줄이라 «줄 안에 <대상 폴더>가 있으면 통과»는 거짓 음성을 낸다.
    출현마다 앞뒤 창에서 쓰기 동사를 찾고, 그때만 `<대상 폴더>/scope.md` 형태를 요구한다.
    """
    issues: list[str] = []
    for rel in (CLAUDE_COMMANDS, CODEX_SKILL):
        text = _read(root, rel)
        if text is None:
            issues.append(f'D3 {rel}: missing')
            continue
        for number, line in _collection_region(text):
            for match in re.finditer(r'scope\.md', line):
                window = line[max(0, match.start() - VERB_WINDOW):match.end() + VERB_WINDOW]
                if not any(verb in window for verb in WRITE_VERBS):
                    continue
                if line[max(0, match.start() - 20):match.start()].endswith('<대상 폴더>/'):
                    continue
                issues.append(f'D3 {rel}:{number}: scope.md 쓰기 지시에 <대상 폴더>/ 수식이 없다 '
                              f'(…{line[max(0, match.start() - 30):match.end() + 10]}…)')
    return issues


def check_anchors(root: Path) -> list[str]:
    """구간 앵커가 살아 있는지 — 사라지면 D1·D3가 빈 구간에서 조용히 green이 된다."""
    issues: list[str] = []
    for rel in (CLAUDE_COMMANDS, CODEX_SKILL):
        text = _read(root, rel)
        if text is None:
            continue
        if not _definition_lines(text):
            issues.append(f'D4 {rel}: «{LOCATION_SECTION}» 절을 찾지 못했다 — D1의 제외 구간이 공전한다')
        if not _collection_region(text):
            issues.append(f'D3 {rel}: «{REGION_START}» ~ «{REGION_END}» 구간을 찾지 못했다 — D3가 공전한다')
    return issues


def check_d4(root: Path) -> list[str]:
    """`<대상 폴더>` 정의가 «산출물 위치» 절에 있다."""
    issues: list[str] = []
    for rel in (CLAUDE_COMMANDS, CODEX_SKILL):
        text = _read(root, rel)
        if text is None:
            issues.append(f'D4 {rel}: missing')
            continue
        section = re.split(r'^## ', text, flags=re.MULTILINE)
        body = next((part for part in section if part.startswith('산출물 위치')), None)
        if body is None or '<대상 폴더>' not in body:
            issues.append(f'D4 {rel}: «산출물 위치» 절에 <대상 폴더> 정의가 없다')
    return issues


def validate(root: Path) -> list[str]:
    return (check_a(root) + check_b(root) + check_c(root)
            + check_d1(root) + check_d2(root) + check_d3(root) + check_d4(root)
            + check_anchors(root))


def _fixture(root: Path, *, clean: bool) -> None:
    commands = root / CLAUDE_COMMANDS
    commands.parent.mkdir(parents=True, exist_ok=True)
    skill = root / CODEX_SKILL
    skill.parent.mkdir(parents=True, exist_ok=True)
    holder = '<대상 폴더>' if clean else '<산출물 폴더>'
    defer = ('ⓑ defer가 허용하는 것 = 조회·보고 — 재동결은 허용하지 않는다\n' if clean
             else 'ⓑ defer가 허용하는 것 = 재동결·조회·보고\n')
    body = ('## 산출물 위치\n\n- `<산출물 폴더>/scope.md`\n'
            + ('- `<대상 폴더>` = 평시 `<산출물 폴더>` · 재동결 중 staging\n' if clean else '')
            + '\n## 절차\n\n' + defer
            + '5. **화면 디자인 출처 해소**\n'
            + f'`freeze_design.py --out {holder}/design-ref --manifest {holder}/source-manifest.json`\n'
            + f'실행 경계를 `{holder}/scope.md`에 기록한다.\n'
            + f'비의미 대상은 `{holder}/screen-declared.json`에 적어 --declared 로 준다.\n'
            + '6. **준비 판정**\n')
    commands.write_text(body, encoding='utf-8')
    skill.write_text(body, encoding='utf-8')
    for rel in (*GUIDES, *HOOK_SCRIPTS):
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('유보는 조회·보고만 허용한다\n' if clean
                        else '유보는 재동결·조회·보고를 허용한다\n', encoding='utf-8')
    for rel in ACQUISITION:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        target = 'TARGET' if clean else 'BUILD'
        path.write_text(f'`--out {target}/design-ref --manifest {target}/source-manifest.json`\n',
                        encoding='utf-8')
    for rel in REFREEZE_SCRIPTS:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        names = SUBCOMMANDS if clean else SUBCOMMANDS[:-1]   # C: 서브커맨드 결손
        body = ''.join(f'def {name}(build):\n    return 0\n\n' for name in names)
        if not clean:
            body += "# refreeze-diff 잔존 · --compare-build 잔존\n"   # B
        path.write_text(body, encoding='utf-8')
    if not clean:   # D2 — 보존 대상이 치환돼 있으면 red
        skill = root / CODEX_SKILL
        skill.write_text(skill.read_text(encoding='utf-8')
                         + '\n`<대상 폴더>/motion-notes.md` 를 갱신한다.\n', encoding='utf-8')


def self_test() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as raw:
        clean_root = Path(raw) / 'clean'
        _fixture(clean_root, clean=True)
        issues = validate(clean_root)
        if issues:
            failures.append(f'정상 fixture가 red: {issues}')
        dirty_root = Path(raw) / 'dirty'
        _fixture(dirty_root, clean=False)
        dirty_issues = validate(dirty_root)
        codes = {issue.split()[0] for issue in dirty_issues}
        for code in ('A', 'B', 'C', 'D1', 'D2', 'D3', 'D4'):
            if code not in codes:
                failures.append(f'변이 fixture에서 {code} 가 red를 내지 않았다')
        if not any('declared' in issue for issue in dirty_issues):
            failures.append('화면별 이름 폐기 대상(DISCARD_PATTERNS)이 D1에 잡히지 않았다')
        # 구간 앵커가 사라지면 D1·D3가 빈 구간에서 공전한다 — check_anchors 가 그것을 red 로 낸다.
        anchor_root = Path(raw) / 'anchorless'
        _fixture(anchor_root, clean=True)
        for rel in (CLAUDE_COMMANDS, CODEX_SKILL):
            path = anchor_root / rel
            path.write_text(path.read_text(encoding='utf-8')
                            .replace(f'## {LOCATION_SECTION}', '## 어딘가')
                            .replace(REGION_START, '출처'), encoding='utf-8')
        if not check_anchors(anchor_root):
            failures.append('구간 앵커가 사라져도 check_anchors 가 침묵했다')
    for failure in failures:
        print(f'[web-refreeze-contract] self-test {failure}')
    if failures:
        return 1
    print('[web-refreeze-contract] self-test green')
    return 0


def main(argv: list[str]) -> int:
    if '--self-test' in argv:
        return self_test()
    root = Path(__file__).resolve().parents[2]
    issues = validate(root)
    for issue in issues:
        print(f'[web-refreeze-contract] {issue}')
    if issues:
        print(f'[web-refreeze-contract] 위반 {len(issues)}건')
        return 1
    print('[web-refreeze-contract] 계약 green (A·B·C·D1~D4)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
