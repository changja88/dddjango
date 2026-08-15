#!/usr/bin/env python3
"""명세 정합성 검사 ①~⑧ + 규칙→소유자 매핑표 생성 (메인테이너/빌드타임 — 런타임 게이트 아님).

배경: 4번(명세 531규칙)의 완료 검증이 «손으로» 돌았고, 그 과정에서 #361(자리 누락)·#34(죽은
문면)가 손으로 걸렸다. 531규칙은 손으로 못 지킨다 — 5·6번 작업이 명세를 «편집»하는 동안
같은 부류의 드리프트를 결정적으로 탐지한다. corpus_mirror_sync.py 와 같은 부류다.

검사 여덟 (계획 2026-08-11-implementation-plan.md §3):
  ① 중복        정규화한 규칙 문면이 같은 쌍 (㉯ 가 71건을 손으로 걷었다)
  ② 끊긴 참조    «살아 있는 규칙 행» 안의 #N 이 죽은 번호를 가리킴
                 (걷어낸-목록 절은 대상 밖 — 거기는 죽은 번호를 «일부러» 적는 자리다.
                  <span> 정정 이력도 제외)
  ③ 트리 커버리지 140행 중 규칙 행(자리·문면)이 한 번도 안 가리키는 행 = 0 · 141행 이상 참조 금지
  ④ 카드 커버리지 결정 카드 57장(1~59, 19·23 없음) 중 인용 0건 = 0 · 없는 카드(D19·D23) 명시 인용 금지
  ⑤ 죽은 문면    걷어낸 낱말이 규칙 문면에 재등장 (deny-list 를 데이터로 인용하는 행은 allowlist)
  ⑥ 술어 정합    predicates.md 의 #N 전부 생존 · 등급 일치 · ast+ 는 «후보·물음» 필수
  ⑦ 등급 정합    판정·어겼을때 값이 넷 안 · 명세가 스스로 적은 집계표(판정×어겼을때·읽는 법)와 재실측 일치
  ⑧ 소유자 정합  rule-owner-map 이 명세와 1:1 · 등급→소유자 모양(§계획 1) · 작업 값 넷 안

fail-CLOSED: 파일 부재·앵커 실패·파싱 실패는 exit 3. 런타임 게이트의 fail-open 을 베끼지 않는다.

exit:  0 = clean        2 = 위반 (①~⑧ 어느 하나)
       3 = 구조 전제 깨짐 (파일 부재·표 앵커 실패 등 — 사람 개입 필요)
       1 = usage error

사용:
  python3 workspace/tools/spec_lint.py                     # ①~⑦ (+⑧: 매핑표가 있으면)
  python3 workspace/tools/spec_lint.py --emit-owner-map    # 매핑표 골격 생성(stdout 경고, 파일 기록)
  python3 workspace/tools/spec_lint.py --root /path/to/repo
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

EXIT_CLEAN = 0
EXIT_USAGE = 1
EXIT_VIOLATION = 2
EXIT_STRUCTURE = 3

SPEC_REL = "workspace/design/2026-08-08-tree-revision-spec.md"
PRED_REL = "workspace/design/2026-08-11-predicates.md"
TREE_REL = "docs/file_tree.html"
MAP_REL = "workspace/plan/2026-08-11-rule-owner-map.md"

GRADES = ("path", "ast", "ast+", "human")
WHENS = ("blocker", "검사기", "이행", "면제")
WORKS = ("재작성", "치환", "무변", "신설")
LIVE_CARDS = frozenset(set(range(1, 60)) - {19, 23})  # 57장
TREE_ROW_MAX = 140


class StructureError(Exception):
    """구조 전제 위반 → fail-closed(exit 3)."""


@dataclass(frozen=True)
class Rule:
    num: int
    text: str      # c1 규칙
    loc: str       # c2 자리
    grade: str     # c3 판정 (정규화)
    basis: str     # c4 근거
    when: str      # c6 어겼을 때 (정규화)
    line_no: int


# ──────────────────────────────────────────────────────────────── 파싱

def _norm_token(s: str) -> str:
    return s.replace("**", "").replace("`", "").strip()


def load_rules(spec_text: str) -> list[Rule]:
    """7컬럼 규칙 행만. 번호는 볼드 방어(int(c[0]) 금지 — «**629**» 사고)."""
    rules: list[Rule] = []
    for i, line in enumerate(spec_text.splitlines(), 1):
        m = re.match(r"^\|\s*\*{0,2}(\d+)\*{0,2}\s*\|", line)
        if not m:
            continue
        cols = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cols) != 7 or _norm_token(cols[-1]) not in WHENS:
            continue
        rules.append(
            Rule(
                num=int(m.group(1)),
                text=cols[1],
                loc=cols[2],
                grade=_norm_token(cols[3]),
                basis=_norm_token(cols[4]),
                when=_norm_token(cols[6]),
                line_no=i,
            )
        )
    if not rules:
        raise StructureError("규칙 행 0건 — 7컬럼 계약이 깨졌거나 파일이 비었다")
    nums = [r.num for r in rules]
    if len(nums) != len(set(nums)):
        dup = sorted({n for n in nums if nums.count(n) > 1})
        raise StructureError(f"규칙 번호 중복: {dup}")
    return rules


def load_tree_rows(html_text: str) -> dict[int, str]:
    """정본 HTML 에서 data-r → 리프 이름. 트리 행 번호의 유일한 출처."""
    pat = re.compile(
        r'<div data-r="(\d+)" class="tr[^"]*" style="--d:\d+">\s*<span class="path">(.*?)</span>',
        re.S,
    )
    rows: dict[int, str] = {}
    for m in pat.finditer(html_text):
        nm = re.search(r'<b class="nm">(.*?)</b>', m.group(2))
        name = re.sub(r"<[^>]+>", "", nm.group(1) if nm else m.group(2))
        rows[int(m.group(1))] = name
    if len(rows) != TREE_ROW_MAX:
        raise StructureError(f"트리 행 {len(rows)}개 — {TREE_ROW_MAX}개여야 한다(data-r 추출 실패?)")
    return rows


def _strip_spans(text: str) -> str:
    return re.sub(r"<span\b.*?</span>", "", text, flags=re.S)


def _expand_row_refs(text: str) -> set[int]:
    """「트리 97·98행」·「트리 105~111행」·「트리 13·42·44·49행」 → 행 번호 집합."""
    out: set[int] = set()
    for chunk in re.findall(r"트리\s*([0-9][0-9·~,\s]*)행", text):
        for tok in re.split(r"[·,\s]+", chunk):
            if not tok:
                continue
            if "~" in tok:
                a, b = tok.split("~", 1)
                if a.isdigit() and b.isdigit():
                    out.update(range(int(a), int(b) + 1))
            elif tok.isdigit():
                out.add(int(tok))
    return out


# ──────────────────────────────────────────────────────────────── 검사 ①~⑦

def check_duplicates(rules: list[Rule]) -> list[str]:
    seen: dict[str, int] = {}
    out = []
    for r in rules:
        key = re.sub(r"\s+", " ", _norm_token(r.text))
        if key in seen:
            out.append(f"① 중복 문면: #{seen[key]} ↔ #{r.num}")
        else:
            seen[key] = r.num
    return out


# 죽은 번호를 «일부러» 언급하는 자리 — 대체 소유자를 함께 적은 묘비 참조만 허용한다.
DANGLING_TOMBSTONES: frozenset[tuple[int, int]] = frozenset({
    (74, 22),  # 「그때 근거로 든 #22 는 5차가 걷어냈고 자리를 #488 이 잇는다」
})


def check_dangling_refs(rules: list[Rule]) -> list[str]:
    """살아 있는 규칙 «행 안»의 #N 만 본다 — 걷어낸-목록 절·span 은 죽은 번호를 일부러 적는 자리."""
    live = {r.num for r in rules}
    out = []
    for r in rules:
        body = _strip_spans(" | ".join((r.text, r.loc, r.basis)))
        for n in {int(x) for x in re.findall(r"#(\d+)\b", body)}:
            if n not in live and (r.num, n) not in DANGLING_TOMBSTONES:
                out.append(f"② 끊긴 참조: #{r.num} 행이 죽은 #{n} 을 가리킨다 (줄 {r.line_no})")
    return out


