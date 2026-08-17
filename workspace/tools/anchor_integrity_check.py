#!/usr/bin/env python3
"""스킬 § 앵커 무결성 검사 — observance hardening 1-A (메인테이너/빌드타임 — 런타임 게이트 아님).

배경: 웨이브 1 감사(2026-08-16)와 3렌즈 중재(2026-08-17)에서 «인용자는 있는데 코퍼스에 없는
§ 조항»(댕글링 앵커 — `architecture-ddd` §3.2 «판정 소유→구조 이주» 항-(2))과 houserules 의
SKILL/final 이중 §번호 공간 오독이 실증됐다. 해소되지 않는 앵커는 §번호를 불투명 토큰으로
훈련시켜 «실독 없는 §인용»의 코퍼스 층위 원인이 된다 — 이 검사가 그 부류를 결정적으로 탐지한다.
corpus_lint·spec_lint 와 같은 부류라 registry 밖이다.

검사 대상(인용자): dddjango/agents/*.md · dddjango/commands/*.md · dddjango/scripts/*.py ·
codex-dddjango/skills/dddjango*/SKILL.md · codex-dddjango/skills/dddjango/scripts/*.py
해소 코퍼스(정본): dddjango/skills/<skill>/{SKILL.md, references/final.md}
(codex `dddjango-` 접두 개명은 접두를 벗겨 정본으로 해소한다 — 미러는 byte-identical 이
corpus_mirror_sync 로 보장되므로 정본 해소가 곧 미러 해소다.)

앵커 문법 — 닫힌 목록(명세 §1-A · 문법 밖 § 표기는 «미해석»으로 보고해 미탐을 침묵시키지 않는다):
  ① 표준형        `skill-name` §N[.M]      (백틱 스킬명 + 밖의 §)
  ② 백틱 내장형    `skill-name §N[.M]`      (한 백틱 안)
  ③ 약칭형        houserules §N · cleancode §N (약칭 사전으로 해소)
  ④ 무스킬명형     final.md §N · 맨 §N       (같은 행의 직전 스킬 언급으로 귀속 — 못 찾으면
                   «맥락 미해소» 보고, 위반 아님: 명세 자체 절번호 등 정당한 비-스킬 §가 있다)
  ⑤ 하위 항·행 범위 «항-(2)»·«트리 22~32행» 동반 — §N 절 실재 + 동반 «제목»의 본문 실재를
                   검증한다(항·행 번호 자체는 검증 대상 밖 — 절·제목 검증으로 갈음)
  ⑥ codex 접두형   dddjango-architecture-ddd → architecture-ddd (①②의 스킬명 변형)

판정:
  OK          앵커가 그 스킬 문서에서 해소됨
  MISSING     스킬은 실재하나 §번호가 SKILL.md·references/final.md 어디에도 없음 → 위반
  AMBIGUOUS   이중 §공간 스킬(houserules)의 무접두 인용 중 «양쪽 공간에 다 있는 충돌 번호» → 위반
              (한쪽 전용 번호는 그쪽으로 해소 — 실질 모호만 잡는다)
  UNKNOWN     스킬명이 코퍼스에 없음 → 위반
  UNRESOLVED  ④의 맥락 미해소 — 보고만(위반 아님. 문법 밖 § 표기도 ④가 전수 수거하므로
              별도 UNPARSED 판정은 없다 — 미탐 침묵 없음)

self-test 가 매 호출에 선행한다(합성 red/green — «검사를 좁혀서 green» 순환 차단).
fail-CLOSED: 코퍼스 디렉터리 부재·self-test 실패는 exit 3.

exit: 0=clean(보고-전용 포함) · 2=위반(MISSING/AMBIGUOUS/UNKNOWN) · 3=구조 전제 깨짐 · 1=usage
사용: python3 workspace/tools/anchor_integrity_check.py [--root <저장소>] [--list-all]
"""
from __future__ import annotations

