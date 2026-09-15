#!/usr/bin/env bash
# dddjango-web 클리핑 여유 정적 검사(check_clip_clearance) 자기 회귀 픽스처.
#   CC1(패딩 충분) ↔ CC2(overflow-y:auto + 패딩 0 = 이번 결함의 회귀 · 축 전파로 좌우도 발견)
#   CC3(overflow:hidden 도 클립) · CC4(서브트리에 링 보유 요소 없음 → 인벤토리)
#   CC5(inset 만 = 링 아님) · CC6(0 0 0 3px 를 네 변 3px 로 파스) · CC7(color-mix 의 30 이 길이로 안 샘)
#   CC8(blur>0 판정 제외) · CC9(extends 로 block 을 채우는 자식까지 본다)
#   CC10(자기 자신 제외 — 요소의 overflow 는 자기 그림자를 자르지 않는다)
#   U1(사용법) · DET(결정론)
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
  printf ':root { --focus-ring: 0 0 0 3px rgba(208,114,122,.30); }\n%s\n' "$2" > "$d/static/css/app.css"
  printf '%s\n' "$3" > "$d/page/page.html"
  echo "$d"
}
run() { python3 "$SCRIPTS/check_clip_clearance.py" "$@" 2>&1; }

RING='.field:focus-within { box-shadow: var(--focus-ring); }'
BOX='<div class="scroll"><div class="field"><input type="text"></div></div>'