def check_tree_coverage(rules: list[Rule], tree: dict[int, str]) -> list[str]:
    covered: set[int] = set()
    out = []
    for r in rules:
        refs = _expand_row_refs(r.loc) | _expand_row_refs(r.text)
        over = {n for n in refs if n > TREE_ROW_MAX or n < 1}
        if over:
            out.append(f"③ 없는 트리 행 참조: #{r.num} → {sorted(over)}")
        covered |= refs - over
    missing = sorted(set(tree) - covered)
    for n in missing:
        out.append(f"③ 규칙 0건인 트리 행: {n} ({tree[n]})")
    return out


def check_card_coverage(spec_text: str) -> list[str]:
    out = []
    cited: set[int] = set()
    for m in re.finditer(r"\bD(\d{1,2})\s*~\s*D(\d{1,2})\b", spec_text):
        cited.update(range(int(m.group(1)), int(m.group(2)) + 1))
    singles = {int(x) for x in re.findall(r"\bD(\d{1,2})\b", spec_text)}
    cited |= singles
    for n in sorted(LIVE_CARDS - cited):
        out.append(f"④ 인용 0건인 결정 카드: D{n}")
    for n in sorted((singles - LIVE_CARDS) & set(range(1, 60))):
        out.append(f"④ 없는 카드를 명시 인용: D{n} (19·23 은 존재하지 않는다)")
    return out


