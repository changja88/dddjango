#!/usr/bin/env bash
# dddjango-web 링 중첩 정적 검사(check_focus_ring) 자기 회귀 픽스처.
#   FR1(전역 링 + 면제 없는 자손 = 이번 결함의 회귀 · 직각 링) · FR2(box-shadow:none 면제)
#   FR3(sr-only 은닉 면제 — A8 .choice-pair__input 실측 오탐) · FR4(:where 타입 나열도 링이다)
#   FR5(타입 링은 그 태그만) · FR6(조상 스코프는 발견 줄에 표기) · FR7(:not 예외는 면제)
#   FR8(자손의 자기 그림자 선언은 인벤토리 — 교체이지 누락이 아니다)
#   FR9(링 규칙 0건은 «발견 0» 이 아니라 «판정 안 함») · FR10(:is(.x,.y) 는 전역이 아니다)
#   FR11(radius 일치면 직각 표기 없음) · FR12(inset 만은 바깥 링이 아니다)
#   FR13 ★ 순서 함정 — 면제 대상이 먼저 나와도 뒤의 미면제 요소가 발견돼야 한다
#   U1·U2(사용법) · DET(결정론)
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

mk() { # mk <이름> <css 본문> <템플릿 본문>
  local d="$T/$1/web"; mkdir -p "$d/static/css" "$d/page"
  printf ':root { --focus-ring: 0 0 0 3px rgba(208,114,122,.30); --r-field: 16px; }\n%s\n' "$2" > "$d/static/css/app.css"
  printf '%s\n' "$3" > "$d/page/page.html"
  echo "$d"
}
run() { python3 "$SCRIPTS/check_focus_ring.py" "$@" 2>&1; }

GLOBAL=':focus-visible { outline: none; box-shadow: var(--focus-ring); }'
WRAP='.ctl:focus-within { box-shadow: var(--focus-ring); }
.ctl { border-radius: var(--r-field); }'
BOX='<div class="ctl"><select class="sel"><option>x</option></select></div>'

