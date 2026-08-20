#!/usr/bin/env python3
"""두 런타임 Coordinator 절차의 «의미 미러» 대조 (T2-3 · 적대 리뷰 AN#12).

`corpus_mirror_sync` 는 `commands/*.md`·`SKILL.md` 를 **설계상 미러 면제**로 둔다(plugin-native
단일 파일). 그래서 Claude 쪽 절차만 고치고 Codex 쪽을 잊어도 **기계가 아무 말을 하지 않는다** —
같은 버전으로 배포되는 두 런타임 중 하나에만 처치가 들어간 플러그인이 나온다.

이 검사는 그 공백을 닫는다: 대조 대상 절의 본문을 **런타임 표기 차이만 정규화**해 대조하고,
남는 차이를 전부 보고한다. 행동 parity(같은 red 픽스처로 발화·예산·최종 게이트 비교)는 설치본
갱신이 선행하므로 T2-0b 몫이고, 여기서는 **문면 이탈**을 막는다.

exit 0 = 정합 / 2 = 이탈 / 1 = 재료 결손.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT: Path = Path(__file__).resolve().parents[2]
CLAUDE: Path = ROOT / "dddjango" / "commands" / "dddjango.md"
CODEX: Path = ROOT / "codex-dddjango" / "skills" / "dddjango" / "SKILL.md"

# 대조할 절 — (표시 이름, 시작 정규식, 끝 정규식)
SECTIONS: "tuple[tuple[str, str, str], ...]" = (
    ("step 6′ 재생성 루프", r"^6′\. \*\*재생성 루프", r"^7\. \*\*G2 배너\*\*"),
)

# 런타임 표기 차이 — 의미가 같고 표기만 다른 것만 정규화한다(내용 차이를 지우면 안 된다).
NORMALIZE: "tuple[tuple[str, str], ...]" = (
    (r"\$\{CLAUDE_PLUGIN_ROOT\}/scripts/", "<PLUGIN>/scripts/"),
    (r"\$\{SKILL_DIR\}/scripts/", "<PLUGIN>/scripts/"),   # codex 측 플러그인 루트 표기
    (r"`scripts/regen_core\.py`\(이 스킬 폴더 기준 — 실행 시 절대 경로로 편다\)",
     "`<PLUGIN>/scripts/regen_core.py`"),
    (r"`\$\{CLAUDE_PLUGIN_ROOT\}/scripts/regen_core\.py`", "`<PLUGIN>/scripts/regen_core.py`"),
    (r"dddjango:", "dddjango-"),          # 서브에이전트 지정 표기(claude `:` ↔ codex `-`)
    (r"AskUserQuestion", "게이트 질문 채널"),
    (r"`Bash`", "`네이티브 셸`"),
)


def _extract(text: str, start: str, end: str) -> "str | None":
    lines: "list[str]" = text.splitlines()
    s_re, e_re = re.compile(start), re.compile(end)
    begin: int = -1
    for i, line in enumerate(lines):
        if begin < 0 and s_re.match(line):
            begin = i
            continue
        if begin >= 0 and e_re.match(line):
            return "\n".join(lines[begin:i]).strip()
    return None


def _normalize(text: str) -> str:
    for pat, rep in NORMALIZE:
        text = re.sub(pat, rep, text)
    return re.sub(r"[ \t]+", " ", text).strip()


def main() -> int:
    if not CLAUDE.is_file() or not CODEX.is_file():
        print("재료 결손: 절차 문서 없음", file=sys.stderr)
        return 1
    a_text: str = CLAUDE.read_text(encoding="utf-8")
    b_text: str = CODEX.read_text(encoding="utf-8")
    problems: "list[str]" = []
    for name, start, end in SECTIONS:
        a = _extract(a_text, start, end)
        b = _extract(b_text, start, end)
        if a is None or b is None:
            problems.append(
                f"{name}: 절 부재 — claude={'있음' if a else '없음'} · "
                f"codex={'있음' if b else '없음'} (한 런타임에만 처치가 들어갔다)")
            continue
        na, nb = _normalize(a), _normalize(b)
        if na == nb:
            print(f"[parity] {name}: 정합 ({len(na)}자)")
            continue
        a_lines, b_lines = na.splitlines(), nb.splitlines()
        diff: "list[str]" = []
        for i in range(max(len(a_lines), len(b_lines))):
            x = a_lines[i] if i < len(a_lines) else "(없음)"
            y = b_lines[i] if i < len(b_lines) else "(없음)"
            if x != y:
                diff.append(f"    행 {i + 1}:\n      claude: {x[:160]}\n      codex : {y[:160]}")
        problems.append(f"{name}: 문면 이탈 {len(diff)}행\n" + "\n".join(diff[:5]))
    if problems:
        print(f"[parity] 이탈 {len(problems)}건 — 두 런타임이 같은 처치를 싣지 않는다", file=sys.stderr)
        for p in problems:
            print(f"  {p}", file=sys.stderr)
        return 2
    print(f"[parity] 대조 절 {len(SECTIONS)}종 전건 정합 — 두 런타임 의미 미러 유지")
    return 0


if __name__ == "__main__":
    sys.exit(main())