# 걷어낸 낱말 — 재등장하면 죽은 문면. (allowlist: deny-list «데이터»로 그 낱말을 인용하는 행)
DEAD_PHRASES: dict[str, frozenset[int]] = {
    # 토큰(정규식) : 그 토큰을 데이터로 정당하게 인용하는 규칙 번호
    r"dto_(?:in|out)": frozenset(),
    r"(?<![a-z_])dto/": frozenset({201}),        # 「dto/ 겹을 만들지 않는다」 — 금지 규칙의 정당한 언급
    r"(?<![a-z_])feature\s*당": frozenset(),
    r"(?<![a-z_·])(?<!internal_)(?<!external_)broker_port\.py": frozenset(),
    r"query_repository": frozenset(),
    r"presentation_layer": frozenset({88}),      # 「presentation_layer/ 를 쓰지 않는다」
    r"infra_layer": frozenset({324}),            # 「infra_layer/…를 쓰지 않는다」
    r"published_service": frozenset({146}),      # 「published_service/ 칸을 만들지 않는다」
}


def check_dead_phrases(rules: list[Rule]) -> list[str]:
    out = []
    for r in rules:
        body = _strip_spans(r.text + " " + r.loc)
        for pat, allow in DEAD_PHRASES.items():
            if r.num in allow:
                continue
            if re.search(pat, body):
                out.append(f"⑤ 죽은 문면: #{r.num} 에 «{pat}» (줄 {r.line_no})")
    return out


def load_predicates(pred_text: str) -> dict[int, tuple[str, str]]:
    """predicates.md 의 | # | 바꿈 | 술어 | 행 → {번호: (등급, 술어)}."""
    out: dict[int, tuple[str, str]] = {}
    for line in pred_text.splitlines():
        m = re.match(r"^\|\s*\*{0,2}(\d+)\*{0,2}\s*\|", line)
        if not m:
            continue
        cols = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cols) != 3:
            continue
        grade = _norm_token(cols[1])
        if grade not in GRADES:
            continue
        out[int(m.group(1))] = (grade, cols[2])
    if not out:
        raise StructureError("술어 문서에서 항목 0건 — 3컬럼 계약이 깨졌다")
    return out