import argparse
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

EXIT_CLEAN = 0
EXIT_USAGE = 1
EXIT_VIOLATION = 2
EXIT_BROKEN = 3

ALIASES = {
    "houserules": "discipline-houserules",
    "cleancode": "discipline-cleancode",
}

# 스킬명 토큰: 소문자·하이픈, 지식 스킬 형태(architecture-/implementation-/discipline- 계열).
_SKILL_WORD = r"(?:dddjango[:-])?(?:architecture|implementation|discipline)-[a-z][a-z-]*"

# ① 표준형: `skill` §N  (스킬명 백틱 뒤 공백·조사 허용 범위 안의 §)
_RE_STANDARD = re.compile(rf"`({_SKILL_WORD})`[^`§\n]{{0,40}}?§([0-9]+(?:\.[0-9]+)*)")
# ② 백틱 내장형: `skill §N`
_RE_INLINE = re.compile(rf"`({_SKILL_WORD})\s+§([0-9]+(?:\.[0-9]+)*)`")
# ③ 약칭형: 백틱 없이 약칭 + §N (약칭 앞이 한글·공백 등 — 영문 낱말 연속이면 배제)
_RE_ALIAS = re.compile(
    r"(?<![A-Za-z`-])(" + "|".join(ALIASES)
    + r")\s+(?:(?:references/)?final\.md\s+|SKILL(?:\.md)?\s+)?§([0-9]+(?:\.[0-9]+)*)"
)
# 연쇄 번호: §3.2·§3.6 / §6.1/§6.2 — 스킬 귀속을 직전 매치에서 잇는다
_RE_CHAIN = re.compile(r"[·/,]\s*§([0-9]+(?:\.[0-9]+)*)")
# 모든 § 표기(커버리지 계산용)
_RE_ANY = re.compile(r"§[0-9]+(?:\.[0-9]+)*")
# ④ 문서 한정어(이중 공간 해소용): 앵커 앞 근방의 final.md / SKILL 표기
_RE_DOC_FINAL = re.compile(r"(?:references/)?final\.md")
_RE_DOC_SKILL = re.compile(r"SKILL(?:\.md)?")


@dataclass
class Anchor:
    file: str
    line_no: int
    skill: str | None  # 정규화된 스킬명(접두 제거) 또는 None(무스킬명)
    section: str
    doc_hint: str | None  # "final" | "skill" | None
    raw: str
    title: str | None = None  # 앵커 직후 «제목» — 있으면 본문 실재까지 검증
    verdict: str = ""
    note: str = ""


def _normalize_skill(name: str) -> str:
    name = name.removeprefix("dddjango:").removeprefix("dddjango-")
    return ALIASES.get(name, name)


def _load_corpus(root: Path) -> dict[str, dict[str, set[str]]]:
    """skill → {"skill": {절번호…}, "final": {절번호…}} · 헤딩 두 양식(`## N.`·`## §N`) 지원."""
    skills_dir = root / "dddjango" / "skills"
    if not skills_dir.is_dir():
        raise FileNotFoundError(f"코퍼스 없음: {skills_dir}")
    heading = re.compile(r"^#{2,4}\s*§?([0-9]+(?:\.[0-9]+)*)[.\s]")
    corpus: dict[str, dict[str, set[str]]] = {}
    for sk in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
        spaces: dict = {"skill": set(), "final": set(), "text": ""}
        sk_md = sk / "SKILL.md"
        fin_md = sk / "references" / "final.md"
        if sk_md.is_file():
            t = sk_md.read_text(encoding="utf-8")
            spaces["text"] += t
            for ln in t.splitlines():
                m = heading.match(ln)
                if m and ln.lstrip("#").lstrip().startswith("§"):
                    spaces["skill"].add(m.group(1))
        if fin_md.is_file():
            t = fin_md.read_text(encoding="utf-8")
            spaces["text"] += t
            for ln in t.splitlines():
                m = heading.match(ln)
                if m:
                    spaces["final"].add(m.group(1))
        corpus[sk.name] = spaces
    return corpus


