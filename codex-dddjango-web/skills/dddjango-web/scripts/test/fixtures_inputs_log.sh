#!/usr/bin/env bash
# dddjango-web inputs 기록 명령 픽스처 — Coordinator 본문(Phase 2 step 3)의 ```sh 블록 ①②를
# 그대로 뽑아 가짜 검사기로 돌린다. 판정: 명령 exit = 검사기 exit(행을 못 쓰면 1) · 행마다 탭 구분 5칸 ·
# 출력 칸 = 검사기 stdout+stderr 원문(탭·줄바꿈은 공백 · `%`·`\`·백틱 글자 그대로) · 기록 시각 UTC ·
# 임시 출력 파일 삭제 · coder 행은 파일 → 블록 ②(셸 해석 0 · 시각은 블록이 붙임) · 네 줄이 아니거나
# 탭이 든 행 파일은 붙지 않는다. 블록은 bash 와 (있으면) zsh 로 돈다. 이 파일 자체는 bash 전용(러너가 bash 로 부른다).
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
PASS=0; FAIL=0

# 본문 위치 — Claude 배치(commands/) · Codex 배치(SKILL.md)
if [ -f "$HERE/../../commands/dddjango-web.md" ]; then
  DOC="$HERE/../../commands/dddjango-web.md"
  MIRROR="$HERE/../../../codex-dddjango-web/skills/dddjango-web/SKILL.md"
elif [ -f "$HERE/../../SKILL.md" ]; then
  DOC="$HERE/../../SKILL.md"
  MIRROR="$HERE/../../../../../dddjango-web/commands/dddjango-web.md"
else
  echo "FAIL Coordinator 본문을 찾지 못함"; exit 1
fi

ok()  { PASS=$((PASS+1)); echo "PASS $1"; }
bad() { FAIL=$((FAIL+1)); echo "FAIL $1"; [ -n "${2:-}" ] && printf '%s\n' "$2" | head -12 | sed 's/^/    /'; return 0; }

T="$(mktemp -d)"
trap 'rm -rf "$T"' EXIT

# 블록 추출 — inputs-log.tsv 와 --phase inputs 를 함께 담은 ```sh 블록 하나(들여쓰기 3칸 제거)
extract() { # extract <md> <out>
  python3 - "$1" "$2" <<'PY'
import sys
lines = open(sys.argv[1], encoding="utf-8").read().split("\n")
blocks, cur = [], None
for line in lines:
    s = line.strip()
    if cur is None and s == "```sh":
        cur = []
    elif cur is not None and s == "```":
        blocks.append(cur); cur = None
    elif cur is not None:
        cur.append(line[3:] if line.startswith("   ") else line)
hit = [b for b in blocks if any("inputs-log.tsv" in x for x in b) and any("--phase inputs" in x for x in b)]
if len(hit) != 1:
    sys.exit(f"inputs 기록 블록 {len(hit)}개")
open(sys.argv[2], "w", encoding="utf-8").write("\n".join(hit[0]) + "\n")
PY
}

if extract "$DOC" "$T/block.sh" 2>"$T/err"; then ok "블록 추출(1개)"; else bad "블록 추출" "$(cat "$T/err")"; echo "fixtures_inputs_log: PASS=$PASS FAIL=$FAIL"; exit 1; fi
if [ -f "$MIRROR" ]; then
  if extract "$MIRROR" "$T/mirror.sh" 2>"$T/err" && cmp -s "$T/block.sh" "$T/mirror.sh"; then ok "Claude·Codex 블록 byte 동일"
  else bad "Claude·Codex 블록 byte 동일" "$(diff "$T/block.sh" "$T/mirror.sh" 2>&1; cat "$T/err")"; fi
fi