# 술어 문서의 묘비 참조 — 소유권 이관 기록만 허용한다.
PRED_TOMBSTONES: frozenset[tuple[int, int]] = frozenset({
    (181, 513),  # 멱등 물음의 소유자 — 「08-11 · C8 에 #513 에서 이관」
})


def check_predicates(rules: list[Rule], preds: dict[int, tuple[str, str]]) -> list[str]:
    out = []
    by_num = {r.num: r for r in rules}
    for n, (grade, pred) in sorted(preds.items()):
        if n not in by_num:
            out.append(f"⑥ 술어가 죽은 규칙을 가리킴: #{n}")
            continue
        if by_num[n].grade != grade:
            out.append(f"⑥ 등급 불일치: #{n} 명세={by_num[n].grade} ↔ 술어={grade}")
        body = _strip_spans(pred)
        for ref in {int(x) for x in re.findall(r"#(\d+)\b", body)}:
            if ref not in by_num and (n, ref) not in PRED_TOMBSTONES:
                out.append(f"⑥ 술어 #{n} 안의 끊긴 참조: #{ref}")
    for r in rules:
        if r.grade != "ast+":
            continue
        if r.num not in preds:
            out.append(f"⑥ ast+ 인데 술어 항목 없음: #{r.num}")
        else:
            pred = preds[r.num][1]
            for need in ("후보", "물음"):
                if need not in pred:
                    out.append(f"⑥ ast+ 술어에 «{need}» 없음: #{r.num}")
    return out


def check_grades(rules: list[Rule], spec_text: str) -> list[str]:
    out = []
    for r in rules:
        if r.grade not in GRADES:
            out.append(f"⑦ 판정 값 이탈: #{r.num} «{r.grade}»")
        if r.when not in WHENS:
            out.append(f"⑦ 어겼을때 값 이탈: #{r.num} «{r.when}»")
    # 명세가 스스로 적은 판정×어겼을때 표를 재실측과 대조
    anchor = spec_text.find("`판정` × `어겼을 때`")
    if anchor < 0:
        raise StructureError("판정×어겼을때 표 앵커 없음")
    stated: dict[str, list[int]] = {}
    for m in re.finditer(
        r"^\|\s*`(path|ast|ast\+|human)`\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|",
        spec_text[anchor : anchor + 2000],
        re.M,
    ):
        stated[m.group(1)] = [int(m.group(i)) for i in range(2, 6)]
    if set(stated) != set(GRADES):
        raise StructureError(f"판정×어겼을때 표 파싱 실패 — 얻은 행: {sorted(stated)}")
    for g in GRADES:
        actual = [sum(1 for r in rules if r.grade == g and r.when == w) for w in WHENS]
        if stated[g] != actual:
            out.append(f"⑦ 집계표 불일치: {g} 명세={stated[g]} ↔ 실측={actual}")
    # 읽는 법 세 덩어리
    def _stated(pat: str) -> int:
        m = re.search(pat, spec_text)
        if not m:
            raise StructureError(f"읽는 법 앵커 없음: {pat}")
        return int(m.group(1))

    pa = sum(1 for r in rules if r.grade in ("path", "ast") and r.when == "blocker")
    ap = sum(1 for r in rules if r.grade == "ast+" and r.when == "blocker")
    hu = sum(1 for r in rules if r.grade == "human" and r.when == "blocker")
    for label, got, want in (
        ("path+ast blocker", pa, _stated(r"`path`\+`ast`\s*의\s*blocker\s*\|\s*\*\*(\d+)\*\*")),
        ("ast+ blocker", ap, _stated(r"`ast\+`\s*의\s*blocker\s*\|\s*\*\*(\d+)\*\*")),
        ("human blocker", hu, _stated(r"`human`\s*의\s*blocker\s*\|\s*\*\*(\d+)\*\*")),
    ):
        if got != want:
            out.append(f"⑦ 읽는 법 불일치: {label} 명세={want} ↔ 실측={got}")
    m = re.search(r"`human`\s*의\s*blocker\s*\|\s*\*\*\d+\*\*\s*\|([^|]*)\|", spec_text)
    if m:
        listed = {int(x) for x in re.findall(r"#(\d+)", m.group(1))}
        actual_set = {r.num for r in rules if r.grade == "human" and r.when == "blocker"}
        if listed != actual_set:
            out.append(f"⑦ human blocker 목록 불일치: 명세={sorted(listed)} ↔ 실측={sorted(actual_set)}")
    return out