def _section_resolves(section: str, space: set[str]) -> bool:
    """§3.2 는 «3.2 헤딩» 또는 «부모 3 헤딩+본문»으로 해소될 수 있다 — 헤딩 정확 일치 우선,
    하위 번호(§9.6 등 절 안의 소절 표기)는 부모 절 실재로 해소한다(하위 구조는 보고 소관)."""
    if section in space:
        return True
    parts = section.split(".")
    while len(parts) > 1:
        parts = parts[:-1]
        if ".".join(parts) in space:
            return True
    return False


def _doc_hint(text: str, start: int, from_pos: int | None = None) -> str | None:
    window = text[from_pos if from_pos is not None else max(0, start - 60) : start]
    last_final = None
    last_skill = None
    for m in _RE_DOC_FINAL.finditer(window):
        last_final = m.start()
    for m in _RE_DOC_SKILL.finditer(window):
        last_skill = m.start()
    if last_final is None and last_skill is None:
        return None
    return "final" if (last_skill is None or (last_final or -1) > last_skill) else "skill"


def _extract(file_label: str, text: str) -> tuple[list[Anchor], list[Anchor]]:
    """returns (anchors, unresolved) — 행 단위 스캔·연쇄 번호 승계."""
    anchors: list[Anchor] = []
    unresolved: list[Anchor] = []
    consumed_spans: list[tuple[int, int, int]] = []  # (line_no, s, e)
    lines = text.splitlines()
    for i, line in enumerate(lines, 1):
        matches: list[tuple[int, int, str, str]] = []  # (s, e, skill_raw, section)
        for rx in (_RE_INLINE, _RE_STANDARD, _RE_ALIAS):
            for m in rx.finditer(line):
                matches.append((m.start(), m.end(), m.group(1), m.group(2)))
        matches.sort()
        merged: list[tuple[int, int, str, str]] = []
        for cand in matches:
            if any(cand[0] >= p[0] and cand[1] <= p[1] for p in merged):
                continue  # ①이 ②의 내부와 겹치면 넓은 쪽만
            merged.append(cand)
        title_rx = re.compile(r"\s*«([^»]{2,40})»")
        for s, e, skill_raw, section in merged:
            hint = _doc_hint(line, e, from_pos=s)  # 한정어는 이름~§ 사이(gap)에만 실재
            tm = title_rx.match(line, e)
            anchors.append(Anchor(file_label, i, _normalize_skill(skill_raw), section, hint, line[s:e],
                                  tm.group(1) if tm else None))
            consumed_spans.append((i, s, e))
            # 연쇄: 매치 직후 이어지는 ·§N / /§N 을 같은 스킬로 승계
            pos = e
            while True:
                cm = _RE_CHAIN.match(line, pos)
                if not cm:
                    break
                anchors.append(
                    Anchor(file_label, i, _normalize_skill(skill_raw), cm.group(1), hint, line[s:cm.end()])
                )
                consumed_spans.append((i, cm.start(), cm.end()))
                pos = cm.end()
        # 커버리지: 소비 안 된 § 표기 → 같은 행 직전 스킬 언급으로 귀속 시도, 실패면 미해소
        for m in _RE_ANY.finditer(line):
            if any(ln == i and m.start() >= s and m.end() <= e for ln, s, e in consumed_spans):
                continue
            prior = None
            for pm in re.finditer(rf"`?({_SKILL_WORD})`?", line[: m.start()]):
                prior = pm
            if prior:
                hint = _doc_hint(line, m.start(), from_pos=prior.end())
                tm = re.compile(r"\s*«([^»]{2,40})»").match(line, m.end())
                anchors.append(
                    Anchor(file_label, i, _normalize_skill(prior.group(1)), m.group(0)[1:], hint,
                           f"{prior.group(1)} …{m.group(0)} (행내 귀속)",
                           tm.group(1) if tm else None)
                )
            else:
                unresolved.append(Anchor(file_label, i, None, m.group(0)[1:], None, line.strip()[:80]))
    return anchors, unresolved