# 블록을 ①(# ① ~ # ② 앞)과 ②(# ② 뒤)로 나누고 자리표시를 채운다
fill() { # fill <part 1|2> <build> <name> <out>
  python3 - "$T/block.sh" "$1" "$2" "$3" "$4" "$T/checker.py" "$T/proj" <<'PY'
import re, sys
src, part, build, name, out, checker, proj = sys.argv[1:8]
lines = open(src, encoding="utf-8").read().split("\n")
i1 = next(i for i, x in enumerate(lines) if x.startswith("# ①"))
i2 = next(i for i, x in enumerate(lines) if x.startswith("# ②"))
body = lines[i1 + 1:i2] if part == "1" else [x for x in lines[i2 + 1:] if x.strip()]
text = "\n".join(body) + "\n"
for k, v in {"<Python>": sys.executable, "<checker>": checker, "<산출물 폴더>": build,
             "<타깃 프로젝트 루트>": proj, "<폴더명>": name, "<슬라이스>": "S1", "<회차>": "2"}.items():
    text = text.replace(k, v)
left = re.findall(r"<[^\s<>]+>", text)
if left:
    sys.exit(f"채우지 못한 자리표시: {left}")
open(out, "w", encoding="utf-8").write(text)
PY
}

# 가짜 검사기 — 모드는 환경변수 FX_MODE(ok|defect|usage). 결함은 실제 검사기처럼 stderr 로 낸다.
cat > "$T/checker.py" <<'PY'
import os, sys
mode = os.environ.get("FX_MODE", "ok")
if mode == "ok":
    print('{"input_digest": "abc123"}')
    sys.exit(0)
if mode == "defect":
    print("[design-evidence] defect: manifests[0]:\tsha mismatch %s %d \\n `x`", file=sys.stderr)
    print("[design-evidence] defect: case c1: capture missing", file=sys.stderr)
    sys.exit(2)
print("[design-evidence] usage/error: --build missing", file=sys.stderr)
sys.exit(1)
PY
mkdir -p "$T/proj"
DEFECT_CELL='[design-evidence] defect: manifests[0]: sha mismatch %s %d \n `x` [design-evidence] defect: case c1: capture missing'

fields_ok() { # fields_ok <log> — 모든 행이 정확히 5칸이면 0
  awk -F'\t' 'NF != 5 { bad = 1 } END { exit bad ? 1 : 0 }' "$1"
}
utc_ok() { # utc_ok <시각 칸> <전 UTC 분> <후 UTC 분> — 비UTC 시간대(+05:45)에서도 칸의 분이 UTC 분이면 0
  local m; m=$(printf '%s' "$1" | sed -n 's/^[0-9-]*T[0-9][0-9]:\([0-9][0-9]\):[0-9][0-9]Z$/\1/p')
  [ -n "$m" ] && { [ "$m" = "$2" ] || [ "$m" = "$3" ]; }
}

SHELLS=(bash)
command -v zsh >/dev/null 2>&1 && SHELLS+=(zsh)
export TZ=Asia/Kathmandu   # UTC 와 분이 다른 시간대 — `date -u` 가 빠지면 시각 칸의 분이 어긋난다

