#!/usr/bin/env python3
"""check_token_disposition — 토큰 전수 처분의 결정론 검사 (dddjango-web).

architecture-web §8 「크기 전수 연결」은 규범에만 있고 **집행이 없었다** — 절단 풀의
전수성도, 기각 사유의 사실성도 기계가 보지 않았다. 그 사이로 실결함이 나갔다:
A8 관계인 빌드가 `--space-1`(2px)을 «미사용 space 단계»라는 사유로 기각했는데 동결 시안은
그 값을 4곳에 쓰고 있었고(그중 하나가 스크롤 컨테이너의 `padding: 2px 2px 4px`), 그 패딩이
명세로 옮겨지지 않아 포커스 링이 좌우로 잘렸다.
정본: workspace/design/2026-09-15-web-clip-fidelity.md · 계획 …-plan.md T1.

사용:
  python check_token_disposition.py --spec-only <design-spec.md> <design-tokens.json> \
      <design-ref 경로> [--screen-meta <screen-meta.json>]

검사 3종:
  T1a 전수성   — 절단 풀의 모든 토큰이 채택/기각 어느 한쪽에 있는가(빈칸 0).
  T1b 양방향   — 풀 밖 토큰 금지 · 채택∩기각 중복 금지.
  T1c 기각 정당성 — **기각한 토큰의 값이 동결 시안에 실제로 쓰이면 발견.**
      사유 문구는 보지 않는다(거짓 사유 차단이 목적이다). 발견은 «기각이 틀렸다»가 아니라
      «사유를 사실로 대라»는 반송 근거다.
      오탐 가드 3종 — ① 비변별 값(0·none·auto…) 제외 ② **귀속 불가**: 그 값을 채택 토큰이
      공유하면 시안 사용을 기각 토큰에 귀속할 수 없으므로 제외 ③ **화면 범위**: screen-meta의
      source_sha256으로 이번 화면의 dc만 읽는다.

표 판형(헤더 행 문자 고정 — 이 문자열이 파서의 앵커다):
  | 축 | 처분 | 토큰 |
  축 ∈ colors|typography|spacing|borderRadius|shadows · 처분 ∈ 채택|기각 · 토큰은 백틱 인용 목록.
  **탈출구 대칭 가드**: 토큰 전수 처분 절 heading이 있는데 고정 헤더가 없으면 FINDING(판형 위반)이다.
  절 자체가 없으면 [warn]+exit 0(레거시 산문 — 합법 재빌드 비차단).

exit: 0=발견 0 / 1=사용법·파일 부재·파싱 실패(미실행 취급 — 통과가 아니다) / 2=발견 ≥1
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

HEADER = "| 축 | 처분 | 토큰 |"
AXES = ("colors", "typography", "spacing", "borderRadius", "shadows")
DISPOSITIONS = ("채택", "기각")
SECTION_RE = re.compile(r"^#{1,6}\s.*토큰\s*전수\s*처분", re.M)
TOKEN_RE = re.compile(r"`(--[\w-]+)`")
INLINE_STYLE_RE = re.compile(r'style\s*=\s*"([^"]*)"')
PX_RE = re.compile(r"^-?[0-9.]+px$")
REM_RE = re.compile(r"^(-?[0-9.]+)(rem|em)$")
HEX_RE = re.compile(r"^#[0-9a-fA-F]{3,8}$")
RGB_RE = re.compile(r"^rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,[^)]*)?\)$")
ESC_PIPE = "\x00"
# 비변별 값 — 시안 어디에나 있어 귀속이 성립하지 않는다(`--space-0: 0px` ↔ `margin: 0` 수백 건).
TRIVIAL = frozenset(
    ("0", "0px", "none", "auto", "transparent", "inherit", "initial", "unset", "1", "100%")
)
REM_BASE = 16.0


def die(msg: str) -> None:
    print(f"[token-disposition] {msg}", file=sys.stderr)
    sys.exit(1)


def warn(msg: str) -> None:
    print(f"[warn] {msg}")


def read_text(path: Path) -> str:
    if not path.is_file():
        die(f"파일 없음: {path}")
    try:
        return path.read_text(encoding="utf-8-sig")
    except OSError as e:
        die(f"읽기 실패: {path} ({e})")
    raise AssertionError


def split_row(line: str) -> list[str]:
    """마크다운 표 행을 셀로 분해 — 이스케이프 파이프(\\|)는 셀 안 문자로 보존한다."""
    guarded = line.replace("\\|", ESC_PIPE)
    return [c.strip().replace(ESC_PIPE, "|") for c in guarded.strip().strip("|").split("|")]


def norm_row(line: str) -> str:
    return "| " + " | ".join(split_row(line)) + " |"


def parse_disposition(text: str, findings: list[str]) -> tuple[dict[str, set[str]], bool] | None:
    """헤더 앵커로 처분 표를 파스. 헤더 미검출이면 None.

    코드 펜스 내부는 건너뛴다(문서의 판형 예시가 실표로 오파스되면 false red).
    반환: ({'채택': {...}, '기각': {...}}, 절_heading_존재)."""
    ncols = len(split_row(HEADER))
    has_section = False
    out: dict[str, set[str]] = {d: set() for d in DISPOSITIONS}
    found = False
    in_table = False
    in_fence = False
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if SECTION_RE.match(stripped):
            has_section = True
            continue
        if norm_row(line) == HEADER:
            found = in_table = True
            continue
        if in_table and not stripped.startswith("|"):
            in_table = False  # 연속 블록의 끝 — 하류 표를 먹지 않는다(선례 parse_tables)
            continue
        if not in_table:
            continue
        cells = split_row(line)
        if set("".join(cells)) <= set("-: "):  # 구분 행
            continue
        if len(cells) != ncols:
            findings.append(f"판형 위반 — 셀 {len(cells)}개(헤더 {ncols}개): {line.strip()[:80]}")
            continue
        axis, disp, tokens = cells[0], cells[1], cells[2]
        if axis not in AXES:
            findings.append(f"판형 위반 — 축 이름 «{axis}» 은 {'|'.join(AXES)} 가 아니다")
            continue
        if disp not in DISPOSITIONS:
            findings.append(f"판형 위반 — 처분 «{disp}» 은 채택|기각 이 아니다 (축 {axis})")
            continue
        names = TOKEN_RE.findall(tokens)
        if not names:
            findings.append(f"판형 위반 — 토큰 칸이 비었거나 백틱 인용이 없다 (축 {axis} · {disp})")
            continue
        out[disp].update(names)
    return (out, has_section) if found else None


def load_pool(path: Path) -> dict[str, str]:
    """절단 풀 = design-tokens.json 의 dict 절(colors·typography·spacing·borderRadius·shadows) 합집합.

    arbitraryValues 는 리스트(Tailwind 임의값)라 토큰이 아니다 — 풀에 넣지 않고 계수만 보고한다."""
    try:
        data = json.loads(read_text(path))
    except json.JSONDecodeError as e:
        die(f"JSON 파싱 실패: {path} ({e})")
    if not isinstance(data, dict):
        die(f"최상위가 객체가 아니다: {path}")
    pool: dict[str, str] = {}
    for section, value in data.items():
        if not isinstance(value, dict):
            continue
        for name, raw in value.items():
            if isinstance(raw, dict):
                # 중첩 표현(예: typography 의 {"size": "14px"}) — 단일 값이면 벗긴다.
                inner = [str(v).strip() for v in raw.values()]
                pool[name] = inner[0] if len(inner) == 1 else " ".join(inner)
            else:
                pool[name] = str(raw).strip()
    if not pool:
        die(f"절단 풀이 비었다: {path} — extract_design 산출만 받는다")
    extra = data.get("arbitraryValues")
    if isinstance(extra, list) and extra:
        warn(f"arbitraryValues {len(extra)}건은 토큰이 아니라 풀 밖이다 — 이 검사의 대상이 아니다")
    return pool


def design_bodies(design_ref: Path, screen_meta: Path | None) -> tuple[str, str]:
    """동결 시안의 인라인 선언 본문과 그 범위 설명을 돌려준다.

    screen-meta 의 source_sha256 이 있으면 그 파일 하나로 좁힌다(가드 ③ — 범위 밖 화면의
    값이 기각 정당성 발견으로 새는 것을 막는다)."""
    if design_ref.is_file():
        files = [design_ref]
        scope = design_ref.name
    else:
        files = sorted(p for p in design_ref.rglob("*.html") if p.is_file())
        scope = f"{design_ref.name}/**/*.html {len(files)}건"
    if not files:
        die(f"시안 HTML 이 없다: {design_ref}")
    if screen_meta is not None and not screen_meta.is_file():
        warn(f"screen-meta 없음: {screen_meta} — 전 시안 파일로 대조한다")
        screen_meta = None
    if screen_meta is not None:
        try:
            want = str(json.loads(read_text(screen_meta)).get("source_sha256") or "").lower()
        except json.JSONDecodeError as e:
            die(f"JSON 파싱 실패: {screen_meta} ({e})")
        if want:
            picked = [p for p in files
                      if hashlib.sha256(p.read_bytes()).hexdigest().lower() == want]
            if picked:
                files, scope = picked, picked[0].name
            else:
                warn(f"screen-meta 의 source_sha256 과 일치하는 시안 파일이 없다 — 전 파일로 대조한다")
    decls: list[str] = []
    for path in files:
        src = path.read_text(encoding="utf-8", errors="replace")
        for style in INLINE_STYLE_RE.findall(src):
            decls.extend(d.strip() for d in style.split(";") if d.strip())
    return "\n".join(decls), scope


def norm_color(value: str) -> str | None:
    v = value.strip()
    if HEX_RE.match(v):
        h = v[1:]
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        return "#" + h[:6].lower()
    m = RGB_RE.match(v)
    if m:
        return "#" + "".join(f"{int(m.group(i)):02x}" for i in (1, 2, 3))
    return None


def px_of(value: str) -> float | None:
    v = value.strip()
    if PX_RE.match(v):
        return float(v[:-2])
    m = REM_RE.match(v)
    if m:
        return float(m.group(1)) * REM_BASE
    return None


def used_in_design(name: str, value: str, body: str,
                   body_colors: set[str], body_px: set[float]) -> bool | None:
    """시안 본문이 이 토큰을 쓰는가. None = 미대조(복합 값)."""
    if re.search(r"var\(\s*" + re.escape(name) + r"\s*[,)]", body):
        return True  # 시안이 토큰을 직접 인용한다 — 값 대조보다 강한 증거다
    v = value.strip()
    if v.lower() in TRIVIAL:
        return None
    px = px_of(v)
    if px is not None:
        return px in body_px
    color = norm_color(v)
    if color is not None:
        return color in body_colors
    return None


def body_index(body: str) -> tuple[set[str], set[float]]:
    """시안 본문에서 대조 가능한 길이·색을 추출한다 — 값 단위로 뽑아 부분 일치 오탐을 없앤다."""
    colors: set[str] = set()
    lengths: set[float] = set()
    for decl in body.splitlines():
        _, _, raw = decl.partition(":")
        for tok in re.findall(r"#[0-9a-fA-F]{3,8}|rgba?\([^)]*\)|-?[0-9.]+(?:px|rem|em)", raw):
            c = norm_color(tok)
            if c is not None:
                colors.add(c)
                continue
            p = px_of(tok)
            if p is not None:
                lengths.add(p)
    return colors, lengths


def main(argv: list[str]) -> int:
    if len(argv) < 4 or argv[0] != "--spec-only":
        die("사용: check_token_disposition.py --spec-only <design-spec.md> "
            "<design-tokens.json> <design-ref 경로> [--screen-meta <screen-meta.json>]")
    spec_path, tokens_path, ref_path = (Path(argv[1]), Path(argv[2]), Path(argv[3]))
    screen_meta = None
    rest = argv[4:]
    if rest:
        if len(rest) != 2 or rest[0] != "--screen-meta":
            die("사용: … [--screen-meta <screen-meta.json>]")
        screen_meta = Path(rest[1])
    if not ref_path.exists():
        die(f"시안 경로 없음: {ref_path}")

    findings: list[str] = []
    parsed = parse_disposition(read_text(spec_path), findings)
    pool = load_pool(tokens_path)

    if parsed is None:
        # 탈출구 대칭 가드 — 절은 있는데 판형이 없으면 그것은 판형 위반이지 레거시가 아니다.
        has_section = bool(SECTION_RE.search(read_text(spec_path)))
        if has_section:
            print(f"[FINDING] 토큰 전수 처분 절은 있는데 고정 헤더 «{HEADER}» 가 없다 — 판형 위반")
            print("[token-disposition] 발견 1건")
            return 2
        warn(f"고정 헤더 «{HEADER}» 미검출 · 전수 처분 절도 없다 — 레거시 산문 판형(미검증)")
        print("[token-disposition] 미검증 — 판형 부재")
        return 0

    table, _ = parsed
    adopted, rejected = table["채택"], table["기각"]

    both = sorted(adopted & rejected)
    for name in both:
        findings.append(f"T1b 중복 처분 — 채택과 기각 양쪽에 있다: {name}")
    outside = sorted((adopted | rejected) - set(pool))
    for name in outside:
        findings.append(f"T1b 풀 밖 토큰 — design-tokens.json 에 없다: {name}")
    missing = sorted(set(pool) - (adopted | rejected))
    for name in missing:
        findings.append(f"T1a 미처분 — 채택·기각 어느 쪽에도 없다: {name} = {pool[name]}")

    body, scope = design_bodies(ref_path, screen_meta)
    body_colors, body_px = body_index(body)
    # 가드 ② 귀속 불가 — 채택 토큰이 같은 값을 가지면 시안 사용을 기각 토큰에 귀속할 수 없다.
    adopted_values = {pool[n].strip().lower() for n in adopted if n in pool}
    n_trivial = n_shared = n_uncompared = 0
    judged = sorted(t for t in rejected - adopted if t in pool)
    for name in judged:
        value = pool[name]
        if value.strip().lower() in TRIVIAL:
            n_trivial += 1
            continue
        if value.strip().lower() in adopted_values:
            n_shared += 1
            continue
        hit = used_in_design(name, value, body, body_colors, body_px)
        if hit is None:
            n_uncompared += 1
        elif hit:
            findings.append(
                f"T1c 기각 정당성 — 기각했는데 시안이 쓴다: {name} = {value} (시안 {scope})")

    print(f"[token-disposition] 풀 {len(pool)} · 채택 {len(adopted)} · 기각 {len(rejected)} · "
          f"시안 범위 {scope}")
    print(f"[token-disposition] 기각 정당성 커버리지 — 판정 {len(judged)} 중 "
          f"대조 {len(judged) - n_trivial - n_shared - n_uncompared} · "
          f"비변별 제외 {n_trivial} · 귀속 불가 제외 {n_shared} · 복합 미대조 {n_uncompared}")
    for line in findings:
        print(f"[FINDING] {line}")
    print(f"[token-disposition] 발견 {len(findings)}건")
    return 2 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
