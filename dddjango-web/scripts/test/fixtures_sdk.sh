#!/usr/bin/env bash
# dddjango-web 공식 SDK 등재(WV · sdk_vendor.py · WS6/WP1/WP2/WP3 벤더 분기) 픽스처 — 합성 프로젝트 · 카카오 꼴 시험 SDK ·
# 가짜 fetch(네트워크 0). 각 red 에 양성 짝을 둔다. id 는 설계 픽스처 표의 K 번호 그대로다.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPTS="$(cd "$HERE/.." && pwd)"
PASS=0; FAIL=0

FX() { python3 "$HERE/sdk_fixture.py" "$@" 2>&1; }
BS() { python3 "$SCRIPTS/backstop.py" "$@" 2>&1; }
SV() { python3 "$SCRIPTS/sdk_vendor.py" "$@" 2>&1; }
G() { git -C "$1" -c user.name=t -c user.email=t@t "${@:2}"; }
commit() { G "$1" add -A >/dev/null; G "$1" commit -qm "$2"; G "$1" rev-parse HEAD; }

check() { # check <이름> <기대 exit> <실제 exit> <출력> ['<고정 문자열>=<개수|+>']…
  local name="$1" want="$2" got="$3" out="$4" ok=1 why="" spec pat n c
  shift 4
  [ "$got" != "$want" ] && { ok=0; why="exit=$got want=$want"; }
  for spec in "$@"; do
    pat="${spec%=*}"; n="${spec##*=}"
    c=$(grep -cF -- "$pat" <<<"$out" || true)
    if [ "$n" = "+" ]; then [ "$c" -ge 1 ] || { ok=0; why="$why [$pat]=$c(≥1)"; }
    else [ "$c" = "$n" ] || { ok=0; why="$why [$pat]=$c(≠$n)"; }; fi
  done
  if [ $ok = 1 ]; then PASS=$((PASS+1)); echo "PASS $name"; else
    FAIL=$((FAIL+1)); echo "FAIL $name —$why"; echo "$out" | head -25 | sed 's/^/    /'; fi
}

must() { # must <이름> <명령…> — 준비 단계가 실패하면 FAIL 로 센다(헛통과 방지)
  local name="$1" out; shift
  out=$("$@" 2>&1) || { FAIL=$((FAIL+1)); echo "FAIL $name(준비 실패)"; echo "$out" | tail -5 | sed 's/^/    /'; return 1; }
}
NAVER='{"use_scope": ["Kakao.init"], "namespace_members": {}, "namespace_words": {"API": ["사용자 정보"], "Auth": ["로그인"], "Share": ["공유"]}}'

T="$(mktemp -d)"
trap 'rm -rf "$T"' EXIT
CHART="web/chart/chart/view/chart.html"
FEATURE="web/static/js/chart_kakao_share.js"

page_ok() { # 페이지 block 안 SDK 태그(기능 JS 앞) · 키 data 속성 `{{ }}`
  cat > "$1/$CHART" <<'EOF'
{% extends "base.html" %}
{% load static %}
{% block content %}
<div data-chart-kakao-share data-kakao-javascript-key="{{ state.kakao_javascript_key }}">
  <button type="button" data-chart-kakao-share-button>카카오톡</button>
</div>
{% endblock %}
{% block scripts %}
<script src="{% static 'web/vendor/kakao_js_sdk/kakao.min.js' %}" defer></script>
<script src="{% static 'web/js/chart_kakao_share.js' %}" defer></script>
{% endblock scripts %}
EOF
  cat > "$1/$FEATURE" <<'EOF'
(() => {
  const ROOT = "[data-chart-kakao-share]";
  function initialize(root) {
    if (!window.Kakao) return "transient";
    if (window.Kakao.isInitialized()) return "ready";
    const key = root.dataset.kakaoJavascriptKey;
    if (!key) return "config";
    window.Kakao.init(key);
    return "ready";
  }
  document.addEventListener("click", (event) => {
    const root = event.target.closest(ROOT);
    if (!root || initialize(root) !== "ready") return;
    window.Kakao.Share.sendDefault({ objectType: "feed" });
  });
})();
EOF
}

# ---------- 기준 프로젝트: 설치(격리 커밋) + 페이지 사용
FX mkproj "$T/base" >/dev/null
OUT=$(FX install "$T/base"); E=$?
check "K0 install(본인 직접) exit 0 · 격리 커밋" 0 "$E" "$OUT" "[sdk] 설치 kakao_js_sdk=1" "commit=1"
page_ok "$T/base"
commit "$T/base" "page" >/dev/null
newp() { rm -rf "$T/$1"; cp -R "$T/base" "$T/$1"; echo "$T/$1"; }
base_of() { G "$1" rev-parse HEAD; }

# ---------- K1: 정상 등재 + 표지 + 페이지 block 안 SDK 태그 + 키 {{ }}
P=$(newp k1); B=$(G "$P" rev-parse HEAD~1)
OUT=$(BS "$P" --diff-base "$B" --only wv,wp,ws,wn); E=$?
check "K1 정상 등재 gated(페이지·기능 JS added) exit 0" 0 "$E" "$OUT" "BLOCKER=0"
OUT=$(SV verify "$P"); E=$?
check "K1 verify exit 0" 0 "$E" "$OUT" "발견 0건=1"
OUT=$(BS "$P" --all --only wv); E=$?
check "K1 전역(--all) WV 0" 0 "$E" "$OUT" "BLOCKER=0"

# ---------- K2: 사본 1바이트 수정(기준점 이전 · gated) / 운영자 sha384 불일치(결속 재계산)
P=$(newp k2); printf 'x' >> "$P/web/static/vendor/kakao_js_sdk/kakao.min.js"; commit "$P" tamper >/dev/null; B=$(base_of "$P")
OUT=$(BS "$P" --diff-base "$B" --only wv); E=$?
check "K2a 사본 변조 — gated 에서도 WV2" 2 "$E" "$OUT" "[WV2] BLOCKER=1" "sha256 불일치=1"
P=$(newp k2b); FX edit "$P" kakao_js_sdk '{"upstream_integrity": "sha384-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"}' --rebind >/dev/null
OUT=$(BS "$P" --diff-base HEAD --only wv2,wv3); E=$?
check "K2b 운영자 sha384 불일치 — WV2" 2 "$E" "$OUT" "[WV2] BLOCKER=1" "공개 무결성(sha384) 불일치=1" "[WV3]=0"

# ---------- K3: 결속 뒤 service_api 만 수정 / 출처 «발주 고정 ⓐ» / at 시간대 없음
P=$(newp k3a); FX edit "$P" kakao_js_sdk '{"service_api": "바꾼 목적"}' >/dev/null
OUT=$(BS "$P" --diff-base HEAD --only wv3); E=$?
check "K3a 결속 뒤 칸 수정 — WV3" 2 "$E" "$OUT" "승인 결속 불일치=1"
P=$(newp k3b); FX edit "$P" kakao_js_sdk '{"approval.source": "발주 고정 ⓐ 09-28"}' --rebind >/dev/null
OUT=$(BS "$P" --diff-base HEAD --only wv3); E=$?
check "K3b 출처 «발주 고정 ⓐ» — WV3" 2 "$E" "$OUT" "출처 꼴 위반=1"
P=$(newp k3c); FX edit "$P" kakao_js_sdk '{"approval.at": "2026-10-01 15:00"}' --rebind >/dev/null
OUT=$(BS "$P" --diff-base HEAD --only wv3); E=$?
check "K3c at 시간대 없음 — WV3" 2 "$E" "$OUT" "approval.at 꼴 위반=1"

# ---------- K4: http 원본 · 원본 호스트 운영자 밖 · sha 꼴 · file 이 static/js · 모르는 칸
for pair in 'http|{"source_url": "http://t1.kakaocdn.net/kakao_js_sdk/2.8.3/kakao.min.js"}|https 여야' \
            'host|{"source_url": "https://cdn.example.org/kakao.min.js"}|점 경계 하위가 아니다' \
            'sha|{"sha256": "XYZ"}|sha256 꼴 위반' \
            'file|{"file": "static/js/kakao.min.js"}|static/vendor/<id>/<파일>' \
            'waiver|{"waiver": true}|모르는 칸'; do
  IFS='|' read -r tag patch want <<<"$pair"
  P=$(newp "k4$tag"); FX edit "$P" kakao_js_sdk "$patch" --rebind >/dev/null
  OUT=$(BS "$P" --diff-base HEAD --only wv1); E=$?
  check "K4 $tag — WV1" 2 "$E" "$OUT" "$want=+"
done

# ---------- K5: id html2canvas / 짝 kakao_js_sdk
P=$(newp k5); FX edit "$P" kakao_js_sdk '{}' --rename html2canvas >/dev/null
OUT=$(BS "$P" --diff-base HEAD --only wv4); E=$?
check "K5a id html2canvas — WV4 덫" 2 "$E" "$OUT" "[WV4] BLOCKER=1" "html2canvas=+"
P=$(newp k5b)
OUT=$(BS "$P" --diff-base HEAD --only wv4); E=$?
check "K5b 짝 kakao_js_sdk — WV4 0" 0 "$E" "$OUT" "BLOCKER=0"

# ---------- K6: 목록 있음 + 이번 실행에 미등재 디렉터리 · 직속 파일 · 등재 id 안 하위
P=$(newp k6); B=$(base_of "$P")
mkdir -p "$P/web/static/vendor/html2canvas" "$P/web/static/vendor/kakao_js_sdk/2.8.3"
echo 'x' > "$P/web/static/vendor/html2canvas/html2canvas.min.js"
echo 'r' > "$P/web/static/vendor/readme.txt"
echo 'y' > "$P/web/static/vendor/kakao_js_sdk/2.8.3/x.js"
OUT=$(BS "$P" --diff-base "$B" --only wv5,wv13,ws6,wp1); E=$?
check "K6 WV5 1 + WV13 2 + WS6 3 + WP1 2" 2 "$E" "$OUT" "[WV5] BLOCKER=1" "[WV13] BLOCKER=2" "[WS6] BLOCKER=3" "[WP1] BLOCKER=2"

# ---------- K7: web/sdk_registry.json 허용 / web/vendor.json
P=$(newp k7); B=$(G "$P" rev-parse HEAD~2)
OUT=$(BS "$P" --diff-base "$B" --only ws1); E=$?
check "K7a sdk_registry.json 은 web/ 직속 허용" 0 "$E" "$OUT" "BLOCKER=0"
echo '{}' > "$P/web/vendor.json"
OUT=$(BS "$P" --diff-base "$B" --only ws1); E=$?
check "K7b web/vendor.json — WS1" 2 "$E" "$OUT" "[WS1] BLOCKER=1"