for SH in "${SHELLS[@]}"; do
  B="$T/build-$SH"; NAME="fx-inputs-log-$SH-$$"; mkdir -p "$B"
  TD="$T/tmp-$SH"; mkdir -p "$TD"
  if ! fill 1 "$B" "$NAME" "$T/one-$SH.sh" 2>"$T/err" || ! fill 2 "$B" "$NAME" "$T/two-$SH.sh" 2>>"$T/err"; then
    bad "[$SH] 자리표시 채움" "$(cat "$T/err")"; continue
  fi
  ROWF="$B/.coder-row-S1-2.txt"

  # A. 검사기 exit 0 → 명령 exit 0 · 행 1 · 5칸 · 출력 칸 = digest JSON 그대로 · 시각 UTC
  m0=$(date -u +%M); out=$(FX_MODE=ok TMPDIR="$TD" "$SH" "$T/one-$SH.sh" 2>&1); ec=$?; m1=$(date -u +%M)
  row=$(sed -n '1p' "$B/inputs-log.tsv" 2>/dev/null)
  f1=$(printf '%s' "$row" | awk -F'\t' '{print $1}')
  f5=$(printf '%s' "$row" | awk -F'\t' '{print $5}')
  f234=$(printf '%s' "$row" | awk -F'\t' '{print $2"|"$3"|"$4}')
  if [ "$ec" = 0 ] && [ "$f234" = "coordinator|S1/2|0" ] && [ "$f5" = '{"input_digest": "abc123"}' ] && utc_ok "$f1" "$m0" "$m1" \
     && fields_ok "$B/inputs-log.tsv" && grep -qF "inputs-log 행 1" <<<"$out" \
     && ! ls "$TD"/"$NAME"-inputs-*.out >/dev/null 2>&1; then ok "[$SH] A 성공 행(exit 0 · 5칸 · digest 칸 · UTC)"
  else bad "[$SH] A 성공 행" "ec=$ec f1=$f1 f234=$f234 f5=$f5 out=$out"; fi

  # B. 검사기 exit 2(stderr · 탭 · 여러 줄 · `%`·`\`·백틱) → 명령 exit 2 · 5칸 · 출력 칸 = stderr 원문 글자 그대로
  out=$(FX_MODE=defect TMPDIR="$TD" "$SH" "$T/one-$SH.sh" 2>&1); ec=$?
  n=$(wc -l < "$B/inputs-log.tsv" | tr -d ' ')
  row=$(sed -n '2p' "$B/inputs-log.tsv")
  f4=$(printf '%s' "$row" | awk -F'\t' '{print $4}')
  f5=$(printf '%s' "$row" | awk -F'\t' '{print $5}')
  if [ "$ec" = 2 ] && [ "$n" = 2 ] && [ "$f4" = 2 ] && [ "$f5" = "$DEFECT_CELL" ] && fields_ok "$B/inputs-log.tsv" \
     && grep -qF "sha mismatch" <<<"$out" && grep -qF "inputs-log 행 2" <<<"$out"; then ok "[$SH] B 실패 행(exit 2 보존 · stderr 원문 칸)"
  else bad "[$SH] B 실패 행" "ec=$ec n=$n f4=$f4
f5=[$f5]
want=[$DEFECT_CELL]"; fi

  # C. 검사기 exit 1 → 명령 exit 1
  FX_MODE=usage TMPDIR="$TD" "$SH" "$T/one-$SH.sh" >/dev/null 2>&1; ec=$?
  if [ "$ec" = 1 ] && fields_ok "$B/inputs-log.tsv"; then ok "[$SH] C 미실행 행(exit 1 보존)"; else bad "[$SH] C 미실행 행" "ec=$ec"; fi

  # D. coder 행 네 줄(파일 쓰기 도구 흉내 = python 직접 쓰기) — 셸 메타문자가 글자 그대로 · 시각은 블록이 UTC 로
  python3 - "$ROWF" "$T/pwned-$SH" <<'PY'
import sys
row, pwned = sys.argv[1], sys.argv[2]
cells = ["coder", "S1/2", "0",
         '{"input_digest": "abc123"} · 순서 준수 `id` $HOME %s %d "q" \'q\' $(touch ' + pwned + ') \\n']