# ──────────────────────────────────────────────────────────────── ⑧ + 매핑표

def load_owner_map(map_text: str) -> dict[int, tuple[str, str, str, str]]:
    out: dict[int, tuple[str, str, str, str]] = {}
    for line in map_text.splitlines():
        m = re.match(r"^\|\s*\*{0,2}(\d+)\*{0,2}\s*\|", line)
        if not m:
            continue
        cols = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cols) != 6:
            continue
        n = int(m.group(1))
        if n in out:
            raise StructureError(f"매핑표 번호 중복: #{n}")
        out[n] = (_norm_token(cols[1]), cols[2].strip(), cols[3].strip(), _norm_token(cols[4]))
    if not out:
        raise StructureError("매핑표에서 행 0건 — 6컬럼 계약이 깨졌다")
    return out


def check_owner_map(rules: list[Rule], omap: dict[int, tuple[str, str, str, str]]) -> list[str]:
    out = []
    spec_nums = {r.num for r in rules}
    for n in sorted(spec_nums - set(omap)):
        out.append(f"⑧ 매핑표에 없는 규칙: #{n}")
    for n in sorted(set(omap) - spec_nums):
        out.append(f"⑧ 명세에 없는 매핑표 행: #{n}")
    by_num = {r.num: r for r in rules}
    for n, (grade, c_owner, d_owner, work) in sorted(omap.items()):
        r = by_num.get(n)
        if r is None:
            continue
        if grade != r.grade:
            out.append(f"⑧ 등급 불일치: #{n} 명세={r.grade} ↔ 매핑표={grade}")
        if work not in WORKS:
            out.append(f"⑧ 작업 값 이탈: #{n} «{work}»")
        has_c, has_d = c_owner not in ("", "—"), d_owner not in ("", "—")
        if r.grade in ("path", "ast") and not (has_c and not has_d):
            out.append(f"⑧ 모양 위반(path·ast→ⓒ 하나): #{n} ⓒ={c_owner!r} ⓓ={d_owner!r}")
        if r.grade == "ast+" and not (has_c and has_d):
            out.append(f"⑧ 모양 위반(ast+→ⓒ+ⓓ): #{n} ⓒ={c_owner!r} ⓓ={d_owner!r}")
        if r.grade == "human" and not (has_d and not has_c):
            out.append(f"⑧ 모양 위반(human→ⓓ 하나): #{n} ⓒ={c_owner!r} ⓓ={d_owner!r}")
    return out


