#!/usr/bin/env bash
# dddjango-web 토큰 처분 집행 검사(check_token_disposition) 자기 회귀 픽스처.
# 케이스마다 negative(발견)에 positive-control(정상 통과) 짝을 둔다:
#   TD1(정상) ↔ TD2(T1a 미처분)·TD3(T1b 풀 밖)·TD4(T1b 중복)
#   TD5(T1c — 기각한 2px 를 시안이 쓴다 = 이번 결함의 회귀) ↔ TD6(기각했고 시안에 없음)
#   TD7(비변별 0px 제외) · TD8(rem↔px 환산) · TD9(귀속 불가 — 채택 토큰이 같은 값)
#   TD10(절 있는데 판형 없음 = FINDING) ↔ TD11(절도 없음 = warn+0)
#   TD12(화면 범위 — screen-meta 로 이번 화면 dc 만) · U1(사용법) · DET(결정론)
set -u
SCRIPTS="$(cd "$(dirname "$0")/.." && pwd)"
PASS=0; FAIL=0

assert() { # assert <이름> <기대exit> <있어야 할 문자열|-> <없어야 할 문자열|-> <실제exit> <출력>
  local name="$1" wantexit="$2" want="$3" unwant="$4" gotexit="$5" out="$6" ok=1
  [ "$gotexit" != "$wantexit" ] && ok=0
  [ "$want" != "-" ] && ! grep -qF -- "$want" <<<"$out" && ok=0
  [ "$unwant" != "-" ] && grep -qF -- "$unwant" <<<"$out" && ok=0
  if [ $ok = 1 ]; then PASS=$((PASS+1)); echo "PASS $name"; else
    FAIL=$((FAIL+1)); echo "FAIL $name (exit=$gotexit want=$wantexit)"; echo "$out" | head -20 | sed 's/^/    /'
  fi
}

T="$(mktemp -d)"
trap 'rm -rf "$T"' EXIT

mk() { # mk <이름> <처분표 본문> <시안 인라인 style 내용> [extra tokens json]
  local d="$T/$1"; mkdir -p "$d/design-ref"
  {
    echo "# 명세"
    echo
    echo "## 9. 토큰 전수 처분"
    echo
    printf '%s\n' "$2"
  } > "$d/design-spec.md"
  cat > "$d/design-tokens.json" <<JSON
{"colors":{"--accent":"#D0727A","--ink":"#1A1A1A"},
 "typography":{"--fs-body":"14px"},
 "spacing":{"--space-1":"2px","--space-2":"4px","--space-0":"0px","--gutter":"20px"},
 "borderRadius":{"--radius-sm":"12px"},
 "shadows":{"--shadow-1":"0 1px 3px rgba(0,0,0,.08)"},
 "arbitraryValues":[]}
JSON
  printf '<div style="%s"></div>\n' "$3" > "$d/design-ref/screen.dc.html"
  echo "$d"
}