def _judge(anchors: list[Anchor], corpus: dict[str, dict[str, set[str]]]) -> None:
    dual = {name for name, sp in corpus.items() if sp["skill"]}
    # 이중 공간 = SKILL.md 가 자체 §헤딩을 가진 스킬(실재: discipline-houserules)
    for a in anchors:
        assert a.skill is not None
        if a.skill not in corpus:
            a.verdict, a.note = "UNKNOWN", "코퍼스에 없는 스킬명"
            continue
        sp = corpus[a.skill]
        if a.skill in dual and a.doc_hint is None:
            in_final = _section_resolves(a.section, sp["final"])
            in_skill = _section_resolves(a.section, sp["skill"])
            if in_final and in_skill:  # 실질 충돌 번호만 모호 — 한쪽 전용 번호는 그쪽으로 해소
                a.verdict = "AMBIGUOUS"
                a.note = "이중 §공간 스킬의 충돌 번호 — 문서 접두(final.md §N / SKILL §N) 필요"
                continue
        if a.doc_hint == "final":
            ok = _section_resolves(a.section, sp["final"])
        elif a.doc_hint == "skill":
            ok = _section_resolves(a.section, sp["skill"])
        else:
            ok = _section_resolves(a.section, sp["final"]) or _section_resolves(a.section, sp["skill"])
        a.verdict = "OK" if ok else "MISSING"
        if not ok:
            a.note = "SKILL.md·references/final.md 어디에도 §%s 헤딩 없음" % a.section
        elif a.title and a.title not in sp.get("text", ""):
            a.verdict = "MISSING"
            a.note = "§%s 절은 실재하나 인용 제목 «%s» 이 코퍼스 본문에 없음(제목 댕글링)" % (a.section, a.title)


def _scan_targets(root: Path) -> list[Path]:
    targets: list[Path] = []
    targets += sorted((root / "dddjango" / "agents").glob("*.md"))
    targets += sorted((root / "dddjango" / "commands").glob("*.md"))
    targets += sorted((root / "dddjango" / "scripts").glob("*.py"))
    codex_skills = root / "codex-dddjango" / "skills"
    if codex_skills.is_dir():
        # 역할 스킬 + 오케스트레이터만 — 지식 스킬 SKILL.md 의 자기-§ 요약표는 대상 아님(명세 §1-A)
        roles = ("dddjango", "dddjango-coder", "dddjango-acceptance-tester",
                 "dddjango-design-architect", "dddjango-design-review-ddd",
                 "dddjango-design-review-api", "dddjango-design-review-db",
                 "dddjango-discipline-reviewer")
        for r in roles:
            p = codex_skills / r / "SKILL.md"
            if p.is_file():
                targets.append(p)
        targets += sorted((codex_skills / "dddjango" / "scripts").glob("*.py"))
    return targets