# 트리 행 → ⓒ 검사기 (계획 §6 의 신설 목록 포함). 사람이 확정한 값 — 근거는 매핑표 머리말.
_R = "scripts/"
ROW_TO_CHECKER: dict[range, str] = {
    range(1, 2): _R + "check-layer-skeleton.py",
    range(2, 5): _R + "check-composition-root.py",
    range(5, 7): _R + "check-event-publish.py (신설)",
    range(7, 8): _R + "check-layer-skeleton.py",
    range(8, 10): _R + "check-composition-root.py",
    range(10, 11): _R + "check-error-centralization.py",
    range(11, 13): _R + "check-api-error-controller-contract.py",
    range(13, 16): _R + "check-usecase-dto-placement.py",
    range(16, 22): _R + "check-missable-entrance.py (신설)",
    range(22, 33): _R + "check-context-isolation.py",
    range(33, 35): _R + "check-missable-entrance.py (신설)",
    range(35, 38): _R + "check-event-publish.py (신설)",
    range(38, 45): _R + "check-usecase-dto-placement.py",
    range(45, 59): _R + "check-port-adapter-pairing.py (신설)",
    range(59, 68): _R + "check-domain-model.py (신설)",
    range(68, 69): _R + "check-transaction-boundary.py (신설)",
    range(69, 75): _R + "check-domain-model.py (신설)",
    range(75, 80): _R + "check-db-table.py",
    range(80, 82): _R + "check-mechanism-ownership.py",
    range(82, 89): _R + "check-naming.py (신설)",
    range(89, 97): _R + "check-port-adapter-pairing.py (신설)",
    range(97, 100): _R + "check-context-isolation.py",
    range(100, 105): _R + "check-port-adapter-pairing.py (신설)",
    range(105, 110): _R + "check-test-config.py",
    range(110, 112): _R + "check-port-adapter-pairing.py (신설)",
    range(112, 113): _R + "check-business-vocabulary.py (신설)",
    range(113, 120): _R + "check-broker-contract.py (신설)",
    range(120, 130): _R + "check-business-vocabulary.py (신설)",
    range(130, 135): _R + "check-business-vocabulary.py (신설)",
    range(135, 136): _R + "check-layer-skeleton.py",
    range(136, 138): _R + "check-composition-root.py",
    range(138, 139): _R + "check-broker-contract.py (신설)",
    range(139, 141): _R + "check-test-config.py",
}

# 자리에 트리 행이 없는 규칙(전역 제약·장 참조)의 키워드 라우팅 — 위에서 먼저 맞은 것이 이긴다.
KEYWORD_TO_CHECKER: tuple[tuple[str, str], ...] = (
    (r"검사기|check-|채택 신호|touched|fail-?open|exit|백스톱|이중 수용", "workspace/tools/checker_lint.py (신설)"),
    (r"타입|애너테이션|어노테이션|mypy", _R + "check-public-surface-annotation.py"),
    (r"트랜잭션|애그리거트 하나|save|remove|리포지토리.*쓰기", _R + "check-transaction-boundary.py (신설)"),
    (r"사실|이벤트|발행|브로커|구독|celery", _R + "check-event-publish.py (신설)"),
    (r"업무 어휘|#628|framework|pure/", _R + "check-business-vocabulary.py (신설)"),
    (r"이름|명명|낱말|약어|접미|접두|stem|토큰", _R + "check-naming.py (신설)"),
    (r"골격|제1원칙|칸을|트리.*개정|빈 채로|폐쇄", _R + "check-layer-skeleton.py"),
    (r"import|의존|안쪽|경계|관문|BC |ACL|OHS|open_host", _R + "check-context-isolation.py"),
    (r"schema|dto|_in|_out|result|command|query", _R + "check-usecase-dto-placement.py"),
    (r"포트|어댑터|상속|짝|1:1|fake", _R + "check-port-adapter-pairing.py (신설)"),
)

