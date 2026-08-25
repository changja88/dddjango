#!/usr/bin/env python3
"""check_motion_spec — 모션 처분 표의 결정론 검사 (dddjango-web).

구현측 모션은 폐쇄계다(D12 — CSS 모션 + `data-motion` 선언뿐·전부 커밋 텍스트).
따라서 브라우저 없이 «관찰 표(motion-notes) ↔ 처분 표(설계 명세) ↔ web/ 트리»의
정적 대조로 모션 검증이 성립한다. 이 검사기가 그 대조의 소유자다 — 계획
workspace/plan/2026-08-25-web-motion-determinism-plan.md W4.

사용:
  python check_motion_spec.py --spec-only <design-spec.md> <motion-notes.md> [--audit <render-audit.json>]
      # G1 승인 직후 — 판형·전수성(+실측→기록 전사 계수 게이트). red는 architect 반송 근거.
  python check_motion_spec.py <design-spec.md> <motion-notes.md> <web-root>
      # G2 — 전수성 + 채택 행 구현 좌표 실재 + 역스윕(처분 표 밖 모션 발명 발견).
      # <web-root>는 소비 프로젝트의 web/ 디렉터리. 지위는 compare와 동급 —
      # 판단 자료(비차단)·배너 1급 의무 표기.

표 판형(헤더 행 문자 고정 — 이 문자열이 파서의 앵커다):
  notes: | id | 요소 | 트리거 | 효과 | 재현 분류(예상) | 출처 |
  spec : | note id | 처분 | 분류 | 구현 좌표 | 값 | 근거 |
  상태 행(id 칼럼 `—`)은 전수성·수량 대조에서 제외 — «(없음-확인)»은 green,
  «(미관찰)»은 [warn] 미검증. 헤더 미검출(레거시 산문 판형)은 [warn]+exit 0
  (합법 재빌드 비차단) — 단 notes가 표 판형이고 모션 행이 있는데 spec에 표가
  없으면 그것은 전수 처분 누락(FINDING)이다.

exit: 0=발견 0 / 1=사용법·파일 부재·읽기 실패(미실행 취급 — 통과가 아니다) / 2=발견 ≥1
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

NOTES_HEADER = "| id | 요소 | 트리거 | 효과 | 재현 분류(예상) | 출처 |"
SPEC_HEADER = "| note id | 처분 | 분류 | 구현 좌표 | 값 | 근거 |"
ID_RE = re.compile(r"^m\d+$")
STATUS_IDS = {"—", "-"}  # 빈칸은 상태 행이 아니라 id 판형 위반이다(조용한 증발 금지)
DISPOSITIONS = {"채택", "기각", "한계"}
KINDS = {"css-hover", "css-focus", "css-transition", "css-keyframes", "러너", "—", "-"}
COORD_RE = re.compile(r"^(?P<path>[^:]+?)\s*::\s*(?P<sel>.+)$")
TOKEN_RE = re.compile(r"var\((--[\w-]+)\)")
KEYFRAMES_RE = re.compile(r"@keyframes\s+([\w-]+)")
DATA_MOTION_RE = re.compile(r"data-motion=(\"|')([^\"']+)\1")
CSS_COMMENT_RE = re.compile(r"/\*.*?\*/", re.S)
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
ESC_PIPE = "\x00"  # 셀 안 이스케이프 파이프(\|) 보존용 placeholder


def die(msg: str) -> None:
    print(f"[motion-spec] {msg}", file=sys.stderr)
    sys.exit(1)


def read_text(path: str) -> str:
    p = Path(path)
    if not p.is_file():
        die(f"파일 없음: {path}")
    try:
        return p.read_text(encoding="utf-8")
    except OSError as e:
        die(f"읽기 실패: {path} ({e})")
    raise AssertionError


def split_row(line: str) -> list[str]:
    """마크다운 표 행을 셀로 분해 — 이스케이프 파이프(\\|)는 셀 안 문자로 보존한다."""
    guarded = line.replace("\\|", ESC_PIPE)
    return [c.strip().replace(ESC_PIPE, "|") for c in guarded.strip().strip("|").split("|")]


def norm_row(line: str) -> str:
    return "| " + " | ".join(split_row(line)) + " |"


def parse_tables(text: str, header: str, label: str, findings: list[str]) -> list[list[str]] | None:
    """헤더 행 완전 일치를 앵커로 표 행들을 파스. 헤더 미검출이면 None(레거시/부재).

    코드 펜스(```·~~~) 내부는 건너뛴다(문서의 판형 예시가 실표로 오파스되면 G1 false red).
    셀 수가 헤더와 다른 행은 판형 위반 FINDING. 복수 표는 이어 붙인다(결정적)."""
    ncols = len(split_row(header))
    lines = text.splitlines()
    rows: list[list[str]] = []
    found = False
    in_fence = False
    i = 0
    while i < len(lines):
        stripped = lines[i].lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            i += 1
            continue
        if not in_fence and norm_row(lines[i]) == header:
            found = True
            i += 1
            if i < len(lines) and set(lines[i].replace("|", "").strip()) <= set("-: "):
                i += 1  # 구분 행
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                cells = split_row(lines[i])
                if len(cells) != ncols:
                    findings.append(f"{label} 표 판형 위반(칼럼 {len(cells)}≠{ncols}): {lines[i].strip()[:80]}")
                else:
                    rows.append(cells)
                i += 1
            continue
        i += 1
    return rows if found else None


def audit_motion_counts(path: str) -> int:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        die(f"--audit 읽기 실패: {path} ({e})")
    motion = data.get("motion") if isinstance(data, dict) else None
    if not isinstance(motion, dict):
        return 0  # v1 — 계수 게이트 해당 없음
    return sum(len(motion.get(k, []) or []) for k in
               ("transitions", "transitionRules", "keyframes", "animationRules", "hoverSelectors", "focusSelectors"))


def check_impl(root: Path, spec_rows: list[list[str]], findings: list[str], warns: list[str]) -> None:
    css_files = sorted(root.rglob("*.css"))
    html_files = sorted(root.rglob("*.html"))
    # 주석은 걷어내고 본다 — 주석 속 잔재가 역스윕 오탐·존재 검사 오통과를 만들지 않게
    css_all = CSS_COMMENT_RE.sub("", "\n".join(f.read_text(encoding="utf-8", errors="replace") for f in css_files))
    html_all = HTML_COMMENT_RE.sub("", "\n".join(f.read_text(encoding="utf-8", errors="replace") for f in html_files))

    def token_used(token: str, body: str) -> bool:
        # var( 토큰 [,)]) 정확 매치 — 접두 부분 문자열(--duration-fast ⊂ --duration-faster) 오통과 차단
        return re.search(rf"var\(\s*{re.escape(token)}\s*[,)]", body) is not None

    adopted_kf: set[str] = set()
    adopted_tokens: set[str] = set()
    for row in spec_rows:
        note_id, disp, kind, coord, value, _ = row
        if disp != "채택":
            continue
        if kind in ("—", "-"):
            findings.append(f"{note_id}: 채택인데 분류 미지정(—)")
            continue
        if kind == "러너":
            token = coord.strip()
            adopted_tokens.add(token)
            if not re.search(rf"data-motion=(\"|'){re.escape(token)}\1", html_all):
                findings.append(f"{note_id}: 러너 채택 토큰 «{token}» — 템플릿에 data-motion 선언 없음")
            if "motion.js" not in html_all:
                findings.append(f"{note_id}: 러너 채택인데 base.html에 motion.js 로드 태그 없음")
            if "[data-motion]" not in css_all or "motion-in" not in css_all:
                findings.append(f"{note_id}: 러너 초기 은닉 판형([data-motion]·motion-in) CSS 없음")
        else:
            m = COORD_RE.match(coord)
            if not m:
                findings.append(f"{note_id}: 구현 좌표 판형 위반(«파일경로 :: 셀렉터» 필요): {coord[:60]}")
                continue
            rel, sel = m.group("path").strip(), m.group("sel").strip()
            cand = [root / rel, root.parent / rel]  # web/ 프리픽스 유무 양쪽 수용
            target = next((p for p in cand if p.is_file()), None)
            if target is None:
                findings.append(f"{note_id}: 좌표 파일 없음 — {rel}")
                continue
            body = CSS_COMMENT_RE.sub("", target.read_text(encoding="utf-8", errors="replace"))
            needle = f"@keyframes {sel}" if kind == "css-keyframes" else sel
            if needle not in body:
                findings.append(f"{note_id}: {rel} 에 «{needle}» 없음")
            if kind == "css-keyframes":
                adopted_kf.add(sel)
            for token in TOKEN_RE.findall(value):
                if not token_used(token, body):
                    findings.append(f"{note_id}: 값 토큰 {token} 사용이 {rel} 의 선언에 없음")
        # 값 토큰 정의 검사는 분류 무관(러너 행 포함) — 유령 토큰이 조용히 통과하지 않게
        for token in TOKEN_RE.findall(value):
            if f"{token}:" not in css_all:
                findings.append(f"{note_id}: 값 토큰 {token} 정의가 web/ CSS 어디에도 없음")

    # 역스윕 — 처분 표 밖의 모션 구현(발명) 발견
    for name in sorted(set(KEYFRAMES_RE.findall(css_all))):
        if name not in adopted_kf:
            findings.append(f"역스윕: 처분 표 채택에 없는 @keyframes «{name}» — 모션 발명(명세 밖)")
    for _q, token in sorted(set(DATA_MOTION_RE.findall(html_all))):
        if "{{" in token or "{%" in token:
            findings.append(f"역스윕: 동적 data-motion 값 «{token}» — 정적 검사 불가(리터럴 토큰 필요)")
        elif token not in adopted_tokens:
            findings.append(f"역스윕: 처분 표 채택에 없는 data-motion «{token}» — 모션 발명(명세 밖)")
    if not css_files and not html_files:
        warns.append(f"web-root에 css/html 파일 0건 — 경로 확인: {root}")


def main(argv: list[str]) -> int:
    spec_only = "--spec-only" in argv
    args = [a for a in argv[1:] if a != "--spec-only"]
    audit_path: str | None = None
    if "--audit" in args:
        i = args.index("--audit")
        if i + 1 >= len(args):
            die("사용: --audit <render-audit.json>")
        audit_path = args[i + 1]
        del args[i:i + 2]
    if (spec_only and len(args) != 2) or (not spec_only and len(args) != 3):
        die("사용: check_motion_spec.py --spec-only <spec.md> <notes.md> [--audit <audit.json>] | <spec.md> <notes.md> <web-root>")

    findings: list[str] = []
    warns: list[str] = []
    spec_text, notes_text = read_text(args[0]), read_text(args[1])

    notes_rows = parse_tables(notes_text, NOTES_HEADER, "notes", findings)
    spec_rows = parse_tables(spec_text, SPEC_HEADER, "spec", findings)

    if notes_rows is None:
        print(f"[warn] 레거시 산문 판형(motion-notes 표 헤더 미검출) — 모션 축 미검증(표 판형 재기록 권장): {args[1]}")
        print("[motion-spec] 발견 0건 · 모션 축 미검증(레거시)")
        return 0

    motion_rows = [r for r in notes_rows if r[0] not in STATUS_IDS]
    status_joins = [" ".join(r) for r in notes_rows if r[0] in STATUS_IDS]
    motion_ids: list[str] = []  # 전수성 모수는 판형 유효 id만 — 위반 id는 FINDING 후 연쇄 오탐 차단
    for r in motion_rows:
        if ID_RE.match(r[0]):
            motion_ids.append(r[0])
        else:
            findings.append(f"notes id 판형 위반(m<n> 필요·빈칸 불가): «{r[0]}» — {r[1][:30]}")
    for sj in status_joins:
        if "(없음-확인)" not in sj and "(미관찰)" not in sj:
            warns.append(f"상태 행에 마커((없음-확인)|(미관찰)) 없음: {sj[:60]}")

    spec_ids: list[str] = []
    if spec_rows is None:
        if motion_ids:
            findings.append(f"처분 표 미검출 — notes 모션 {len(motion_ids)}행의 전수 처분 누락(architect 소유)")
        elif any("(미관찰)" in sj for sj in status_joins):
            warns.append("모션: 미검증(관찰 생략 — 문답·재실측으로 보강 권장)")
        elif any("(없음-확인)" in sj for sj in status_joins):
            print("INFO 모션: 없음-확인(관찰 근거 있음) — 처분 표 불요")
    else:
        for row in spec_rows:
            note_id, disp, kind = row[0], row[1], row[2]
            if note_id in spec_ids:
                findings.append(f"처분 표 중복 id: {note_id} — 모순 처분(채택+기각 병존) 가능")
            spec_ids.append(note_id)
            if disp not in DISPOSITIONS:
                findings.append(f"{note_id}: 처분 값 위반(채택|기각|한계): «{disp}»")
            if kind not in KINDS:
                findings.append(f"{note_id}: 분류 값 위반: «{kind}»")
        # 전수성 — 양방향(상태 행·판형 위반 id 제외 — 위반은 위에서 이미 FINDING)
        for mid in motion_ids:
            if mid not in spec_ids:
                findings.append(f"전수성: notes {mid} 가 처분 표에 없음(빈칸 0 위반)")
        for sid in spec_ids:
            if sid not in motion_ids:
                findings.append(f"전수성: 처분 표 {sid} 가 notes에 없음(관찰 근거 없는 처분)")
        if not motion_ids and not spec_ids and any("(미관찰)" in sj for sj in status_joins):
            warns.append("모션: 미검증(관찰 생략 — 문답·재실측으로 보강 권장)")

    if audit_path is not None:
        counts = audit_motion_counts(audit_path)
        measured_rows = [r for r in motion_rows if "실측" in r[5] or "스캔" in r[5]]
        if counts > 0 and not measured_rows:
            warns.append(f"전사 이음매: 실측 모션 인벤토리 {counts}건인데 notes에 출처=실측/스캔 행 0 — 전사 누락 의심")

    if not spec_only:
        root = Path(args[2])
        if not root.is_dir():
            die(f"web-root 디렉터리 없음: {args[2]}")
        check_impl(root, spec_rows or [], findings, warns)

    for w in warns:
        print(f"[warn] {w}")
    for i, f in enumerate(findings, 1):
        print(f"FINDING {i}) {f}")
    mode = "spec-only" if spec_only else "full"
    print(f"[motion-spec] {mode} · 발견 {len(findings)}건 · notes 모션 {len(motion_ids)}행 · 처분 {len(spec_ids)}행")
    return 2 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