def _self_test() -> None:
    corpus = {
        "architecture-ddd": {"skill": set(), "final": {"3", "3.2", "3.6"},
                             "text": "### 3.2 엔티티\n판정 소유→구조 이주 항-(1) 항-(2) 본문"},
        "discipline-houserules": {"skill": {"1", "6"}, "final": {"0", "1", "4"}, "text": ""},
        "implementation-test": {"skill": set(), "final": {"7", "15"}, "text": ""},
    }
    cases = [  # (본문, 기대 verdict 시퀀스)
        ("근거 `architecture-ddd` §3.2·§3.6.", ["OK", "OK"]),                       # ①+연쇄 green
        ("근거 `architecture-ddd` §9.9 위반.", ["MISSING"]),                        # ① red
        ("근거 `implementation-test §7`.", ["OK"]),                                  # ② green
        ("houserules §1 근거.", ["AMBIGUOUS"]),                                     # ③ 충돌 번호 red
        ("houserules §6.1/§6.2 근거.", ["OK", "OK"]),                                # ③ 한쪽 전용 → 해소
        ("`discipline-houserules` `references/final.md` §0·§1 이 정본.", ["OK", "OK"]),  # ④한정 green
        ("`dddjango-architecture-ddd` §3.2 «판정 소유→구조 이주» 항-(2).", ["OK"]),  # ⑥+⑤ green
        ("`architecture-ddd` §3.2 «없는 제목 조항».", ["MISSING"]),                   # 제목 댕글링 red
        ("`architecture-nope` §1 근거.", ["UNKNOWN"]),                               # 미지 스킬 red
        ("houserules final.md §0 근거.", ["OK"]),                                    # ③+한정어 green
        ("`discipline-houserules` SKILL §1 규칙.", ["OK"]),                          # ①+한정어 green
    ]
    for text, expect in cases:
        anchors, _ = _extract("<self>", text)
        _judge(anchors, corpus)
        got = [a.verdict for a in anchors]
        if got != expect:
            raise AssertionError(f"self-test 실패: {text!r} → {got} (기대 {expect})")
    # 맥락 미해소 케이스
    anchors, unresolved = _extract("<self>", "명세 자체 절번호 §3.3 을 인용한다.")
    if anchors or len(unresolved) != 1:
        raise AssertionError("self-test 실패: 무스킬명 § 는 UNRESOLVED 보고여야 한다")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="스킬 § 앵커 무결성 검사")
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    ap.add_argument("--list-all", action="store_true", help="OK 앵커까지 전부 출력")
    try:
        args = ap.parse_args(argv)
    except SystemExit:
        return EXIT_USAGE
    try:
        _self_test()
        corpus = _load_corpus(args.root)
        targets = _scan_targets(args.root)
        if not targets:
            raise FileNotFoundError("스캔 대상 0 — 저장소 루트 확인")
    except (FileNotFoundError, AssertionError, OSError) as exc:
        print(f"[BROKEN] {exc}", file=sys.stderr)
        return EXIT_BROKEN

    all_anchors: list[Anchor] = []
    all_unresolved: list[Anchor] = []
    for t in targets:
        label = str(t.relative_to(args.root))
        anchors, unresolved = _extract(label, t.read_text(encoding="utf-8"))
        all_anchors += anchors
        all_unresolved += unresolved
    _judge(all_anchors, corpus)

    bad = [a for a in all_anchors if a.verdict in {"MISSING", "AMBIGUOUS", "UNKNOWN"}]
    ok_n = sum(1 for a in all_anchors if a.verdict == "OK")
    for a in bad:
        print(f"[{a.verdict}] {a.file}:{a.line_no} `{a.skill}` §{a.section} — {a.note}  ({a.raw[:70]})")
    for a in all_unresolved:
        print(f"[UNRESOLVED] {a.file}:{a.line_no} §{a.section} — 행내 스킬 귀속 실패(보고만): {a.raw}")
    if args.list_all:
        for a in all_anchors:
            if a.verdict == "OK":
                print(f"[OK] {a.file}:{a.line_no} `{a.skill}` §{a.section}")
    print(
        f"\n앵커 {len(all_anchors)}건: OK {ok_n} · 위반 {len(bad)} "
        f"(MISSING {sum(1 for a in bad if a.verdict=='MISSING')} · "
        f"AMBIGUOUS {sum(1 for a in bad if a.verdict=='AMBIGUOUS')} · "
        f"UNKNOWN {sum(1 for a in bad if a.verdict=='UNKNOWN')}) · "
        f"맥락 미해소(보고) {len(all_unresolved)}"
    )
    return EXIT_VIOLATION if bad else EXIT_CLEAN


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