# 등급·라우팅으로 안 닿는 자리의 명시 확정 — «사람 확정» 컬럼의 실체(코드 리뷰로 관리한다).
RULE_OVERRIDES: dict[int, str] = {
    20: _R + "check-layer-skeleton.py",       # 하나뿐인 축 폴더 금지 — 술어 #20 이 코드 대상(평면·외래 칸 가족)
    21: _R + "check-layer-skeleton.py",       # 종류 하나면 파일로 — #20 과 같은 술어
    59: _R + "check-api-error-controller-contract.py",   # catch-all mapper 금지 — #15 의 현행 관할
    62: _R + "check-api-error-controller-contract.py",   # except Exception 금지
    67: _R + "check-usecase-dto-placement.py",           # 응용 DTO raise 금지 — 대상이 «타깃 코드»(자리 D30 의 «백스톱» 낱말이 checker_lint 로 오배정했었다 · #609 전례)
    63: _R + "check-openapi-error-declaration.py",      # response={status: ErrorSchema} 직접 선언·사후 변형 금지 — #5 의 현행 관할(#59·#62 전례)
    103: _R + "check-usecase-dto-placement.py",          # 입구의 값 객체 폭 — 경계 자료
    109: _R + "check-composition-root.py",               # register_<bc>_api 부작용 등록 금지 — registrar 관할
    129: _R + "check-synthetic-infra-exc.py",            # 예외 번역 전수 명시 매핑
    142: _R + "check-usecase-dto-placement.py",          # 요청 스키마가 도메인 객체 생성 금지
    169: _R + "check-naming.py (신설)",                   # 예외 계약 파일명 snake_case
    181: _R + "check-missable-entrance.py (신설)",        # 멱등 물음의 소유자 — 입구 관할
    195: _R + "check-transaction-boundary.py (신설)",     # 쓰기 유스케이스의 애그리거트 우회 금지
    196: _R + "check-usecase-dto-placement.py",          # Boundary·Presenter 를 응용에 안 넣음 — 공개 표면 관할
    197: _R + "check-transaction-boundary.py (신설)",     # 읽기 유스케이스는 UoW 안 받음
    200: _R + "check-transaction-boundary.py (신설)",     # after_commit 위임
    205: _R + "check-usecase-dto-placement.py",          # DTO 는 자기 유스케이스 폴더 안
    260: _R + "check-domain-model.py (신설)",             # entity 는 식별자를 가진다
    314: _R + "check-layer-skeleton.py",                 # specification/ 금지 — 외래 칸 반환 가족
    315: _R + "check-domain-model.py (신설)",             # Factory 는 애그리거트 폴더 안
    343: _R + "check-naming.py (신설)",                   # panel.py 훅 몸통 — admin 가족(#339~#348)과 동거(문면의 save_model 이 키워드 «save» 를 오발화했었다)
    347: _R + "check-context-isolation.py",              # feature/ 는 화면만 — 층 순수성 슬라이스 가족
    492: "workspace/tools/spec_lint.py",                 # 트리에 조건 금지 — 대상이 «정본·명세 문서»다
    564: _R + "check-event-publish.py (신설)",            # 진행표 금지 — 이벤트·순서 관할
    609: "workspace/tools/tree_mirror_check.py",         # 트리 데이터 소유 이행 — 대상이 «우리 문서 파이프라인»(#492 전례 · 키워드가 test-config 로 오배정했었다)
}

Q3_RULES = frozenset({526, 530, 563, 626})  # 유실·지연을 누가 못 견디나 — G1 설계 물음


def _assign_c(rule: Rule) -> str:
    if rule.num in RULE_OVERRIDES:
        return RULE_OVERRIDES[rule.num]
    if rule.when == "검사기":
        return "workspace/tools/checker_lint.py (신설)"
    rows = sorted(_expand_row_refs(rule.loc) | _expand_row_refs(rule.text))
    for n in rows:
        for rng, checker in ROW_TO_CHECKER.items():
            if n in rng:
                return checker
    hay = rule.text + " " + rule.loc
    for pat, checker in KEYWORD_TO_CHECKER:
        if re.search(pat, hay):
            return checker
    return ""


def _assign_d(rule: Rule) -> str:
    if rule.num in Q3_RULES:
        return "agents/design-architect.md"
    if rule.when in ("검사기", "이행"):
        return "메타(6번 지침·checker_lint)"
    return "agents/discipline-reviewer.md"