# ---------- K8: 벤더 태그 — 기능 JS 뒤 · base block 뒤 · async · type=module · nomodule · base+page 중복
vendor_case() { # vendor_case <이름> <페이지 scripts 블록 본문> [base 끝 대체]
  local P; P=$(newp "k8$1"); local B; B=$(base_of "$P")
  printf '{%% extends "base.html" %%}\n{%% load static %%}\n{%% block scripts %%}\n%s\n{%% endblock scripts %%}\n' "$2" > "$P/$CHART"
  if [ -n "${3:-}" ]; then printf '%s\n' "$3" > "$P/web/base/base.html"; fi
  BS "$P" --diff-base "$B" --only wp2
}
SDKTAG="<script src=\"{% static 'web/vendor/kakao_js_sdk/kakao.min.js' %}\" defer></script>"
FTAG="<script src=\"{% static 'web/js/chart_kakao_share.js' %}\" defer></script>"
OUT=$(vendor_case after "$FTAG
$SDKTAG"); E=$?
check "K8a 기능 JS 뒤 — WP2" 2 "$E" "$OUT" "기능 JS 태그보다 뒤=1"
BASE_AFTER="{% load static %}
<html><body>{% block content %}{% endblock %}
<script src=\"{% static 'web/htmx/htmx.min.js' %}\" defer></script>
{% block scripts %}{% endblock scripts %}
$SDKTAG
</body></html>"
OUT=$(vendor_case baseafter "$FTAG" "$BASE_AFTER"); E=$?
check "K8b base 의 block 여는 줄 뒤 — WP2" 2 "$E" "$OUT" "여는 줄보다 뒤=1"
OUT=$(vendor_case async "<script src=\"{% static 'web/vendor/kakao_js_sdk/kakao.min.js' %}\" defer async></script>
$FTAG"); E=$?
check "K8c async — WP2" 2 "$E" "$OUT" "async 실행 금지=1"
OUT=$(vendor_case module "<script src=\"{% static 'web/vendor/kakao_js_sdk/kakao.min.js' %}\" type=\"module\" defer></script>
$FTAG"); E=$?
check "K8d type=module — WP2" 2 "$E" "$OUT" "src·defer(·CSP nonce)만=1"
OUT=$(vendor_case nomodule "<script src=\"{% static 'web/vendor/kakao_js_sdk/kakao.min.js' %}\" nomodule defer></script>
$FTAG"); E=$?
check "K8e nomodule — WP2" 2 "$E" "$OUT" "src·defer(·CSP nonce)만=1"
BASE_DUP="{% load static %}
<html><body>{% block content %}{% endblock %}
<script src=\"{% static 'web/htmx/htmx.min.js' %}\" defer></script>
$SDKTAG
{% block scripts %}{% endblock scripts %}
</body></html>"
OUT=$(vendor_case dup "$SDKTAG
$FTAG" "$BASE_DUP"); E=$?
check "K8f base+page 중복 — 페이지 파일에 1" 2 "$E" "$OUT" "base·페이지 중복 로드=1" "web/chart/chart/view/chart.html=1"
OUT=$(vendor_case pair "$SDKTAG
$FTAG"); E=$?
check "K8g 짝: block 안 · 기능 JS 앞 · defer — 0" 0 "$E" "$OUT" "BLOCKER=0"

# ---------- K9: 이번 실행이 목록을 지움(사본·태그는 기준점 이전) — 슬라이스 커밋 / 미커밋
mk_build() { # mk_build <프로젝트> <git_snapshot> [<슬라이스 커밋들 json>] [<sdk_commits json>]
  mkdir -p "$1/.dddjango-web/lane"
  printf '{"git_snapshot": "%s", "slices": [{"name": "slice-0", "commits": []}, {"name": "slice-1", "commits": %s}], "sdk_commits": %s}\n' \
    "$2" "${3:-[]}" "${4:-[]}" > "$1/.dddjango-web/lane/build-state.json"
}
P=$(newp k9a); B=$(base_of "$P"); rm "$P/web/sdk_registry.json"; C=$(commit "$P" "slice-1: 목록 정리")
mk_build "$P" "$B" "[\"$C\"]"
OUT=$(BS "$P" --diff-base "$B" --only wv10,wv13); E=$?
check "K9a 슬라이스 커밋이 목록 삭제 — WV13 1 + WV10 1" 2 "$E" "$OUT" "[WV13] BLOCKER=1" "[WV10] BLOCKER=1"
P=$(newp k9b); B=$(base_of "$P"); rm "$P/web/sdk_registry.json"; mk_build "$P" "$B"
OUT=$(BS "$P" --diff-base "$B" --only wv10,wv13); E=$?
check "K9b 미커밋 목록 삭제 — WV13 1 + WV10 1" 2 "$E" "$OUT" "[WV13] BLOCKER=1" "[WV10] BLOCKER=1" "미커밋 변경=1"

# ---------- K10: Kakao.init("abc") added / dataset / 기준점 이전 리터럴
P=$(newp k10); B=$(base_of "$P")
printf '%s\n' '(() => { window.Kakao.init("abc"); })();' > "$P/web/static/js/chart_kakao_lit.js"
OUT=$(BS "$P" --diff-base "$B" --only wv7); E=$?
check "K10a 키 리터럴 added — WV7" 2 "$E" "$OUT" "[WV7] BLOCKER=1"
OUT=$(BS "$P" --diff-base HEAD~0 --only wv7); E=$?
C=$(commit "$P" lit)
OUT=$(BS "$P" --diff-base "$C" --only wv7); E=$?
check "K10c 기준점 이전 리터럴 — 0" 0 "$E" "$OUT" "BLOCKER=0"
P=$(newp k10b); B=$(G "$P" rev-parse HEAD~1)
OUT=$(BS "$P" --diff-base "$B" --only wv7); E=$?
check "K10b dataset 키 — 0" 0 "$E" "$OUT" "BLOCKER=0"

# ---------- K11: WV10 — 슬라이스 커밋이 목록+템플릿 · 기록된 sdk_commits 격리 · 슬라이스의 목록 단독 · 승인 병합 · 기준 가지 병합
P=$(newp k11a); B=$(base_of "$P")
FX edit "$P" kakao_js_sdk '{"service_api": "다른 목적"}' --rebind >/dev/null; echo '<p>x</p>' >> "$P/$CHART"
C=$(commit "$P" "slice-1"); mk_build "$P" "$B" "[\"$C\"]"
OUT=$(BS "$P" --diff-base "$B" --only wv10); E=$?
check "K11a 슬라이스 커밋이 목록+템플릿 — WV10 1" 2 "$E" "$OUT" "[WV10] BLOCKER=1"
P=$(newp k11b); B=$(base_of "$P")
FX edit "$P" kakao_js_sdk '{"service_api": "다른 목적"}' --rebind >/dev/null
C=$(commit "$P" "chore(web-sdk): kakao_js_sdk 목적 정정 — G1"); mk_build "$P" "$B" "[]" "[\"$C\"]"
OUT=$(BS "$P" --diff-base "$B" --only wv10); E=$?
check "K11b 기록된 sdk_commits 격리 — 0" 0 "$E" "$OUT" "BLOCKER=0"
P=$(newp k11f); B=$(base_of "$P")
FX edit "$P" kakao_js_sdk '{"service_api": "다른 목적"}' --rebind >/dev/null; echo '<p>x</p>' >> "$P/$CHART"
C=$(commit "$P" "chore(web-sdk): 목적 정정 + 템플릿"); mk_build "$P" "$B" "[]" "[\"$C\"]"
OUT=$(BS "$P" --diff-base "$B" --only wv10); E=$?
check "K11f sdk_commits 커밋이 목록·벤더 밖 경로도 바꿈 — WV10 1" 2 "$E" "$OUT" "목록·벤더 밖 경로도 바꾼다=1"
P=$(newp k11g); B=$(base_of "$P")
FX edit "$P" kakao_js_sdk '{"service_api": "다른 목적"}' --rebind >/dev/null
C=$(commit "$P" "fix: 목적 정정"); mk_build "$P" "$B" "[]" "[\"$C\"]"
OUT=$(BS "$P" --diff-base "$B" --only wv10); E=$?
check "K11g sdk_commits 커밋 제목이 chore(web-sdk): 아님 — WV10 1" 2 "$E" "$OUT" "제목이=1"
P=$(newp k11c); B=$(base_of "$P")
FX edit "$P" kakao_js_sdk '{"service_api": "다른 목적"}' --rebind >/dev/null
C=$(commit "$P" "slice-1 목록만"); mk_build "$P" "$B" "[\"$C\"]"
OUT=$(BS "$P" --diff-base "$B" --only wv10); E=$?
check "K11c 슬라이스에 기록된 목록 단독 커밋 — WV10 1" 2 "$E" "$OUT" "[WV10] BLOCKER=1"
P=$(newp k11d); G "$P" branch -q -M main; B=$(base_of "$P")
G "$P" checkout -qb side; FX edit "$P" kakao_js_sdk '{"service_api": "main 의 정정"}' --rebind >/dev/null
SIDE=$(commit "$P" "chore(web-sdk): main 쪽 정정"); G "$P" checkout -q main
G "$P" checkout -qb lane; echo 'x = 1' > "$P/web/chart/chart/view_model/chart_view_model.py"; commit "$P" lane1 >/dev/null
G "$P" merge -q --no-edit side; M=$(base_of "$P"); mk_build "$P" "$B"
printf '%s main 받기\n' "$M" > "$P/.dddjango-web/lane/approved-merges.txt"
OUT=$(BS "$P" --diff-base "$B" --only wv10); E=$?
check "K11d 승인 병합의 목록 변경 — 0(notice)" 0 "$E" "$OUT" "BLOCKER=0" "승인 병합=+"
rm "$P/.dddjango-web/lane/approved-merges.txt"
G "$P" branch -q -f main side
OUT=$(BS "$P" --diff-base "$B" --only wv10); E=$?
check "K11e 승인 밖 병합이지만 둘째 부모가 main 이력 — notice 0" 0 "$E" "$OUT" "BLOCKER=0" "기준 가지 병합=1"

# ---------- K12: .gitignore 의 *.min.js
P=$(newp k12); echo '*.min.js' > "$P/.gitignore"; commit "$P" ignore >/dev/null
OUT=$(BS "$P" --diff-base HEAD --only wv2); E=$?
check "K12a 무시 규칙에 걸린 등재 사본 — WV2" 2 "$E" "$OUT" "무시 규칙에 걸린다=1"
FX mkproj "$T/k12b" >/dev/null; echo '*.min.js' > "$T/k12b/.gitignore"; commit "$T/k12b" ignore >/dev/null
OUT=$(FX install "$T/k12b"); E=$?
check "K12b install — 자가 verify 실패 되돌림 exit 2" 2 "$E" "$OUT" "install 되돌림=1"
[ ! -e "$T/k12b/web/sdk_registry.json" ] && [ ! -e "$T/k12b/web/static/vendor" ]; E=$?
check "K12c 되돌림 뒤 목록·벤더 없음" 0 "$E" ""

# ---------- K13: 무관 체제 + static/js/html2canvas.min.js + CDN 태그(회귀)
FX mkproj "$T/k13" >/dev/null; P="$T/k13"; B=$(base_of "$P")
echo 'x' > "$P/web/static/js/html2canvas.min.js"
printf '{%% extends "base.html" %%}\n{%% load static %%}\n{%% block scripts %%}\n<script src="https://cdn.jsdelivr.net/npm/html2canvas.js"></script>\n{%% endblock scripts %%}\n' > "$P/$CHART"
OUT=$(BS "$P" --diff-base "$B" --only wp1,wp2,wv); E=$?
check "K13 무관 체제 — 오늘과 같은 WP1·WP2 · WV 0" 2 "$E" "$OUT" "[WP1] BLOCKER=1" "[WP2] BLOCKER=1" "[WV=0"

# ---------- K14·K18·K38: candidate
FX sdkjs "$T/sdk.js" >/dev/null; FX docs "$T/docs.html" "$T/sdk.js" >/dev/null
FX docs "$T/docs-bad.html" "$T/sdk.js" badsri >/dev/null; FX docs "$T/docs-nocite.html" "$T/sdk.js" nocite >/dev/null
FX docs "$T/docs-nosri.html" "$T/sdk.js" nosri >/dev/null
SRC=https://t1.kakaocdn.net/kakao_js_sdk/2.8.3/kakao.min.js; DOC=https://developers.kakao.com/docs/en/javascript/download
fetch_of() { printf '{"%s": ["%s", "%s", "%s"], "%s": ["%s", "text/html", "%s"]}' "$SRC" "${3:-$SRC}" "${4:-application/javascript}" "$1" "$DOC" "$DOC" "$2"; }
cand() { SDKFX_FETCH="$1" FX vendor candidate "$T/k1" --id kakao_js_sdk --version 2.8.3 --source-url "$3" --docs-url "$DOC" --out "$T/cand-$2" "${@:4}"; }
OUT=$(cand "$(fetch_of "$T/sdk.js" "$T/docs.html")" a "$SRC" --from-file "$T/sdk.js"); E=$?
check "K14a --from-file + 문서 integrity 일치 — 0" 0 "$E" "$OUT" "운영자 문서 공개 값과 일치=1"
OUT=$(cand "$(fetch_of "$T/sdk.js" "$T/docs-bad.html")" b "$SRC" --from-file "$T/sdk.js"); E=$?
check "K14b 문서 integrity 불일치 — 2" 2 "$E" "$OUT" "공개 무결성=+"
OUT=$(cand "$(fetch_of "$T/sdk.js" "$T/docs.html")" c "http://t1.kakaocdn.net/kakao_js_sdk/2.8.3/kakao.min.js"); E=$?
check "K14c http 원본 — 1" 1 "$E" "$OUT" "https 여야=1"
OUT=$(cand "$(fetch_of "$T/sdk.js" "$T/docs.html")" d "$SRC"); E=$?
check "K18a 문서에 원본 경로·integrity — upstream_integrity 채움" 0 "$E" "$(cat "$T/cand-d/candidate.json")" '"integrity_from_docs": true=1' '"upstream_integrity": "sha384-=1'
OUT=$(cand "$(fetch_of "$T/sdk.js" "$T/docs-nocite.html")" e "$SRC"); E=$?
check "K18b 원본 경로 없음 — 2" 2 "$E" "$OUT" "인용하지 않는다=1"
OUT=$(cand "$(fetch_of "$T/sdk.js" "$T/docs.html")" f "$SRC" --docs-file "$T/docs.html"); E=$?
check "K18c --docs-file — fetched_from=file" 0 "$E" "$(cat "$T/cand-f/candidate.json")" '"fetched_from": "file"=1'
OUT=$(cand "$(fetch_of "$T/sdk.js" "$T/docs.html" "https://evil.example.org/kakao.min.js")" g "$SRC"); E=$?
check "K38a 리다이렉트로 운영자 밖 — 2" 2 "$E" "$OUT" "운영자 도메인 밖=1"
OUT=$(cand "{\"$DOC\": [\"$DOC\", \"text/html\", \"$T/docs-nosri.html\"]}" h "$SRC" --from-file "$T/sdk.js"); E=$?
check "K38b --from-file 무증거 — 표지 «출처 검증 없음»" 0 "$E" "$OUT" "출처 검증 없음=1"
echo '<!doctype html><html></html>' > "$T/page.html"; : > "$T/empty.js"
OUT=$(cand "$(fetch_of "$T/page.html" "$T/docs.html" "$SRC" "text/html")" i "$SRC"); E=$?
check "K38c HTML 응답 — 2" 2 "$E" "$OUT" "HTML=+"
OUT=$(cand "$(fetch_of "$T/empty.js" "$T/docs.html")" j "$SRC"); E=$?
check "K38d 빈 응답 — 2" 2 "$E" "$OUT" "비었다=1"
SRCX=https://t1.kakaocdn.net/kakao_js_sdk/2.8.3/kakao
sed "s#$SRC#$SRCX#" "$T/docs.html" > "$T/docs-x.html"
OUT=$(SDKFX_FETCH="{\"$SRCX\": [\"$SRCX\", \"application/javascript\", \"$T/sdk.js\"], \"$DOC\": [\"$DOC\", \"text/html\", \"$T/docs-x.html\"]}" FX vendor candidate "$T/k1" --id kakao_js_sdk --version 2.8.3 --source-url "$SRCX" --docs-url "$DOC" --out "$T/cand-k"); E=$?
check "K38e 확장자 없는 원본 — <id>.js" 0 "$E" "$(cat "$T/cand-k/candidate.json")" '"file": "static/vendor/kakao_js_sdk/kakao_js_sdk.js"=1'

# ---------- K15: install --dry-run 쓰기 0 · 정규 바이트 · 멱등 · 출처 «대리 답»
FX mkproj "$T/k15" >/dev/null
OUT=$(FX install "$T/k15" --dry-run); E=$?
[ ! -e "$T/k15/web/sdk_registry.json" ]; W=$?
check "K15a dry-run — exit 0 · 쓰기 0" 00 "$E$W" "$OUT" "dry-run=1"
OUT=$(FX install "$T/k15" --no-commit); E=$?
python3 - "$T/k15/web/sdk_registry.json" <<'PY' > "$T/k15.canon"
import json, sys
raw = open(sys.argv[1], 'rb').read()
canon = (json.dumps(json.loads(raw), ensure_ascii=False, indent=2, sort_keys=True, separators=(',', ': ')) + '\n').encode()
print('canon' if raw == canon else 'noncanon')
PY
check "K15b 설치 — 정규 바이트" 0 "$E" "$(cat "$T/k15.canon")" "canon=1"
S1=$(shasum "$T/k15/web/sdk_registry.json")
OUT=$(FX install "$T/k15" --no-commit); E=$?
S2=$(shasum "$T/k15/web/sdk_registry.json")
[ "$S1" = "$S2" ]; W=$?
check "K15c 같은 입력 재실행 — 멱등(exit 0 · 바이트 동일)" 00 "$E$W" "$OUT" "이미 같은 항목=1"
FX mkproj "$T/k15d" >/dev/null
OUT=$(FX install "$T/k15d" --source "발주자 대리 답 — 승인"); E=$?
check "K15d 출처 «대리 답» — exit 1" 1 "$E" "$OUT" "출처 꼴 위반=1"

# ---------- K16: 승인 원문 — 판 올림 같은 출처 / 새 판 새 원문 / 파일 이름 바뀜 / 판 없음 / 조상 아님 / web/ 안 / Coordinator 토큰만
FX mkproj "$T/k16" >/dev/null; P="$T/k16"
printf '사용자: 카카오 SDK 2.8.3 들이세요(2026-10-01 14:00)\n사용자: 카카오 SDK 2.8.4 로 올리세요(2026-10-02 10:00)\n사용자: 카카오 SDK 올려도 돼요(2026-10-02 10:05)\n사용자: 새 판 kakao_js_sdk 로 가요(2026-10-02 10:06)\n' > "$P/docs/order.md"
C0=$(commit "$P" "order")
OUT=$(FX install "$P" --source "사용자 원문 docs/order.md@${C0:0:12}:1(2026-10-01 14:00)"); E=$?
check "K16 사용자 원문 채택(판·운영자 낱말) — 0" 0 "$E" "$OUT" "[sdk] 설치=1"
OUT=$(FX install "$P" --version 2.8.4 --replace --source "사용자 원문 docs/order.md@${C0:0:12}:1(2026-10-01 14:00)"); E=$?
check "K16a --replace 에 직전과 같은 출처 — 1" 1 "$E" "$OUT" "직전 승인과 같은 출처=1"
OUT=$(FX install "$P" --version 2.8.4 --replace --source "사용자 원문 docs/order.md@${C0:0:12}:3(2026-10-02 10:05)"); E=$?
check "K16d 원문에 판·표지 없음 — 1" 1 "$E" "$OUT" "판 또는 표지=1"
OUT=$(FX install "$P" --version 2.8.4 --replace --source "사용자 원문 docs/order.md@${C0:0:12}:4(2026-10-02 10:06)" --tokens "2.8.4"); E=$?
check "K16g 필수 낱말을 Coordinator 토큰으로만 채움 — 1" 1 "$E" "$OUT" "판 또는 표지=1"
OUT=$(FX install "$P" --version 2.8.4 --replace --source "사용자 원문 docs/order.md@${C0:0:12}:2(2026-10-02 10:00)"); E=$?
check "K16b 새 판을 담은 새 원문 — 0" 0 "$E" "$OUT" "판 올림=+"
G "$P" checkout -qb gone; echo '사용자: 카카오 SDK 2.8.5 로(2026-10-03 09:00)' > "$P/docs/gone.md"; CG=$(commit "$P" gone); G "$P" checkout -q -
OUT=$(FX install "$P" --version 2.8.5 --replace --source "사용자 원문 docs/gone.md@${CG:0:12}:1(2026-10-03 09:00)"); E=$?
check "K16e HEAD 조상이 아닌 커밋의 원문 — 1" 1 "$E" "$OUT" "조상이 아니다=1"
echo '<!-- 카카오 SDK 2.8.5 승인(2026-10-03 09:00) -->' > "$P/web/chart/chart/section/note.html"; CW=$(commit "$P" note)
OUT=$(FX install "$P" --version 2.8.5 --replace --source "사용자 원문 web/chart/chart/section/note.html@${CW:0:12}:1(2026-10-03 09:00)"); E=$?
check "K16f web/ 안 원문 — 1" 1 "$E" "$OUT" "web/·.dddjango-web/ 안=1"
P2=$(newp k16c); OUT=$(FX install "$P2" --version 2.8.4 --replace --source "본인 직접(2026-10-02 11:00:00 +0900)"); E=$?
check "K16c 파일 이름 그대로 판 올림 — 등재 파일 하나" 0 "$E" "$(ls "$P2/web/static/vendor/kakao_js_sdk")" "kakao.min.js=1"

# ---------- K17: remove — 저장소 템플릿 참조 남음 / 참조 제거 뒤 / 마지막 항목
P=$(newp k17)
OUT=$(SV remove "$P" kakao_js_sdk); E=$?
check "K17a 참조 남은 remove — 2" 2 "$E" "$OUT" "아직 kakao_js_sdk 를 가리킨다=1"
page_ok "$P"; printf '{%% extends "base.html" %%}\n' > "$P/$CHART"
OUT=$(SV remove "$P" kakao_js_sdk); E=$?
[ ! -e "$P/web/sdk_registry.json" ] && [ ! -e "$P/web/static/vendor" ]; W=$?
check "K17b·c 참조 제거 뒤 remove — 0 · 마지막 항목이라 목록·vendor 제거" 00 "$E$W" "$OUT" "마지막 항목=1"

# ---------- K19·K20·K21·K22: git 저장 바이트
P=$(newp k19); cp "$P/web/static/vendor/kakao_js_sdk/kakao.min.js" "$T/outside.js"
rm "$P/web/static/vendor/kakao_js_sdk/kakao.min.js"; ln -s "$T/outside.js" "$P/web/static/vendor/kakao_js_sdk/kakao.min.js"; commit "$P" link >/dev/null
OUT=$(BS "$P" --diff-base HEAD --only wv2); E=$?
check "K19 벤더 파일 심볼릭 링크 — WV2(링크·모드 120000)" 2 "$E" "$OUT" "심볼릭 링크 성분=1" "120000=1"
P=$(newp k20); mv "$P/web/static/vendor/kakao_js_sdk" "$T/k20-real"; ln -s "$T/k20-real" "$P/web/static/vendor/kakao_js_sdk"
OUT=$(BS "$P" --diff-base HEAD --only wv2,wv5); E=$?
check "K20 id 디렉터리 심볼릭 링크(태그 무변) — WV2·WV5 gated 에서도" 2 "$E" "$OUT" "[WV2] BLOCKER=1" "[WV5] BLOCKER=1"
P=$(newp k21); rm "$P/web/static/vendor/.gitattributes"; printf 'web/static/vendor/** text=auto eol=crlf filter=sdkx\n' > "$P/.gitattributes"; commit "$P" attrs >/dev/null
OUT=$(BS "$P" --diff-base HEAD --only wv2); E=$?
check "K21a 상위 .gitattributes text=auto·eol=crlf·filter= · 표지 지움 — WV2 ×3" 2 "$E" "$OUT" "변환 속성 text=1" "변환 속성 eol=1" "변환 속성 filter=1"
FX mkproj "$T/k21b" >/dev/null; printf '*.js eol=crlf\n' > "$T/k21b/.git/info/attributes"
OUT=$(FX install "$T/k21b"); E=$?
check "K21b .git/info/attributes 가 eol 을 건다 — install exit 2" 2 "$E" "$OUT" "install 되돌림=1"
FX mkproj "$T/k21c" >/dev/null; P="$T/k21c"; must "K21c 준비(CRLF 원본 설치)" FX install "$P" --crlf
rm "$P/web/static/vendor/.gitattributes"; G "$P" rm -q --cached web/static/vendor/.gitattributes; G "$P" config core.autocrlf true
OUT=$(BS "$P" --diff-base HEAD --only wv2); E=$?
check "K21c 표지 없이 core.autocrlf 변환 — WV2 ④(저장 바이트 ≠ 작업 트리)" 2 "$E" "$OUT" "git 저장 바이트가 작업 트리 바이트와 다르다=1" "변환 속성=0"
P=$(newp k22); mv "$P/web/static/vendor/kakao_js_sdk/kakao.min.js" "$P/web/static/vendor/kakao_js_sdk/Kakao.min.js"
OUT=$(BS "$P" --diff-base HEAD --only wv2,wv5); E=$?
check "K22 디스크 Kakao.min.js · 등재 kakao.min.js — WV2·WV5" 2 "$E" "$OUT" "[WV2] BLOCKER=1" "[WV5] BLOCKER=1"

# ---------- K23: 중복 키 · 비정규 바이트 · size: true · NaN
reg_raw() { # reg_raw <이름> <파이썬 변환식 — 변수 t(원문 문자열)>
  local P; P=$(newp "k23$1")
  python3 - "$P/web/sdk_registry.json" "$2" <<'PY'
import sys
p, expr = sys.argv[1], sys.argv[2]
t = open(p, encoding='utf-8').read()
open(p, 'w', encoding='utf-8').write(eval(expr))
PY
  BS "$P" --diff-base HEAD --only wv1
}
OUT=$(reg_raw dup 't.replace("\"name\":", "\"name\": \"x\",\n      \"name\":", 1)'); E=$?
check "K23a 중복 키 — WV1" 2 "$E" "$OUT" "중복 키=1"
OUT=$(reg_raw noncanon 't.replace("\n", "\n ", 3)'); E=$?
check "K23b 비정규 바이트 — WV1" 2 "$E" "$OUT" "정규 바이트가 아니다=1"
OUT=$(reg_raw booltrue 't.replace("\"size\": 1", "\"size\": true, \"x_\": 1", 1)'); E=$?
check "K23c size: true — WV1" 2 "$E" "$OUT" "size 가 양의 정수가 아니다=1"
OUT=$(reg_raw nan 't.replace("\"size\": ", "\"size\": NaN, \"y_\": ", 1)'); E=$?
check "K23d NaN — WV1" 2 "$E" "$OUT" "비유한 수=1"

# ---------- K24·K41: 등재 id 안 바꿔치기(P13) — 옛 파일 잔존·참조
P=$(newp k24); B=$(base_of "$P"); echo 'evil()' > "$P/web/static/vendor/kakao_js_sdk/old.min.js"
sed -i.bak "s#web/vendor/kakao_js_sdk/kakao.min.js#web/vendor/kakao_js_sdk/old.min.js#" "$P/$CHART"; rm -f "$P/$CHART.bak"
OUT=$(BS "$P" --diff-base "$B" --only wv5,wv6); E=$?
check "K24·K41 등재 id 안 비등재 파일 + 참조 — WV5 1 + WV6 1" 2 "$E" "$OUT" "[WV5] BLOCKER=1" "[WV6] BLOCKER=1"

# ---------- K25a·K25b·K25c: 미등재 단위(목록 시대 전)
FX mkproj "$T/k25" >/dev/null; P="$T/k25"
mkdir -p "$P/web/static/vendor/kakao_tmp"; FX sdkjs "$P/web/static/vendor/kakao_tmp/kakao.min.js" >/dev/null
printf '{%% extends "base.html" %%}\n{%% load static %%}\n{%% block scripts %%}\n<script src="{%% static '"'"'web/vendor/kakao_tmp/kakao.min.js'"'"' %%}" defer></script>\n{%% endblock scripts %%}\n' > "$P/$CHART"
B=$(commit "$P" "임시 사본(목록 이전)")
echo '/* 무관 편집 */' >> "$P/web/static/css/site.css"
OUT=$(BS "$P" --diff-base "$B"); E=$?
check "K25a 목록 없음 + 기준점 이전 사본·태그 · 무관 레인 — gated 0" 0 "$E" "$OUT" "BLOCKER=0"
OUT=$(BS "$P" --debt-scan); E=$?
check "K25a 빚 — WV12 + WS6 + WP1 + WP2(미룰 수 있음) · G0 알림 1행" 2 "$E" "$OUT" "[WV12] web/static/vendor/kakao_tmp/=1" "[WS6] web/static/vendor/kakao_tmp/=1" "[WP1] web/static/vendor/kakao_tmp/kakao.min.js=1" "[WP2] web/chart=1" "미등재 벤더 단위: static/vendor/kakao_tmp/(WV12)=1" "미룰 수 없음=0"
cp -R "$P" "$T/k25c"
OUT=$(FX install "$T/k25c" --id naver_maps --variant n --draft "$NAVER"); E=$?
check "K25c 그 상태에서 다른 SDK install — 0 · 배너 «미등재 벤더 디렉터리 1»" 0 "$E" "$OUT" "미등재 벤더 디렉터리: 1개=1"
OUT=$(BS "$T/k25c" --diff-base HEAD --only wv); E=$?
check "K25b 같은 사본(목록 시대 전 바이트) + 다른 SDK 등재 — 늘 0" 0 "$E" "$OUT" "BLOCKER=0"
OUT=$(BS "$T/k25c" --debt-scan); E=$?
check "K25b 빚 — WV12 + G0 알림" 2 "$E" "$OUT" "[WV12] web/static/vendor/kakao_tmp/=1" "미등재 벤더 단위:=1"

# ---------- K26: file 디렉터리 ≠ id · 두 항목이 같은 file
P=$(newp k26a); FX edit "$P" kakao_js_sdk '{"file": "static/vendor/other/kakao.min.js"}' --rebind >/dev/null
OUT=$(BS "$P" --diff-base HEAD --only wv1); E=$?
check "K26a file 디렉터리 ≠ id — WV1" 2 "$E" "$OUT" "디렉터리가 id 여야=1"
P=$(newp k26b)
python3 - "$P/web/sdk_registry.json" <<'PY'
import json, sys
p = sys.argv[1]; d = json.load(open(p, encoding='utf-8'))
d['sdks']['kakao_two'] = json.loads(json.dumps(d['sdks']['kakao_js_sdk']))
open(p, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=2, sort_keys=True, separators=(',', ': ')) + '\n')
PY
OUT=$(BS "$P" --diff-base HEAD --only wv1); E=$?
check "K26b 두 항목이 같은 file — WV1" 2 "$E" "$OUT" "두 항목이 같은 file=1"

# ---------- K27: 도메인 대조 8
for pair in 'evil|{"source_url": "https://evilkakaocdn.net/k.min.js", "final_url": "https://evilkakaocdn.net/k.min.js"}|점 경계 하위가 아니다' \
            'userinfo|{"source_url": "https://kakao.com@evil.example/k.min.js"}|userinfo' \
            'port|{"source_url": "https://t1.kakaocdn.net:8443/k.min.js"}|포트' \
            'upper|{"source_url": "https://T1.kakaocdn.net/k.min.js"}|대문자' \
            'dot|{"source_url": "https://t1.kakaocdn.net./k.min.js"}|점으로 끝난다' \
            'single|{"operator_domains": ["com", "kakaocdn.net"]}|라벨 둘 이상' \
            'jsdelivr|{"source_url": "https://cdn.jsdelivr.net/npm/kakao.min.js", "operator_domains": ["kakao.com", "kakaocdn.net", "jsdelivr.net"]}|라이브러리 공용 CDN 호스트' \
            'ajax|{"source_url": "https://t1.kakaocdn.net/ajax/libs/kakao.min.js"}|라이브러리 공용 CDN 경로'; do
  IFS='|' read -r tag patch want <<<"$pair"
  P=$(newp "k27$tag"); FX edit "$P" kakao_js_sdk "$patch" --rebind >/dev/null
  OUT=$(BS "$P" --diff-base HEAD --only wv1,wv4); E=$?
  check "K27 $tag — WV1/WV4" 2 "$E" "$OUT" "$want=+"
done

P=$(newp k27o7); FX edit "$P" kakao_js_sdk '{"origins": {"operator": ["developers.kakao.com", "t1.kakaocdn.net"], "operator_in_code": ["developers.kakao.com", "t1.kakaocdn.net"], "other": []}}' --rebind >/dev/null
OUT=$(BS "$P" --diff-base HEAD --only wv4); E=$?
check "K27 O7 — 주석 밖 코드의 운영자 호스트가 배포·문서 호스트뿐 — WV4" 2 "$E" "$OUT" "O7=1"

# ---------- K28: 승인 뒤 public_config·source_url 만 바뀜
P=$(newp k28); FX edit "$P" kakao_js_sdk '{"public_config": [{"attr": "data-kakao-key", "call": "Kakao.init", "setting": "KAKAO_JAVASCRIPT_KEY"}]}' >/dev/null
OUT=$(BS "$P" --diff-base HEAD --only wv3); E=$?
check "K28 승인 뒤 public_config 변경 — WV3" 2 "$E" "$OUT" "승인 결속 불일치=1"

# ---------- K29: setting SECRET_KEY / KAKAO_ADMIN_KEY
for s in SECRET_KEY KAKAO_ADMIN_KEY; do
  P=$(newp "k29$s"); FX edit "$P" kakao_js_sdk "{\"public_config\": [{\"attr\": \"data-kakao-javascript-key\", \"call\": \"Kakao.init\", \"setting\": \"$s\"}]}" --rebind >/dev/null
  OUT=$(BS "$P" --diff-base HEAD --only wv1); E=$?
  check "K29 setting $s — WV1" 2 "$E" "$OUT" "비밀 낱말=1"
done

# ---------- K30·K45·K45+·K45b: WP3 확장(템플릿 URL 속성 · srcdoc · 조립 스킴 · SVG set)
wp3_case() { # wp3_case <이름> <섹션 본문>
  local P; P=$(newp "wp3$1"); local B; B=$(base_of "$P")
  printf '%s\n' "$2" > "$P/web/chart/chart/section/chart_links.html"
  BS "$P" --diff-base "$B" --only wp3
}
OUT=$(wp3_case k30 '<a href="javascript:alert(1)">a</a>
<a href="&#106;avascript:alert(1)">b</a>
<svg><a xlink:href="javascript:alert(1)">c</a></svg>
<iframe srcdoc="&lt;script&gt;alert(1)&lt;/script&gt;"></iframe>'); E=$?
check "K30 WP3 ×4" 2 "$E" "$OUT" "[WP3] BLOCKER=4"
OUT=$(wp3_case k45 "<a href=\"java{{ '' }}script:x\">a</a>
<a href=\"{% if 1 %}javascript{% endif %}:x\">b</a>
<a href=\"{{ 'javascript' }}:x\">c</a>
<a href=\"{{ scheme }}://evil/x\">d</a>
<svg><set attributeName=\"href\" to=\"javascript:alert(1)\"/></svg>"); E=$?
check "K45 WP3 ×5" 2 "$E" "$OUT" "[WP3] BLOCKER=5"
OUT=$(wp3_case k45pair "<a href=\"{% url 'x' %}\">a</a>
<a href=\"{{ state.url }}\">b</a>
<form action=\"{% url 'auth:login' %}\"></form>
<a href=\"{% url 'x' %}?t=12:30\">c</a>
<a href=\"{{ base }}/a:b\">d</a>
<a href=\"{% url 'x' %}?t=10:00\">e</a>
<a href=\"mailto:{{ email }}\">f</a>
<a href=\"https://{{ host }}/x\">g</a>"); E=$?
check "K45 짝 — 0(태그 안 이름공간 콜론 · ?t=12:30 · {{ base }}/a:b)" 0 "$E" "$OUT" "BLOCKER=0"
OUT=$(wp3_case k45plus "<a href=\"{{ 'javascript' }}&#58;K.init('k')\">a</a>
<a href=\"java{{ '' }}script&colon;x\">b</a>"); E=$?
check "K45+ 엔티티 콜론 — WP3 ×2" 2 "$E" "$OUT" "[WP3] BLOCKER=2"
OUT=$(wp3_case k45b "<a href=\"{% url 'a' %}:{{ x }}\">a</a>
<a href=\"{{ host }}:{{ port }}/x\">b</a>
<a href=\"java{# c #}script:x\">c</a>"); E=$?
check "K45b 감수하는 발견 ×2 + 주석 마스킹 뒤 ① 1" 2 "$E" "$OUT" "[WP3] BLOCKER=3" "스킴 자리를 템플릿 태그로=2" "스크립트 스킴으로 시작=1"

# ---------- K31·K33: WV7 템플릿·JS 키 리터럴
P=$(newp k31); B=$(base_of "$P"); sed -i.bak 's#data-kakao-javascript-key="{{ state.kakao_javascript_key }}"#data-kakao-javascript-key="0123abcd"#' "$P/$CHART"; rm -f "$P/$CHART.bak"
OUT=$(BS "$P" --diff-base "$B" --only wv7); E=$?
check "K31a data 속성 리터럴 — WV7" 2 "$E" "$OUT" "[WV7] BLOCKER=1"
P=$(newp k31b); B=$(G "$P" rev-parse HEAD~1)
OUT=$(BS "$P" --diff-base "$B" --only wv7); E=$?
check "K31b {{ state.kakao_javascript_key }} — 0" 0 "$E" "$OUT" "BLOCKER=0"
P=$(newp k33); B=$(base_of "$P")
cat > "$P/web/static/js/chart_kakao_key.js" <<'EOF'
(() => {
  window.Kakao?.init('k1');
  Kakao.init( "k2");
  Kakao["init"]("k3");
  // Kakao.init("YOUR_KEY")
})();
EOF
OUT=$(BS "$P" --diff-base "$B" --only wv7); E=$?
check "K33 ?.·공백·대괄호 ×3 / 주석 0" 2 "$E" "$OUT" "[WV7] BLOCKER=3"

# ---------- K32·K46: WV8(무관 체제에서도)
FX mkproj "$T/k32" >/dev/null; P="$T/k32"; B=$(base_of "$P")
cat > "$P/web/static/js/chart_load.js" <<'EOF'
(() => {
  const s = document.createElement('script');
  s.src = '/x.js';
  import('https://cdn.example.org/mod.js');
  const h = 'https://kapi.kakao.com/v2/user/me';
  setTimeout("go()", 10);
})();
EOF
OUT=$(BS "$P" --diff-base "$B" --only wv8); E=$?
check "K32 무관 체제 WV8 ×4(script · import() · 운영자 호스트 리터럴 · 문자열 타이머)" 2 "$E" "$OUT" "[WV8] BLOCKER=5"
OUT=$(FX wv8); E=$?
check "K46·K46+·K46b·K46c + 구현 메모 ⑤ 8꼴 — WV8 표본 어긋남 0" 0 "$E" "$OUT" "어긋남 0=1"

# ---------- K34: 벤더 태그가 section 조각 · {% static 'vendor/…' %} · 하드코딩 /static/web/vendor/… · 페이지 block 밖
P=$(newp k34); B=$(base_of "$P")
printf '%s\n' "<script src=\"{% static 'web/vendor/kakao_js_sdk/kakao.min.js' %}\" defer></script>" > "$P/web/chart/chart/section/chart_frag.html"
OUT=$(BS "$P" --diff-base "$B" --only wp2,wv6); E=$?
check "K34a section 조각 — WP2" 2 "$E" "$OUT" "[WP2] BLOCKER=1" "fragment=+"
P=$(newp k34b); B=$(base_of "$P"); sed -i.bak "s#'web/vendor/kakao_js_sdk/kakao.min.js'#'vendor/kakao_js_sdk/kakao.min.js'#" "$P/$CHART"; rm -f "$P/$CHART.bak"
OUT=$(BS "$P" --diff-base "$B" --only wp2,wv6); E=$?
check "K34b {% static 'vendor/…' %} — WP2·WV6" 2 "$E" "$OUT" "[WV6] BLOCKER=1" "[WP2] BLOCKER=1"
P=$(newp k34c); B=$(base_of "$P"); sed -i.bak "s#{% static 'web/vendor/kakao_js_sdk/kakao.min.js' %}#/static/web/vendor/kakao_js_sdk/kakao.min.js#" "$P/$CHART"; rm -f "$P/$CHART.bak"
OUT=$(BS "$P" --diff-base "$B" --only wp2,wv6); E=$?
check "K34c 하드코딩 /static/web/vendor/… — WP2·WV6" 2 "$E" "$OUT" "[WV6] BLOCKER=1" "[WP2] BLOCKER=1"
P=$(newp k34d); B=$(base_of "$P")
printf '{%% extends "base.html" %%}\n{%% load static %%}\n%s\n{%% block scripts %%}\n%s\n{%% endblock scripts %%}\n' "$SDKTAG" "$FTAG" > "$P/$CHART"
OUT=$(BS "$P" --diff-base "$B" --only wp2); E=$?
check "K34d 페이지 block 밖 — WP2" 2 "$E" "$OUT" "block scripts %}\` 밖=1"

# ---------- K35: 기능 JS 태그만 added 인데 기준점 이전 벤더 태그보다 앞 · base 만 added 인 base+page 중복
P=$(newp k35a)
printf '{%% extends "base.html" %%}\n{%% load static %%}\n{%% block scripts %%}\n%s\n{%% endblock scripts %%}\n' "$SDKTAG" > "$P/$CHART"; B=$(commit "$P" pre)
printf '{%% extends "base.html" %%}\n{%% load static %%}\n{%% block scripts %%}\n%s\n%s\n{%% endblock scripts %%}\n' "$FTAG" "$SDKTAG" > "$P/$CHART"
OUT=$(BS "$P" --diff-base "$B" --only wp2); E=$?
check "K35a 기능 JS 태그만 added · 기준점 이전 벤더 태그보다 앞 — WP2" 2 "$E" "$OUT" "기능 JS 태그보다 뒤=1"
P=$(newp k35b); B=$(base_of "$P"); printf '%s\n' "$BASE_DUP" > "$P/web/base/base.html"
OUT=$(BS "$P" --diff-base "$B" --only wp2); E=$?
check "K35b base 만 added 인 base+page 중복 — 페이지 파일에 WP2" 2 "$E" "$OUT" "base·페이지 중복 로드=1" "web/chart/chart/view/chart.html=1"

# ---------- K36: rebase/ff 혼합 커밋 · evil merge · 다른 빌드의 chore(web-sdk)
P=$(newp k36a); B=$(base_of "$P"); FX edit "$P" kakao_js_sdk '{"service_api": "ff 유입"}' --rebind >/dev/null; commit "$P" "main 커밋(ff 유입)" >/dev/null; mk_build "$P" "$B"
OUT=$(BS "$P" --diff-base "$B" --only wv10); E=$?
check "K36a rebase/ff 로 받은 기록 밖 커밋 — notice" 0 "$E" "$OUT" "BLOCKER=0" "기록 밖 커밋=1"
P=$(newp k36b); G "$P" branch -q -M main; B=$(base_of "$P"); G "$P" checkout -qb side; echo 'y' > "$P/web/static/css/side.css"; commit "$P" side >/dev/null
G "$P" checkout -q main; G "$P" checkout -qb lane; echo 'z' > "$P/web/static/css/lane.css"; commit "$P" lane >/dev/null
G "$P" merge -q --no-ff --no-commit side >/dev/null 2>&1; FX edit "$P" kakao_js_sdk '{"service_api": "병합 안 변경"}' --rebind >/dev/null; G "$P" add -A; G "$P" commit -qm "merge side"
mk_build "$P" "$B"
OUT=$(BS "$P" --diff-base "$B" --only wv10); E=$?
check "K36b evil merge 의 목록 변경 — WV10 1" 2 "$E" "$OUT" "[WV10] BLOCKER=1" "자신의 목록·벤더 몫=1"
P=$(newp k36c); B=$(base_of "$P"); FX edit "$P" kakao_js_sdk '{"service_api": "다른 빌드"}' --rebind >/dev/null
commit "$P" "chore(web-sdk): 다른 빌드의 정정" >/dev/null; mk_build "$P" "$B"
OUT=$(BS "$P" --diff-base "$B" --only wv10); E=$?
check "K36c 다른 빌드의 chore(web-sdk) 커밋 — notice" 0 "$E" "$OUT" "BLOCKER=0" "기록 밖 커밋=1"

# ---------- K37: sdk_vendor.py verify + 과거 시안 빌드 존재
P=$(newp k37); mkdir -p "$P/.dddjango-web/old/design-ref"; echo '{"has_design_screen": true}' > "$P/.dddjango-web/old/build-state.json"; echo '{}' > "$P/.dddjango-web/old/design-input.json"
OUT=$(SV verify "$P"); E=$?
check "K37 verify 는 시안 증거를 부르지 않는다 — 0" 0 "$E" "$OUT" "발견 0건=1"

# ---------- K39·K52·K52b·K53·K53b: WV9 범위 · 분류 바닥
wv9_case() { # wv9_case <이름> <기능 JS 본문>
  local P; P=$(newp "wv9$1"); local B; B=$(base_of "$P")
  printf '%s\n' "$2" > "$P/web/static/js/chart_wv9.js"
  BS "$P" --diff-base "$B" --only wv9
}
OUT=$(wv9_case k39a 'window.Kakao.Auth.login({});'); E=$?
check "K39a 묶음 밖 이름공간 Auth — WV9 1" 2 "$E" "$OUT" "[WV9] BLOCKER=1" "승인 범위 밖=1"
OUT=$(wv9_case k39b 'window.Kakao.Share.sendScrap({});'); E=$?
check "K39b 같은 이름공간 sendScrap — 0" 0 "$E" "$OUT" "BLOCKER=0"
OUT=$(wv9_case k52a 'window.Kakao.Share.uploadImage({file: f});'); E=$?
check "K52a 이름 지정 원소 없는 uploadImage — WV9 1" 2 "$E" "$OUT" "[WV9] BLOCKER=1"
OUT=$(wv9_case k52c 'Kakao.Share.createDefaultButton({});'); E=$?
check "K52c createDefaultButton — WV9 1" 2 "$E" "$OUT" "[WV9] BLOCKER=1" "UI 함수=1"
OUT=$(wv9_case k52d 'Kakao.Share.cleanup();'); E=$?
check "K52d 수명 함수 cleanup — 0" 0 "$E" "$OUT" "BLOCKER=0"
OUT=$(wv9_case k52e 'Kakao.Share.fooBar();'); E=$?
check "K52e 표에 없는 함수 — WV9 1" 2 "$E" "$OUT" "표에 없는 함수=1"
# 범위 넓힘 — 이름 지정 data_out · 새 이름공간 · gateway 경로
P=$(newp k52b); OUT=$(FX install "$P" --scope-add Kakao.Share.uploadImage); E=$?
check "K52b-scope uploadImage 범위 넓힘(본인 직접) — 0" 0 "$E" "$OUT" "범위 넓힘=+"
B=$(base_of "$P"); printf '%s\n' 'window.Kakao.Share.uploadImage({file: f});' > "$P/web/static/js/chart_wv9.js"
OUT=$(BS "$P" --diff-base "$B" --only wv9,wv1,wv3); E=$?
check "K52b 이름 지정 원소가 있으면 — 0" 0 "$E" "$OUT" "BLOCKER=0"
GW='{"namespace_members": {"API": {"cleanup": "lifecycle", "request": "gateway"}}, "gateway_paths": {"API.request": {"/v1/api/talk/friends": "read", "/v1/api/talk/friends/message/default/send": "data_out", "/v1/user/unlink": "data_out", "/v2/api/talk/message/image/upload": "data_out", "/v2/user/me": "read"}}}'
P=$(newp k52gw); OUT=$(FX install "$P" --scope-add "Kakao.API.request:/v2/user/me" --draft "$GW"); E=$?
check "K52b-gw gateway 경로 범위 넓힘(본인 직접) — 0" 0 "$E" "$OUT" "범위 넓힘=+"
B=$(base_of "$P")
gw_case() { printf '%s\n' "$2" > "$P/web/static/js/chart_gw.js"; BS "$P" --diff-base "$B" --only wv9; }
OUT=$(gw_case a "window.Kakao.API.request({url: '/v2/user/me'});"); E=$?
check "K52b-1 승인 경로 — 0" 0 "$E" "$OUT" "BLOCKER=0"
OUT=$(gw_case b "window.Kakao.API.request({url: '/v1/api/talk/friends/message/default/send'});"); E=$?
check "K52b-2 승인 밖 경로 — WV9 1" 2 "$E" "$OUT" "승인 경로 밖=1"
OUT=$(gw_case c "window.Kakao.API.request({url: path});"); E=$?
check "K52b-3 비리터럴 url — WV9 1" 2 "$E" "$OUT" "문자열 리터럴이 아니다=1"
OUT=$(gw_case d "window.Kakao.API.request({url: 'https://kapi.kakao.com/v2/user/me/?x=1'});"); E=$?
check "K52b-4 절대 주소·쿼리·끝 / 짝(같은 정규형) — 0" 0 "$E" "$OUT" "BLOCKER=0"
OUT=$(gw_case e "window.Kakao.API.request({url: '/v2/user/%6De'});"); E=$?
check "K52b-5 퍼센트 인코딩 짝 — 0" 0 "$E" "$OUT" "BLOCKER=0"
OUT=$(gw_case f "window.Kakao.API.request({url: 'https://evil.example.org/v2/user/me'});"); E=$?
check "K52b-6 운영자 밖 절대 주소 — WV9 1" 2 "$E" "$OUT" "운영자 호스트가 아닌 절대 주소=1"
OUT=$(gw_case g "window.Kakao.API.request({url: '/v9/unknown'});"); E=$?
check "K52b-7 api-paths 밖 경로 — WV9 1" 2 "$E" "$OUT" "api-paths 밖=1"
P=$(newp k52bundle); FX edit "$P" kakao_js_sdk "{\"namespace_members\": {\"API\": {\"cleanup\": \"lifecycle\", \"request\": \"gateway\"}, \"Share\": {\"cleanup\": \"lifecycle\", \"createCustomButton\": \"sdk_ui\", \"createDefaultButton\": \"sdk_ui\", \"createScrapButton\": \"sdk_ui\", \"deleteImage\": \"data_out\", \"scrapImage\": \"data_out\", \"sendCustom\": \"call\", \"sendDefault\": \"call\", \"sendScrap\": \"call\", \"uploadImage\": \"data_out\"}}, \"use_scope\": [\"Kakao.API.*\", \"Kakao.API.request\", \"Kakao.Share.*\", \"Kakao.init\", \"Kakao.isInitialized\"]}" --rebind >/dev/null
OUT=$(BS "$P" --diff-base HEAD --only wv1); E=$?
check "K52b-8 gateway 를 묶음·이름 원소로 — WV1 ×2" 2 "$E" "$OUT" "gateway 이름공간 묶음=1" "gateway 함수는=1"
# K53b·K53: 분류 바닥
for pair in 'req|{"API": {"request": "call", "cleanup": "lifecycle"}}|이름 바닥 gateway' \
            'put|{"Share": {"putObject": "call"}}|이름 바닥 data_out' \
            'upload|{"Share": {"uploadImage": "call"}}|이름 바닥 data_out'; do
  IFS='|' read -r tag patch want <<<"$pair"
  P=$(newp "k53$tag"); FX edit "$P" kakao_js_sdk "{\"namespace_members\": $patch}" --rebind >/dev/null
  OUT=$(BS "$P" --diff-base HEAD --only wv1); E=$?
  check "K53 바닥 $tag — WV1" 2 "$E" "$OUT" "$want=+"
done
P=$(newp k53pair); FX edit "$P" kakao_js_sdk '{"namespace_members": {"Share": {"restoreSession": "call", "outputText": "call", "inputValue": "call", "sendDefault": "call", "cleanup": "lifecycle", "uploadImage": "data_out"}}}' --rebind >/dev/null
OUT=$(BS "$P" --diff-base HEAD --only wv1); E=$?
check "K53b 토큰 짝 restoreSession·outputText·inputValue = call — 바닥 위반 0" 0 "$E" "$OUT" "이름 바닥=0"
P=$(newp k53path); FX edit "$P" kakao_js_sdk '{"namespace_members": {"API": {"cleanup": "lifecycle", "request": "gateway"}, "Share": {"sendDefault": "call", "cleanup": "lifecycle", "uploadImage": "data_out"}}, "gateway_paths": {"API.request": {"/v1/user/unlink": "read"}}}' --rebind >/dev/null
OUT=$(BS "$P" --diff-base HEAD --only wv1); E=$?
check "K53b 경로 바닥 /v1/user/unlink = read — WV1" 2 "$E" "$OUT" "경로 바닥 data_out=1"
P=$(newp k53b2); FX edit "$P" kakao_js_sdk '{"use_scope": ["Kakao.Share.*", "Kakao.Share.createDefaultButton", "Kakao.Share.sendDefault", "Kakao.init"]}' --rebind >/dev/null
OUT=$(BS "$P" --diff-base HEAD --only wv1); E=$?
check "K53 sdk_ui 이름 원소 · call 이름 원소 — WV1 ×2" 2 "$E" "$OUT" "어떤 승인으로도=1" "data_out 함수만=1"
P=$(newp k53b3); FX edit "$P" kakao_js_sdk '{"namespace_words": {"API": ["사용자 정보"], "Auth": ["로그인"], "Share": ["공유"], "Share.uploadImage": ["카카오"]}}' --rebind >/dev/null
OUT=$(BS "$P" --diff-base HEAD --only wv1); E=$?
check "K53 낱말 «카카오»(운영자 토큰) — WV1" 2 "$E" "$OUT" "운영자·제품 낱말과 같거나=1"
# K39 범위 넓힘 출처 — «카카오 로그인»(판 없음) / 없음 / «로그인»만
P=$(newp k39s); printf '사용자: 카카오 로그인 붙여 주세요(2026-10-02 09:00)\n사용자: 붙여 주세요(2026-10-02 09:01)\n사용자: 로그인 붙여 주세요(2026-10-02 09:02)\n' > "$P/docs/req.md"; CR=$(commit "$P" req)
AUTH='{"namespace_members": {"Auth": {"login": "call"}}}'
OUT=$(FX install "$P" --scope-add "Kakao.Auth.*" --draft "$AUTH" --source "사용자 원문 docs/req.md@${CR:0:12}:2(2026-10-02 09:01)"); E=$?
check "K39d 원문에 낱말 없음 — 1" 1 "$E" "$OUT" "승인 출처 거절=1"
OUT=$(FX install "$P" --scope-add "Kakao.Auth.*" --draft "$AUTH" --source "사용자 원문 docs/req.md@${CR:0:12}:3(2026-10-02 09:02)"); E=$?
check "K39e «로그인»만 · 운영자 낱말 없음 — 1" 1 "$E" "$OUT" "운영자·제품 낱말=1"
OUT=$(FX install "$P" --scope-add "Kakao.Auth.*" --draft "$AUTH" --source "사용자 원문 docs/req.md@${CR:0:12}:1(2026-10-02 09:00)"); E=$?
check "K39c «카카오 로그인»(판 없음) — 0" 0 "$E" "$OUT" "범위 넓힘=+"

# ---------- 구현 메모 ③: 판 올림 dry-run — gateway 경로표 다시 뽑기(사라진 경로 1 · 새 경로 1)
P=$(newp gwup); must "③ 준비 scope-add" FX install "$P" --scope-add "Kakao.API.request:/v2/user/me" --draft "$GW"
GW2='{"namespace_members": {"API": {"cleanup": "lifecycle", "request": "gateway"}, "Share": {"cleanup": "lifecycle", "createCustomButton": "sdk_ui", "createDefaultButton": "sdk_ui", "createScrapButton": "sdk_ui", "deleteImage": "data_out", "scrapImage": "data_out", "sendCustom": "call", "sendDefault": "call", "sendScrap": "call", "uploadImage": "data_out"}}, "gateway_paths": {"API.request": {"/v1/api/talk/friends": "read", "/v1/api/talk/friends/message/default/send": "data_out", "/v1/user/unlink": "data_out", "/v2/api/talk/message/image/upload": "data_out", "/v2/user/new_info": "read"}}}'
OUT=$(FX install "$P" --version 2.8.4 --replace --dry-run --drop-api /v2/user/me --extra-api /v2/user/new_info --draft "$GW2" --source "본인 직접(2026-10-02 11:00:00 +0900)"); E=$?
check "③ 판 올림 dry-run(새 판으로 다시 분류) — 사라진 경로 1 · 새 경로 1" 0 "$E" "$OUT" "사라진 경로 /v2/user/me=1" "새 경로(승인 밖) /v2/user/new_info=1"
OUT=$(FX install "$P" --version 2.8.4 --replace --dry-run --drop-api /v2/user/me --extra-api /v2/user/new_info --draft "$GW" --source "본인 직접(2026-10-02 11:00:00 +0900)"); E=$?
check "③ 옛 경로표 초안 — 거절 2(diff 를 먼저 보인다)" 2 "$E" "$OUT" "사라진 경로 /v2/user/me=1" "api-paths 밖=1"

# ---------- K40·K50·K50b·K50c·K50d·K50e·K48·K48b·K48c·K49·K42·K51: 목록 시대
era_proj() { # era_proj <이름> — 목록 없는 기준(main)
  FX mkproj "$T/$1" >/dev/null; G "$T/$1" branch -q -M main; echo "$T/$1"
}
copy_lane() { # copy_lane <프로젝트> [flat] — laneY 가지에 목록 이전 임시 사본(+ 로드 줄)
  local P="$1"; G "$P" checkout -qb laneY
  if [ "${2:-}" = flat ]; then mkdir -p "$P/web/static/vendor"; FX sdkjs "$P/web/static/vendor/kakao.min.js" >/dev/null
  else mkdir -p "$P/web/static/vendor/kakao_tmp"; FX sdkjs "$P/web/static/vendor/kakao_tmp/kakao.min.js" >/dev/null; fi
  commit "$P" "임시 사본" >/dev/null; G "$P" checkout -q main
}
P=$(era_proj k40); copy_lane "$P"; must "준비 install" FX install "$P" --id naver_maps --variant n --draft "$NAVER"
G "$P" merge -q --no-edit laneY
OUT=$(BS "$P" --diff-base HEAD --only wv); E=$?
check "K40 깨끗한 install + 목록 이전 사본 레인 merge — 늘 0" 0 "$E" "$OUT" "BLOCKER=0"
OUT=$(BS "$P" --debt-scan); E=$?
check "K40 빚 WV12 + G0 알림" 2 "$E" "$OUT" "[WV12] web/static/vendor/kakao_tmp/=1" "미등재 벤더 단위:=1"
P=$(era_proj k50); copy_lane "$P" flat; must "준비 install" FX install "$P" --id naver_maps --variant n --draft "$NAVER"
G "$P" merge -q --no-edit laneY
OUT=$(BS "$P" --diff-base HEAD --only wv); E=$?
check "K50 평면 사본 merge — 늘 0" 0 "$E" "$OUT" "BLOCKER=0"
OUT=$(BS "$P" --debt-scan); E=$?
check "K50 빚 WV12(평면)" 2 "$E" "$OUT" "[WV12] web/static/vendor/kakao.min.js=1"
for how in squash rebase pick; do
  P=$(era_proj "k50c$how"); copy_lane "$P"; must "준비 install" FX install "$P" --id naver_maps --variant n --draft "$NAVER"
  case $how in
    squash) G "$P" merge -q --squash laneY >/dev/null; commit "$P" squash >/dev/null ;;
    rebase) G "$P" checkout -q laneY; G "$P" rebase -q main >/dev/null 2>&1 ;;
    pick) G "$P" cherry-pick "$(G "$P" rev-parse laneY)" >/dev/null ;;
  esac
  OUT=$(BS "$P" --diff-base HEAD --only wv13); E=$?
  check "K50c $how 착륙 — WV13 1(고지대로)" 2 "$E" "$OUT" "[WV13] BLOCKER=1"
done
P=$(era_proj k50b); G "$P" checkout -qb laneY; mkdir -p "$P/web/static/vendor/kakao_js_sdk"
FX sdkjs "$P/web/static/vendor/kakao_js_sdk/kakao.min.js" pre >/dev/null; commit "$P" "같은 이름 임시 사본(목록 이전 · 다른 바이트)" >/dev/null
G "$P" checkout -q main; must "K50b 준비 install" FX install "$P"; SV remove "$P" kakao_js_sdk >/dev/null; commit "$P" remove >/dev/null
G "$P" merge -q --no-edit laneY
OUT=$(BS "$P" --diff-base HEAD --only wv13); E=$?
check "K50b 같은 이름의 등재 전 사본이 제거 뒤 병합으로 — 늘 0" 0 "$E" "$OUT" "BLOCKER=0"
OUT=$(BS "$P" --debt-scan); E=$?
check "K50b 빚 WV12" 2 "$E" "$OUT" "[WV12] web/static/vendor/kakao_js_sdk/=1"
for flat in dir flat; do
  P=$(era_proj "k50d$flat"); G "$P" checkout -qb laneY
  if [ $flat = flat ]; then mkdir -p "$P/web/static/vendor"; FX sdkjs "$P/web/static/vendor/kakao.min.js" >/dev/null
  else mkdir -p "$P/web/static/vendor/kakao_js_sdk"; FX sdkjs "$P/web/static/vendor/kakao_js_sdk/kakao.min.js" >/dev/null; fi
  commit "$P" "임시 사본" >/dev/null; G "$P" checkout -q main
  FX install "$P" >/dev/null; G "$P" merge -q --no-edit laneY >/dev/null 2>&1
  OUT=$(BS "$P" --diff-base HEAD --only wv13); E=$?
  check "K50d 임시 사본 = 나중 등재 바이트($flat) · merge — 늘 0" 0 "$E" "$OUT" "BLOCKER=0"
done
P=$(era_proj k50f); mkdir -p "$P/web/static/vendor/lib"; echo 'A' > "$P/web/static/vendor/lib/l.js"; commit "$P" "base lib" >/dev/null
G "$P" checkout -qb s; echo 'B' > "$P/web/static/vendor/lib/l.js"; commit "$P" s >/dev/null
G "$P" checkout -q main; echo 'C' > "$P/web/static/vendor/lib/l.js"; commit "$P" c >/dev/null
G "$P" merge -q s >/dev/null 2>&1; echo 'RESOLVED' > "$P/web/static/vendor/lib/l.js"; G "$P" add -A; G "$P" commit -qm "merge(해소)"
must "K50f 준비 install" FX install "$P" --id naver_maps --variant n --draft "$NAVER"
OUT=$(BS "$P" --diff-base HEAD --only wv13); E=$?
check "K50f 목록 이전 충돌 해소 사본(-m) — 늘 0" 0 "$E" "$OUT" "BLOCKER=0"
P=$(era_proj k50e); copy_lane "$P"
G "$P" checkout -q laneY; printf '{%% extends "base.html" %%}\n{%% load static %%}\n{%% block scripts %%}\n<script src="{%% static '"'"'web/vendor/kakao_tmp/kakao.min.js'"'"' %%}" defer></script>\n{%% endblock scripts %%}\n' > "$P/$CHART"; commit "$P" "로드 줄" >/dev/null; G "$P" checkout -q main
must "준비 install" FX install "$P"; must "준비 install" FX install "$P" --version 2.8.4 --replace --source "본인 직접(2026-10-02 11:00:00 +0900)"
G "$P" merge -q --no-edit laneY >/dev/null 2>&1
OUT=$(BS "$P" --diff-base HEAD --only wv13); E=$?
check "K50e 판 올림 뒤 옛 판 임시 사본(참조 중) merge — WV13 1" 2 "$E" "$OUT" "[WV13] BLOCKER=1"
sed -i.bak "s#web/vendor/kakao_tmp/kakao.min.js#web/vendor/kakao_js_sdk/kakao.min.js#" "$P/$CHART"; rm -f "$P/$CHART.bak"; rm -r "$P/web/static/vendor/kakao_tmp"; commit "$P" "§6-8 #6b 치환 정리" >/dev/null
OUT=$(BS "$P" --diff-base HEAD --only wv13); E=$?
check "K50e 치환 정리(슬라이스 0 · 임시 사본 삭제) 뒤 — 0" 0 "$E" "$OUT" "BLOCKER=0"
P=$(newp k48); mv "$P/web/static/vendor/kakao_js_sdk" "$P/web/static/vendor/kakao_two"; echo 'evil()' >> "$P/web/static/vendor/kakao_two/kakao.min.js"; rm "$P/web/sdk_registry.json"
sed -i.bak "s#kakao_js_sdk#kakao_two#" "$P/$CHART"; rm -f "$P/$CHART.bak"; commit "$P" fix >/dev/null
OUT=$(BS "$P" --diff-base HEAD --only wv13); E=$?
check "K48 항목 삭제 + 개명 + 변조 + 로드 줄 치환(빌드 기록 없음) — WV13 1" 2 "$E" "$OUT" "[WV13] BLOCKER=1"
P=$(era_proj k48b); mkdir -p "$P/web/static/vendor/kakao_js_sdk"; FX sdkjs "$P/web/static/vendor/kakao_js_sdk/kakao.min.js" >/dev/null; commit "$P" "임시 사본" >/dev/null
must "준비 install" FX install "$P" --register-existing "$P/web/static/vendor/kakao_js_sdk/kakao.min.js"
mv "$P/web/static/vendor/kakao_js_sdk" "$P/web/static/vendor/kakao2"; rm "$P/web/sdk_registry.json" "$P/web/static/vendor/.gitattributes"; commit "$P" fix >/dev/null
OUT=$(BS "$P" --diff-base HEAD --only wv13); E=$?
check "K48b 기존 등록 SDK 항목 삭제 + 개명(바이트 그대로) — WV13 1" 2 "$E" "$OUT" "[WV13] BLOCKER=1"
P=$(era_proj k48c); mkdir -p "$P/web/static/vendor/kakao_tmp"; FX sdkjs "$P/web/static/vendor/kakao_tmp/kakao.min.js" >/dev/null; commit "$P" "임시 사본(목록 이전)" >/dev/null
rm -r "$P/web/static/vendor/kakao_tmp"; must "준비 install" FX install "$P"
mv "$P/web/static/vendor/kakao_js_sdk" "$P/web/static/vendor/kakao_tmp"; rm "$P/web/sdk_registry.json" "$P/web/static/vendor/.gitattributes"; commit "$P" "옛 자리로" >/dev/null
OUT=$(BS "$P" --diff-base HEAD --only wv13); E=$?
check "K48c 옛 임시 자리로 되돌려 개명 + 항목 삭제 — WV13 1" 2 "$E" "$OUT" "[WV13] BLOCKER=1"
P=$(newp k48d); printf '{%% extends "base.html" %%}\n' > "$P/$CHART"; SV remove "$P" kakao_js_sdk >/dev/null; commit "$P" remove >/dev/null
mkdir -p "$P/web/static/vendor/newcopy"; echo 'x()' > "$P/web/static/vendor/newcopy/n.min.js"; commit "$P" "새 사본" >/dev/null
OUT=$(BS "$P" --diff-base HEAD --only wv13); E=$?
check "K48c 마지막 remove 뒤 새 미등재 사본 — WV13 1(목록 시대는 끝나지 않는다)" 2 "$E" "$OUT" "[WV13] BLOCKER=1"
P=$(era_proj k49); must "준비 install" FX install "$P"; G "$P" checkout -qb side; must "준비 install" FX install "$P" --id naver_maps --variant n --draft "$NAVER"
G "$P" checkout -q main; echo 'm' > "$P/web/static/css/m.css"; commit "$P" m >/dev/null
G "$P" merge -q --no-ff --no-commit side >/dev/null 2>&1; G "$P" checkout HEAD -- web/sdk_registry.json; echo 'alert("merge-only")' > "$P/web/static/vendor/naver_maps/naver_maps.min.js"; G "$P" add -A; G "$P" commit -qm M
OUT=$(BS "$P" --diff-base HEAD --only wv13); E=$?
check "K49 병합 해소가 항목만 떨어뜨리고 변조(--full-history) — WV13 1" 2 "$E" "$OUT" "[WV13] BLOCKER=1"
P=$(era_proj k49b); G "$P" checkout -qb side; must "K49b 준비 install(곁가지)" FX install "$P"
G "$P" checkout -q main; echo 'm' > "$P/web/static/css/m.css"; commit "$P" m >/dev/null
G "$P" merge -q --no-ff --no-commit side >/dev/null 2>&1; G "$P" rm -q --cached web/sdk_registry.json; rm -f "$P/web/sdk_registry.json"
echo 'alert("merge-only")' >> "$P/web/static/vendor/kakao_js_sdk/kakao.min.js"; G "$P" add -A; G "$P" commit -qm "M(목록 탈락 + 변조)"
OUT=$(BS "$P" --diff-base HEAD --only wv13); E=$?
check "K49b 곁가지 목록을 병합 해소가 떨어뜨림 + 변조(--full-history 로 시대 시작) — WV13 1" 2 "$E" "$OUT" "[WV13] BLOCKER=1"
P=$(newp k42a); rm "$P/web/sdk_registry.json"; echo 'x' >> "$P/web/static/vendor/kakao_js_sdk/kakao.min.js"
OUT=$(BS "$P" --diff-base HEAD --only wv13); E=$?
check "K42a 빌드 기록 없음 · 목록 삭제 + 사본 변조 — WV13" 2 "$E" "$OUT" "[WV13] BLOCKER=1"
drop_entry() { python3 - "$1/web/sdk_registry.json" "$2" <<'PY'
import json, sys
p, sid = sys.argv[1], sys.argv[2]
d = json.load(open(p, encoding='utf-8')); d['sdks'].pop(sid)
open(p, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=2, sort_keys=True, separators=(',', ': ')) + '\n')
PY
}
P=$(newp k42b); must "K42b 준비" FX install "$P" --id naver_maps --variant n --draft "$NAVER"
drop_entry "$P" kakao_js_sdk; echo 'x' >> "$P/web/static/vendor/kakao_js_sdk/kakao.min.js"
OUT=$(BS "$P" --diff-base HEAD --only wv13); E=$?
check "K42b 항목만 삭제 + 사본 변조 — WV13 1" 2 "$E" "$OUT" "[WV13] BLOCKER=1"
P=$(newp k42c); G "$P" branch -q -M main; G "$P" checkout -qb lane; echo 'l' > "$P/web/static/css/lane.css"; commit "$P" lane >/dev/null
G "$P" checkout -q main; rm "$P/web/sdk_registry.json"; echo 'x' >> "$P/web/static/vendor/kakao_js_sdk/kakao.min.js"; commit "$P" "목록 삭제 + 변조" >/dev/null
G "$P" checkout -q lane; G "$P" rebase -q main >/dev/null 2>&1
OUT=$(BS "$P" --diff-base HEAD --only wv13); E=$?
check "K42c 삭제 커밋을 rebase 로 받은 레인 — WV13 1" 2 "$E" "$OUT" "[WV13] BLOCKER=1"
P=$(newp k42d); printf '{%% extends "base.html" %%}\n' > "$P/$CHART"; OUT=$(SV remove "$P" kakao_js_sdk); commit "$P" rm >/dev/null
OUT=$(BS "$P" --diff-base HEAD --only wv); E=$?
check "K42d 정상 remove(디렉터리째) — 0" 0 "$E" "$OUT" "BLOCKER=0"
OUT=$(FX install "$P" --variant again); E=$?
check "K42e 재채택 — 0" 0 "$E" "$OUT" "[sdk] 설치=1"
P=$(era_proj k51a); mkdir -p "$P/web/static/vendor/bulk"; for i in $(seq 1 200); do echo "v$i" > "$P/web/static/vendor/bulk/f$i.js"; done; commit "$P" bulk >/dev/null
S0=$(date +%s); OUT=$(BS "$P" --debt-scan); E=$?; S1=$(date +%s)
check "K51a 미등재 200파일 · 목록 이력 없음 — WV12 · 시간 상한" 2 "$E" "$OUT" "[WV12] web/static/vendor/bulk/=1"
[ $((S1-S0)) -le 20 ]; check "K51a 시간 상한(20 s)" 0 "$?" ""
must "준비 install" FX install "$P"
OUT=$(BS "$P" --debt-scan); E=$?
check "K51b 목록 이력 있음 — WV12(목록 이전 내용)" 2 "$E" "$OUT" "[WV12] web/static/vendor/bulk/=1"
git clone -q --depth 1 "file://$P" "$T/k51c" 2>/dev/null
OUT=$(BS "$T/k51c" --diff-base HEAD --only wv13); E=$?
check "K51c 얕은 클론 + 미등재 단위 — exit 1 «판정 불가»(미실행)" 1 "$E" "$OUT" "판정 불가=+"

# ---------- K43·K44: OS 잡파일 · 무시된 파일 참조
P=$(newp k43a); B=$(base_of "$P"); : > "$P/web/static/vendor/.DS_Store"; : > "$P/web/static/vendor/kakao_js_sdk/.DS_Store"
OUT=$(BS "$P" --diff-base "$B" --only wv,ws6); E=$?
check "K43a 등재 + 미추적 .DS_Store — 0" 0 "$E" "$OUT" "BLOCKER=0"
FX mkproj "$T/k43b" >/dev/null; mkdir -p "$T/k43b/web/static/vendor"; : > "$T/k43b/web/static/vendor/.DS_Store"
OUT=$(FX install "$T/k43b"); E=$?
check "K43b 목록 없음 + .DS_Store 만에서 install — 0 · 배너 줄 0" 0 "$E" "$OUT" "미등재 벤더 디렉터리: 없음=1"
G "$P" add -f web/static/vendor/kakao_js_sdk/.DS_Store
OUT=$(BS "$P" --diff-base "$B" --only wv5); E=$?
check "K43c 추적된 .DS_Store — WV5 1" 2 "$E" "$OUT" "[WV5] BLOCKER=1"
P=$(newp k44); B=$(base_of "$P"); echo 'ignored.js' > "$P/web/static/vendor/kakao_js_sdk/.gitignore_x"; rm "$P/web/static/vendor/kakao_js_sdk/.gitignore_x"
printf 'web/static/vendor/kakao_js_sdk/ign.js\n' >> "$P/.git/info/exclude"; echo 'x()' > "$P/web/static/vendor/kakao_js_sdk/ign.js"
sed -i.bak "s#kakao_js_sdk/kakao.min.js#kakao_js_sdk/ign.js#" "$P/$CHART"; rm -f "$P/$CHART.bak"
OUT=$(BS "$P" --diff-base "$B" --only wv6,wv5); E=$?
check "K44 등재 id 안 무시된 파일을 템플릿이 가리킴 — WV6 1(+ WV5 1)" 2 "$E" "$OUT" "[WV6] BLOCKER=1" "[WV5] BLOCKER=1"

# ---------- K47: 레지스트리 NFD / restore 뒤
P=$(newp k47)
python3 - "$P/web/sdk_registry.json" <<'PY'
import sys, unicodedata
p = sys.argv[1]; t = open(p, encoding='utf-8').read()
open(p, 'w', encoding='utf-8').write(unicodedata.normalize('NFD', t))
PY
OUT=$(BS "$P" --diff-base HEAD --only wv1); E=$?
check "K47a NFD 문자열 — WV1(정규 바이트)" 2 "$E" "$OUT" "정규 바이트가 아니다=1"
OUT=$(SV restore "$P" kakao_js_sdk); E=$?
check "K47b restore(ⓡ2 재정규화) 뒤 — 0" 0 "$E" "$OUT" "ⓡ2 목록 재정규화=1" "발견 0건=1"

# ---------- ⓡ1 restore — 다시 받은 바이트 = 등재 지문 / 다름
P=$(newp rst); cp "$P/web/static/vendor/kakao_js_sdk/kakao.min.js" "$T/rst-good.js"; echo 'x' >> "$P/web/static/vendor/kakao_js_sdk/kakao.min.js"
OUT=$(SDKFX_FETCH="{\"$SRC\": [\"$SRC\", \"application/javascript\", \"$T/rst-good.js\"]}" FX vendor restore "$P" kakao_js_sdk); E=$?
check "ⓡ1 restore — 등재 바이트 복원 0" 0 "$E" "$OUT" "ⓡ1 등재 바이트 복원=1"
echo 'y' >> "$P/web/static/vendor/kakao_js_sdk/kakao.min.js"
OUT=$(SDKFX_FETCH="{\"$SRC\": [\"$SRC\", \"application/javascript\", \"$T/sdk.js.bad\"]}" FX vendor restore "$P" kakao_js_sdk); E=$?
check "ⓡ1 restore — 원본을 받지 못하면 거절 2" 2 "$E" "$OUT" "거절=1"

echo "fixtures_sdk: PASS=$PASS FAIL=$FAIL"
[ "$FAIL" = 0 ]