open(row, "w", encoding="utf-8").write("\n".join(cells) + "\n")
PY
  before=$(wc -l < "$B/inputs-log.tsv" | tr -d ' ')
  m0=$(date -u +%M); out=$(TMPDIR="$TD" "$SH" "$T/two-$SH.sh" 2>&1); ec=$?; m1=$(date -u +%M)
  last=$(tail -n 1 "$B/inputs-log.tsv")
  lf1=$(printf '%s' "$last" | awk -F'\t' '{print $1}')
  rest=$(printf '%s' "$last" | cut -f2-)
  want=$(printf '%s\t%s\t%s\t%s' coder "S1/2" 0 "{\"input_digest\": \"abc123\"} · 순서 준수 \`id\` \$HOME %s %d \"q\" 'q' \$(touch $T/pwned-$SH) \\n")
  if [ "$ec" = 0 ] && [ "$rest" = "$want" ] && utc_ok "$lf1" "$m0" "$m1" && [ ! -e "$T/pwned-$SH" ] && [ ! -e "$ROWF" ] \
     && fields_ok "$B/inputs-log.tsv" && grep -qF "inputs-log 행 $((before+1))" <<<"$out"; then ok "[$SH] D coder 행(메타문자 글자 그대로 · 셸 해석 0 · UTC 시각 · 행 파일 삭제)"
  else bad "[$SH] D coder 행" "ec=$ec f1=$lf1 rest=$rest out=$out"; fi

  # E. 다섯 줄 행 파일(옛 판형 — 시각을 손으로 씀) → 붙지 않음(exit≠0 · 로그 무변 · 행 파일 보존)
  printf '2026-10-01T00:00:00Z\ncoder\nS1/2\n0\nx\n' > "$ROWF"
  before=$(wc -l < "$B/inputs-log.tsv" | tr -d ' ')
  TMPDIR="$TD" "$SH" "$T/two-$SH.sh" >/dev/null 2>&1; ec=$?
  after=$(wc -l < "$B/inputs-log.tsv" | tr -d ' ')
  if [ "$ec" != 0 ] && [ "$before" = "$after" ] && [ -e "$ROWF" ]; then ok "[$SH] E 다섯 줄 행 거부"; else bad "[$SH] E 다섯 줄 행 거부" "ec=${ec} ${before}→${after}"; fi

  # F. 칸 안 탭 → 붙지 않음
  printf 'coder\nS1/2\n0\nx\ty\n' > "$ROWF"
  TMPDIR="$TD" "$SH" "$T/two-$SH.sh" >/dev/null 2>&1; ec=$?
  after2=$(wc -l < "$B/inputs-log.tsv" | tr -d ' ')
  if [ "$ec" != 0 ] && [ "$after" = "$after2" ]; then ok "[$SH] F 탭 든 칸 거부"; else bad "[$SH] F 탭 든 칸 거부" "ec=$ec"; fi

  # G. 마지막 줄 바꿈 없는 네 줄 → 붙는다 / 행 파일 없음 → 붙지 않음
  printf 'coder\nS1/2\n0\nx' > "$ROWF"
  TMPDIR="$TD" "$SH" "$T/two-$SH.sh" >/dev/null 2>&1; ec=$?
  rest=$(tail -n 1 "$B/inputs-log.tsv" | cut -f2-)
  if [ "$ec" = 0 ] && [ "$rest" = "$(printf 'coder\tS1/2\t0\tx')" ] && fields_ok "$B/inputs-log.tsv"; then ok "[$SH] G1 끝 줄바꿈 없는 행 수용"
  else bad "[$SH] G1 끝 줄바꿈 없는 행 수용" "ec=$ec rest=$rest"; fi
  rm -f "$ROWF"
  TMPDIR="$TD" "$SH" "$T/two-$SH.sh" >/dev/null 2>&1; ec=$?
  if [ "$ec" != 0 ]; then ok "[$SH] G2 행 파일 없음 거부"; else bad "[$SH] G2 행 파일 없음 거부" "ec=$ec"; fi

  # H. 재제출 — 같은 회차를 한 번 더 돌려도 새 행이 붙고 앞 행은 그대로다
  first=$(sed -n '1p' "$B/inputs-log.tsv")
  n0=$(wc -l < "$B/inputs-log.tsv" | tr -d ' ')
  FX_MODE=ok TMPDIR="$TD" "$SH" "$T/one-$SH.sh" >/dev/null 2>&1; ec=$?
  n1=$(wc -l < "$B/inputs-log.tsv" | tr -d ' ')
  if [ "$ec" = 0 ] && [ "$n1" = $((n0+1)) ] && [ "$(sed -n '1p' "$B/inputs-log.tsv")" = "$first" ] && fields_ok "$B/inputs-log.tsv"
  then ok "[$SH] H 재제출 행 추가"; else bad "[$SH] H 재제출 행 추가" "ec=${ec} ${n0}→${n1}"; fi

  # I. 로그를 쓸 수 없으면(경로가 폴더) 검사기가 통과해도 명령 exit 1
  B2="$T/build2-$SH"; mkdir -p "$B2/inputs-log.tsv"
  fill 1 "$B2" "$NAME-2" "$T/one2-$SH.sh" 2>/dev/null
  out=$(FX_MODE=ok TMPDIR="$TD" "$SH" "$T/one2-$SH.sh" 2>&1); ec=$?
  if [ "$ec" = 1 ] && grep -qF "inputs-log 기록 실패" <<<"$out"; then ok "[$SH] I 기록 실패 → exit 1"; else bad "[$SH] I 기록 실패 → exit 1" "ec=$ec out=$out"; fi
done

echo "fixtures_inputs_log: PASS=$PASS FAIL=$FAIL"
[ "$FAIL" = 0 ]