# FR1 ★ 이번 결함의 회귀 — 전역 링이 래퍼 안 native select 에 직각으로 겹친다.
d=$(mk fr1 "$GLOBAL
$WRAP" "$BOX")
out=$(run "$d"); rc=$?
assert FR1_이중링_직각 2 "직각 링" "-" $rc "$out"
assert FR1_대상표기 2 '<select class="sel">' "-" $rc "$out"

# FR2 자손이 box-shadow:none 으로 억제되면 이중이 아니다.
d=$(mk fr2 "$GLOBAL
$WRAP
.sel:focus-visible { box-shadow: none; }" "$BOX")
out=$(run "$d"); rc=$?; assert FR2_none억제 0 "발견 0건" "FINDING" $rc "$out"

# FR3 sr-only 로 숨긴 입력은 링을 그릴 수 없다(A8 .choice-pair__input 실측 오탐).
d=$(mk fr3 "$GLOBAL
$WRAP
.sel { position: absolute; width: 1px; height: 1px; clip: rect(0, 0, 0, 0); }" "$BOX")
out=$(run "$d"); rc=$?; assert FR3_은닉면제 0 "발견 0건" "FINDING" $rc "$out"

# FR4 :where 타입 나열 — last_compound 는 'input)' 으로 자르지만 이 검사기는 펼친다.
d=$(mk fr4 ":where(a, button, select):focus-visible { box-shadow: var(--focus-ring); }
$WRAP" "$BOX")
out=$(run "$d"); rc=$?
assert FR4_where타입 2 "타입 링" "-" $rc "$out"
assert FR4_발견 2 "FINDING" "-" $rc "$out"

# FR5 타입 링은 그 태그에만 걸린다 — 대상이 select 뿐인데 링은 textarea 용이다.
d=$(mk fr5 "textarea:focus-visible { box-shadow: var(--focus-ring); }
$WRAP" "$BOX")
out=$(run "$d"); rc=$?; assert FR5_타입불일치 0 "발견 0건" "FINDING" $rc "$out"

# FR6 조상 스코프가 붙은 전역 규칙은 범위 밖 요소에 안 걸린다 — 발견 줄에 표기한다.
d=$(mk fr6 ".theme-dark :focus-visible { box-shadow: var(--focus-ring); }
$WRAP" "$BOX")
out=$(run "$d"); rc=$?; assert FR6_스코프표기 2 "조상 스코프 있음" "-" $rc "$out"

# FR7 셀렉터가 명시한 :not 예외는 면제다.
d=$(mk fr7 ":focus-visible:not(.sel) { box-shadow: var(--focus-ring); }
$WRAP" "$BOX")
out=$(run "$d"); rc=$?; assert FR7_not예외 0 "발견 0건" "FINDING" $rc "$out"

# FR8 자손이 자기 :focus 그림자를 선언했으면 «교체» 다 — 인벤토리로 낸다.
d=$(mk fr8 "$GLOBAL
$WRAP
.sel:focus-visible { box-shadow: 0 0 0 2px blue; }" "$BOX")
out=$(run "$d"); rc=$?
assert FR8_자기선언_인벤토리 0 "자기 :focus 그림자를 선언했다" "FINDING" $rc "$out"

# FR9 ★ 링 규칙이 없으면 «발견 0» 이 아니라 «판정 안 함» 이다(무증상 통과 금지).
d=$(mk fr9 ".ctl { border-radius: var(--r-field); }" "$BOX")
out=$(run "$d"); rc=$?
assert FR9_판정안함 0 "이중 링 판정을 수행하지 않았다" "발견 0건" $rc "$out"

# FR10 :is(.x, .y) 는 클래스로 좁힌 규칙이라 전역이 아니다.
d=$(mk fr10 ":is(.x, .y):focus-visible { box-shadow: var(--focus-ring); }
$WRAP" "$BOX")
out=$(run "$d"); rc=$?; assert FR10_클래스좁힘 0 "판정을 수행하지 않았다" "FINDING" $rc "$out"

# FR11 안팎 radius 가 같으면 이중이되 «직각 링» 은 아니다.
d=$(mk fr11 "$GLOBAL
$WRAP
.sel { border-radius: var(--r-field); }" "$BOX")
out=$(run "$d"); rc=$?; assert FR11_radius일치 2 "FINDING" "직각 링" $rc "$out"

# FR12 inset 만 있는 그림자는 바깥 링이 아니다.
d=$(mk fr12 ":focus-visible { box-shadow: inset 0 0 0 3px red; }
.ctl:focus-within { box-shadow: inset 0 0 0 3px red; }
.ctl { border-radius: var(--r-field); }" "$BOX")
out=$(run "$d"); rc=$?; assert FR12_inset 0 "판정을 수행하지 않았다" "FINDING" $rc "$out"

# FR13 ★ 순서 함정 회귀 — 면제 대상(input)이 미면제 대상(select)보다 먼저 나온다.
#      중복 제거를 면제 판정 «앞» 에 두면 발견이 통째로 사라진다(원형에서 실제로 밟았다).
d=$(mk fr13 "$GLOBAL
$WRAP
.inp:focus-visible { box-shadow: none; }" \
'<div class="ctl"><input class="inp"><select class="sel"><option>x</option></select></div>')
out=$(run "$d"); rc=$?
assert FR13_순서함정 2 '<select class="sel">' "-" $rc "$out"

# U1·U2 사용법 — 미실행(exit 1)은 통과가 아니다.
out=$(run 2>&1); rc=$?; assert U1_인자없음 1 "사용:" "-" $rc "$out"
out=$(run "$T/없는경로" 2>&1); rc=$?; assert U2_디렉터리아님 1 "디렉터리가 아니다" "-" $rc "$out"

# DET 같은 입력이면 같은 출력이다.
d=$(mk det "$GLOBAL
$WRAP" "$BOX")
a=$(run "$d"); b=$(run "$d")
if [ "$a" = "$b" ]; then PASS=$((PASS+1)); echo "PASS DET_결정론"; else
  FAIL=$((FAIL+1)); echo "FAIL DET_결정론"; diff <(echo "$a") <(echo "$b") | head -10 | sed 's/^/    /'
fi

echo "fixtures_focus_ring: PASS=$PASS FAIL=$FAIL"
[ "$FAIL" = 0 ]