def emit_owner_map(rules: list[Rule], out_path: Path) -> list[str]:
    """매핑표 생성. 반환: 라우팅이 못 정한 규칙 경고(빈 ⓒ)."""
    warnings: list[str] = []
    lines = [
        "# 규칙 → 소유자 매핑표 (Phase 0 산출물)",
        "",
        "생성: `python3 workspace/tools/spec_lint.py --emit-owner-map` · 검증: 같은 도구 ⑧",
        "",
        "- **ⓐ 정본**(`skills/discipline-houserules/references/final.md`)은 **전 규칙**의 값 소유자라 컬럼에 없다. ⓑ SKILL.md 는 포인터만(값 0).",
        "- 모양: `path`·`ast`→ⓒ 하나 · `ast+`→ⓒ+ⓓ · `human`→ⓓ 하나. `어겼을 때=검사기`인 행의 ⓒ 는 검사기의 검사기(`workspace/tools/checker_lint.py`)다.",
        "- **작업**: `신설`=그 자리에 새로 쓴다(백스톱 실측 0 이라 대부분) · `재작성`=있는 로직을 다시 · `치환`=이름 갈이 · `무변`.",
        "- `#486~#492`(제1원칙)는 다른 모든 검사보다 먼저 도는 **별도 게이트**다(명세 «읽는 법»).",
        "",
        "| # | 판정 | ⓒ 검사기 | ⓓ 에이전트 | 작업 | 비고 |",
        "|---|---|---|---|---|---|",
    ]
    for r in sorted(rules, key=lambda x: x.num):
        c = _assign_c(r) if r.grade != "human" else "—"
        d = _assign_d(r) if r.grade in ("ast+", "human") else "—"
        if r.grade != "human" and not c:
            warnings.append(f"라우팅 실패(ⓒ 빈칸): #{r.num} 자리={r.loc[:40]}")
            c = "?"
        if "신설" in c:
            work = "신설"
        elif c.endswith(("check-layer-skeleton.py", "check-public-surface-annotation.py", "check-usecase-dto-placement.py")):
            work = "재작성"
        elif r.grade == "human":
            work = "치환"  # ⓓ 문서의 값 사본 → 포인터 갈이
        else:
            work = "신설"
        note = "제1원칙 선행 게이트" if 486 <= r.num <= 492 else ""
        if r.when in ("면제", "이행"):
            note = (note + " · " if note else "") + r.when
        lines.append(f"| {r.num} | {r.grade} | {c} | {d} | {work} | {note} |")
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return warnings


# ──────────────────────────────────────────────────────────────── main

def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--root", default=".", help="저장소 루트")
    ap.add_argument("--emit-owner-map", action="store_true")
    args = ap.parse_args(argv)
    root = Path(args.root)

    try:
        spec_p, pred_p, tree_p = root / SPEC_REL, root / PRED_REL, root / TREE_REL
        for p in (spec_p, pred_p, tree_p):
            if not p.is_file():
                raise StructureError(f"파일 부재: {p}")
        spec_text = spec_p.read_text(encoding="utf-8")
        rules = load_rules(spec_text)
        tree = load_tree_rows(tree_p.read_text(encoding="utf-8"))
        preds = load_predicates(pred_p.read_text(encoding="utf-8"))

        if args.emit_owner_map:
            warnings = emit_owner_map(rules, root / MAP_REL)
            print(f"매핑표 기록: {MAP_REL} · 규칙 {len(rules)}건")
            for w in warnings:
                print(" ", w)
            return EXIT_VIOLATION if warnings else EXIT_CLEAN

        findings: list[str] = []
        findings += check_duplicates(rules)
        findings += check_dangling_refs(rules)
        findings += check_tree_coverage(rules, tree)
        findings += check_card_coverage(spec_text)
        findings += check_dead_phrases(rules)
        findings += check_predicates(rules, preds)
        findings += check_grades(rules, spec_text)
        map_p = root / MAP_REL
        map_state = "매핑표 없음(⑧ 생략)"
        if map_p.is_file():
            findings += check_owner_map(rules, load_owner_map(map_p.read_text(encoding="utf-8")))
            map_state = "⑧ 포함"
    except StructureError as e:
        print(f"구조 전제 깨짐: {e}", file=sys.stderr)
        return EXIT_STRUCTURE

    tally = {g: sum(1 for r in rules if r.grade == g) for g in GRADES}
    print(
        f"규칙 {len(rules)} · " + " · ".join(f"{g} {n}" for g, n in tally.items()) + f" · {map_state}"
    )
    if findings:
        for f in findings:
            print(" ", f)
        print(f"위반 {len(findings)}건")
        return EXIT_VIOLATION
    print("위반 0건")
    return EXIT_CLEAN


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