HDR='| 축 | 처분 | 토큰 |
|---|---|---|'
FULL_OK="$HDR
| colors | 채택 | \`--accent\`, \`--ink\` |
| typography | 채택 | \`--fs-body\` |
| spacing | 채택 | \`--space-2\`, \`--gutter\` |
| spacing | 기각 | \`--space-1\`, \`--space-0\` |
| borderRadius | 기각 | \`--radius-sm\` |
| shadows | 채택 | \`--shadow-1\` |"

run() { python3 "$SCRIPTS/check_token_disposition.py" "$@" 2>&1; }
check() { # check <빌드경로>
  run --spec-only "$1/design-spec.md" "$1/design-tokens.json" "$1/design-ref"
}

# TD1 정상 — 기각한 2px·0px·12px 가 시안에 없다
d=$(mk td1 "$FULL_OK" "gap: 20px; color: #D0727A"); out=$(check "$d"); rc=$?; assert TD1_정상 0 "발견 0건" "FINDING" $rc "$out"

# TD2 T1a 미처분 — --gutter 를 표에서 뺀다
d=$(mk td2 "${FULL_OK/, \`--gutter\`/}" "gap: 20px"); out=$(check "$d"); rc=$?; assert TD2_미처분 2 "T1a 미처분" - $rc "$out"

# TD3 T1b 풀 밖
d=$(mk td3 "$FULL_OK
| spacing | 채택 | \`--nope\` |" "gap: 20px"); out=$(check "$d"); rc=$?; assert TD3_풀밖 2 "T1b 풀 밖 토큰" - $rc "$out"

# TD4 T1b 중복
d=$(mk td4 "$FULL_OK
| spacing | 기각 | \`--gutter\` |" "gap: 20px"); out=$(check "$d"); rc=$?; assert TD4_중복 2 "T1b 중복 처분" - $rc "$out"

# TD5 ★ 이번 결함의 회귀 — 기각한 --space-1(2px) 를 시안이 쓴다
d=$(mk td5 "$FULL_OK" "padding: 2px 2px 4px"); out=$(check "$d"); rc=$?
assert TD5_기각정당성 2 "T1c 기각 정당성" - $rc "$out"
assert TD5_토큰명 2 "--space-1 = 2px" - $rc "$out"

# TD6 positive-control — 기각한 12px 가 시안에 없다
d=$(mk td6 "$FULL_OK" "gap: 20px"); out=$(check "$d"); rc=$?; assert TD6_무발견 0 "발견 0건" "--radius-sm" $rc "$out"

# TD7 비변별 값 — 기각한 --space-0(0px) 가 시안 margin:0 에 걸려도 발견 아님
d=$(mk td7 "$FULL_OK" "margin: 0; padding: 0"); out=$(check "$d"); rc=$?
assert TD7_비변별 0 "비변별 제외 1" "--space-0" $rc "$out"

# TD8 rem↔px 환산 — 시안이 0.125rem(=2px) 로 쓴다
d=$(mk td8 "$FULL_OK" "padding: 0.125rem"); out=$(check "$d"); rc=$?; assert TD8_rem환산 2 "--space-1 = 2px" - $rc "$out"

# TD9 귀속 불가 — --space-1 을 기각하고 같은 값 2px 를 가진 토큰을 채택하면 귀속 불가
d="$T/td9"; mkdir -p "$d/design-ref"
printf '# 명세\n\n## 9. 토큰 전수 처분\n\n%s\n| colors | 채택 | `--accent` |\n| spacing | 채택 | `--twin` |\n| spacing | 기각 | `--space-1` |\n' "$HDR" > "$d/design-spec.md"
cat > "$d/design-tokens.json" <<'JSON'
{"colors":{"--accent":"#D0727A"},"spacing":{"--space-1":"2px","--twin":"2px"},"arbitraryValues":[]}
JSON
printf '<div style="padding: 2px"></div>\n' > "$d/design-ref/screen.dc.html"
out=$(check "$d"); rc=$?; assert TD9_귀속불가 0 "귀속 불가 제외 1" "--space-1" $rc "$out"

# TD10 절은 있는데 고정 헤더가 없다 → FINDING (탈출구 대칭 가드)
d=$(mk td10 "- 채택(2): \`--accent\`, \`--ink\`" "gap: 20px"); out=$(check "$d"); rc=$?
assert TD10_판형위반 2 "고정 헤더" - $rc "$out"

# TD11 절 자체가 없다 → warn + exit 0 (레거시 비차단)
d="$T/td11"; mkdir -p "$d/design-ref"
printf '# 명세\n\n## 3. 화면\n\n산문뿐이다.\n' > "$d/design-spec.md"
cp "$T/td1/design-tokens.json" "$d/design-tokens.json"
printf '<div style="gap: 20px"></div>\n' > "$d/design-ref/screen.dc.html"
out=$(check "$d"); rc=$?; assert TD11_레거시 0 "레거시 산문 판형" "FINDING" $rc "$out"

# TD12 화면 범위 — screen-meta 의 source_sha256 이 지목한 dc 만 본다
d=$(mk td12 "$FULL_OK" "gap: 20px")
printf '<div style="padding: 2px"></div>\n' > "$d/design-ref/other.dc.html"
SHA=$(python3 -c "import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" "$d/design-ref/screen.dc.html")
printf '{"screen_label":"s","source_sha256":"%s"}\n' "$SHA" > "$d/screen-meta.json"
out=$(run --spec-only "$d/design-spec.md" "$d/design-tokens.json" "$d/design-ref" --screen-meta "$d/screen-meta.json"); rc=$?
assert TD12_화면범위 0 "시안 범위 screen.dc.html" "--space-1" $rc "$out"
out=$(check "$d"); rc=$?; assert TD12_범위없으면발견 2 "--space-1 = 2px" - $rc "$out"

# TD13 연속 블록 한정 — 처분 표 아래의 다른 표를 먹지 않는다
d=$(mk td13 "$FULL_OK

## 10. 다른 절

| 화면 | 상태 | 비고 |
|---|---|---|
| 목록 | 기본 | 없음 |" "gap: 20px"); out=$(check "$d"); rc=$?
assert TD13_연속블록 0 "발견 0건" "판형 위반" $rc "$out"

# TD14 중첩 dict 언랩 — typography 가 {"size": "…"} 판형이어도 대조된다
d="$T/td14"; mkdir -p "$d/design-ref"
printf '# 명세\n\n## 9. 토큰 전수 처분\n\n%s\n| typography | 기각 | `--fs-x` |\n' "$HDR" > "$d/design-spec.md"
printf '{"typography":{"--fs-x":{"size":"14px"}},"arbitraryValues":[]}\n' > "$d/design-tokens.json"
printf '<div style="font-size: 14px"></div>\n' > "$d/design-ref/screen.dc.html"
out=$(check "$d"); rc=$?; assert TD14_중첩언랩 2 "--fs-x = 14px" - $rc "$out"

# TD15 var(--토큰) 인용도 사용이다 (값이 시안에 리터럴로 없어도)
d=$(mk td15 "$FULL_OK" "padding: var(--space-1)"); out=$(check "$d"); rc=$?
assert TD15_var인용 2 "--space-1" - $rc "$out"

# TD16 screen-meta 파일 부재 → warn 하고 계속(미실행 exit 1 이 아니다)
d=$(mk td16 "$FULL_OK" "gap: 20px")
out=$(run --spec-only "$d/design-spec.md" "$d/design-tokens.json" "$d/design-ref" --screen-meta "$d/nope.json"); rc=$?
assert TD16_meta부재 0 "screen-meta 없음" - $rc "$out"

# U1 사용법
out=$(run); rc=$?; assert U1_사용법 1 "사용:" - $rc "$out"
out=$(run --spec-only "$T/nope.md" "$T/td1/design-tokens.json" "$T/td1/design-ref"); rc=$?
assert U2_파일부재 1 "파일 없음" - $rc "$out"

# DET 결정론 — 같은 입력 2회 byte 동일
a=$(check "$T/td5"); b=$(check "$T/td5")
if [ "$a" = "$b" ]; then PASS=$((PASS+1)); echo "PASS DET_결정론"; else FAIL=$((FAIL+1)); echo "FAIL DET_결정론"; fi

echo
echo "fixtures_token_disposition: PASS=$PASS FAIL=$FAIL"
[ "$FAIL" = 0 ]