# CC1 패딩 충분 → 발견 0
d=$(mk cc1 "$RING
.scroll { overflow-y: auto; padding: 3px 3px 4px; }" "$BOX")
out=$(run "$d"); rc=$?; assert CC1_패딩충분 0 "발견 0건" "FINDING" $rc "$out"

# CC2 ★ 이번 결함의 회귀 — overflow-y:auto 인데 패딩 0. 축 전파로 좌우도 나와야 한다.
d=$(mk cc2 "$RING
.scroll { overflow-y: auto; }" "$BOX")
out=$(run "$d"); rc=$?
assert CC2_결함회귀 2 ".scroll" - $rc "$out"
assert CC2_축전파_좌 2 "left 여유 0px < 확장 3px" - $rc "$out"
assert CC2_축전파_우 2 "right 여유 0px < 확장 3px" - $rc "$out"

# CC3 overflow:hidden 도 클립이다 (가장 단단하다)
d=$(mk cc3 "$RING
.scroll { overflow: hidden; }" "$BOX")
out=$(run "$d"); rc=$?; assert CC3_hidden 2 "overflow hidden" - $rc "$out"

# CC4 서브트리에 링 보유 요소가 없다 → 인벤토리(발견 아님)
d=$(mk cc4 "$RING
.scroll { overflow: hidden; }" '<div class="scroll"><span>글자만</span></div>')
out=$(run "$d"); rc=$?; assert CC4_노이즈절단 0 "링 보유 요소 없음" "FINDING" $rc "$out"

# CC5 inset 그림자는 링이 아니다
d=$(mk cc5 ".field:focus-within { box-shadow: inset 0 0 0 3px rgba(0,0,0,.3); }
.scroll { overflow: hidden; }" "$BOX")
out=$(run "$d"); rc=$?; assert CC5_inset제외 0 "링 규칙 0" "FINDING" $rc "$out"

# CC6 0 0 0 3px 를 네 변 3px 로 — 단위 없는 0 을 길이로 받아야 한다
d=$(mk cc6 "$RING
.scroll { overflow: hidden; padding: 3px 3px 3px 2px; }" "$BOX")
out=$(run "$d"); rc=$?
assert CC6_좌만부족 2 "left 여유 2px < 확장 3px" "right 여유" $rc "$out"

# CC7 color-mix 안의 30 이 길이로 새면 안 된다
d=$(mk cc7 ".field:focus-within { box-shadow: 0 0 0 3px color-mix(in srgb,#D0727A 30%,transparent); }
.scroll { overflow: hidden; padding: 3px; }" "$BOX")
out=$(run "$d"); rc=$?; assert CC7_색함수 0 "발견 0건" "FINDING" $rc "$out"

# CC8 blur>0 은 판정에서 빼고 고지한다
d=$(mk cc8 ".field:focus-within { box-shadow: 0 0 20px 0 rgba(0,0,0,.3); }
.scroll { overflow: hidden; padding: 1px; }" "$BOX")
out=$(run "$d"); rc=$?; assert CC8_blur제외 0 "blur>0 그림자 1건은 판정 제외" "FINDING" $rc "$out"

# CC9 extends — 컨테이너는 base 에, 링 보유 요소는 자식 템플릿에
d="$T/cc9/web"; mkdir -p "$d/static/css" "$d/page"
printf ':root { --focus-ring: 0 0 0 3px rgba(208,114,122,.30); }\n%s\n.scroll { overflow-y: auto; }\n' "$RING" > "$d/static/css/app.css"
printf '<div class="scroll">{%% block body %%}{%% endblock %%}</div>\n' > "$d/page/base.html"
printf '{%% extends "page/base.html" %%}\n{%% block body %%}<div class="field"><input type="text"></div>{%% endblock %%}\n' > "$d/page/child.html"
out=$(run "$d"); rc=$?; assert CC9_extends추적 2 ".scroll" - $rc "$out"

# CC10 자기 자신 제외 — textarea 가 스스로 overflow:auto 이고 자손이 없다
d=$(mk cc10 ".ta:focus-visible { box-shadow: var(--focus-ring); }
.ta { overflow: auto; }" '<textarea class="ta"></textarea>')
out=$(run "$d"); rc=$?; assert CC10_자기제외 0 "발견 0건" "FINDING" $rc "$out"

# CC11 콤마 목록 — 앞 멤버의 링과 앞 멤버 클리핑도 본다(마지막 하나만 보면 미탐)
d=$(mk cc11 ".field:focus-within,
.other:focus-visible { box-shadow: var(--focus-ring); }
.scroll,
.other-scroll { overflow-y: auto; }" "$BOX")
out=$(run "$d"); rc=$?; assert CC11_콤마목록 2 ".scroll" - $rc "$out"

# CC12 패딩이 overflow 와 다른 규칙에 선언 — 캐스케이드로 읽어야 오탐이 안 난다
d=$(mk cc12 "$RING
.scroll { overflow-y: auto; }
.scroll { padding: 3px 3px 4px; }" "$BOX")
out=$(run "$d"); rc=$?; assert CC12_캐스케이드 0 "발견 0건" "FINDING" $rc "$out"

# CC13 논리 속성 padding-inline/block
d=$(mk cc13 "$RING
.scroll { overflow-y: auto; padding-inline: 3px; padding-block: 4px; }" "$BOX")
out=$(run "$d"); rc=$?; assert CC13_논리속성 0 "발견 0건" "FINDING" $rc "$out"

# CC14 !important 가 값 파싱을 깨지 않는다
d=$(mk cc14 "$RING
.scroll { overflow-y: auto; padding: 3px 3px 4px !important; }" "$BOX")
out=$(run "$d"); rc=$?; assert CC14_important 0 "발견 0건" "FINDING" $rc "$out"

# CC15 calc() 는 0 이 아니라 «미해석» 이다 (멀쩡한 빌드를 확정으로 반송하면 안 된다)
d=$(mk cc15 "$RING
.scroll { overflow-y: auto; padding: calc(var(--x) + 2px); }" "$BOX")
out=$(run "$d"); rc=$?; assert CC15_calc미해석 0 "패딩 미해석" "확정" $rc "$out"

# CC16 전역 :focus-visible 경로 — 기반 셀렉터가 비어도 포커스 가능 요소가 링을 진다
d=$(mk cc16 ":focus-visible { box-shadow: var(--focus-ring); }
.scroll { overflow-y: auto; }" '<div class="scroll"><button type="button">가</button></div>')
out=$(run "$d"); rc=$?; assert CC16_전역링 2 ".scroll" - $rc "$out"

# CC17 심각도 2단 — 0 < 여유 < 확장 은 «경미»
d=$(mk cc17 "$RING
.scroll { overflow-y: auto; padding: 2px; }" "$BOX")
out=$(run "$d"); rc=$?; assert CC17_경미 2 "[경미]" "[확정]" $rc "$out"

# CC18 blur>0 은 판정 규칙에서 빠지고 고지만 남는다(전역 최대 지배 방지)
d=$(mk cc18 "$RING
.deco:checked + .box { box-shadow: 0 1px 3px rgba(0,0,0,.08); }
.scroll { overflow-y: auto; padding: 3px 3px 4px; }" "$BOX")
out=$(run "$d"); rc=$?; assert CC18_blur비지배 0 "발견 0건" "FINDING" $rc "$out"

# CC11 ★ Django 주석 속 리터럴 태그는 링 보유 요소가 아니다 — 주석을 스트립하지 않으면
#      산문이 발견을 만든다(실결함: 부품 docstring 의 <button> 이 오탐으로 잡혔다).
d=$(mk cc11 "$RING
.scroll { overflow-y: auto; }" \
'<div class="scroll">{% comment %}예시: <div class="field"><input type="text"></div>{% endcomment %}{# <div class="field">도 예시 #}<p>글자만</p></div>')
out=$(run "$d"); rc=$?; assert CC11_주석속_리터럴마크업 0 "링 보유 요소 없음" "FINDING" $rc "$out"

# U1 사용법 · 디렉터리 아님
out=$(run); rc=$?; assert U1_사용법 1 "사용:" - $rc "$out"
out=$(run "$T/nope"); rc=$?; assert U2_경로부재 1 "디렉터리가 아니다" - $rc "$out"

# DET 결정론
a=$(run "$T/cc2/web"); b=$(run "$T/cc2/web")
if [ "$a" = "$b" ]; then PASS=$((PASS+1)); echo "PASS DET_결정론"; else FAIL=$((FAIL+1)); echo "FAIL DET_결정론"; fi

echo
echo "fixtures_clip_clearance: PASS=$PASS FAIL=$FAIL"
[ "$FAIL" = 0 ]
