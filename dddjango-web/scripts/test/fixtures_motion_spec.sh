#!/usr/bin/env bash
# dddjango-web 모션 처분 표 검사기(check_motion_spec) 자기 회귀 픽스처.
# 케이스마다 negative(발견)에 positive-control(정상 통과) 짝을 둔다:
#   G1(--spec-only 정상) · G2(full 정상 — css-hover·css-keyframes·러너 3형 합성 web/)
#   ↔ R1(전수성)·R2(좌표 파일 부재)·R3(값 토큰 미정의)·R4(역스윕 발명)·R5(표 판형 위반)
#   W1(레거시 산문 → warn·exit 0) · W2((미관찰)+0행 → 미검증 warn) · W3(--audit 전사 계수 게이트)
#   U1(사용법)·U2(파일 부재) · DET(같은 red 입력 2회 byte 동일)
# 표 판형·검사 축 정의는 check_motion_spec.py 헤더와 계획
# workspace/plan/2026-08-25-web-motion-determinism-plan.md W4가 소유한다.
set -u
SCRIPTS="$(cd "$(dirname "$0")/.." && pwd)"
PASS=0; FAIL=0

run_py() { python3 "$SCRIPTS/$1" "${@:2}" 2>&1; }

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

# ---------- 표본 생성: 관찰 표·처분 표·합성 web/ 트리
cat > "$T/notes.md" <<'EOF'
# 동적 표현 관찰 기록

| id | 요소 | 트리거 | 효과 | 재현 분류(예상) | 출처 |
|---|---|---|---|---|---|
| m1 | 주문 카드 | hover | 그림자 상승 0.3s ease-out | CSS | 실측 |
| m2 | 히어로 | load | 페이드인 0.6s | CSS | 문답 |
| m3 | 목록 항목 | scroll | 진입 페이드 0.6s | 러너 | 문답 |
| m4 | 비밀번호 표시 | click | 아이콘 회전 0.3s | UI JS | 실측 |
EOF

cat > "$T/spec.md" <<'EOF'
## 동적 표현 처분

| note id | 처분 | 분류 | 구현 좌표 | 값 | 근거 |
|---|---|---|---|---|---|
| m1 | 채택 | css-hover | web/order_list/order_list.css :: .order_card:hover | var(--duration-fast) var(--ease-out) | 원본 hover 재현 |
| m2 | 채택 | css-keyframes | web/design_system/foundation/motion.css :: motion-fade | var(--duration-reveal) | 원본 로드 페이드 |
| m3 | 채택 | 러너 | reveal | var(--duration-reveal) | 스크롤 진입 발동 |
| m4 | 채택 | ui-js | static/js/password_visibility.js :: [data-password-visibility] | var(--duration-fast) | 승인된 UI 동작 계약과 실제 클릭 검증에 연결 |
EOF

W="$T/proj/web"
mkdir -p "$W/design_system/foundation" "$W/order_list" "$W/static/js"
cat > "$W/design_system/foundation/tokens.css" <<'EOF'
:root { --duration-fast: 0.3s; --duration-reveal: 0.6s; --ease-out: ease-out; }
EOF
cat > "$W/design_system/foundation/motion.css" <<'EOF'
@keyframes motion-fade { from { opacity: 0; } to { opacity: 1; } }
@media (prefers-reduced-motion: no-preference) {
  html.motion-ready [data-motion] { opacity: 0; }
  html.motion-ready [data-motion].motion-in { opacity: 1; transition: opacity var(--duration-reveal) var(--ease-out); }
}
EOF
cat > "$W/order_list/order_list.css" <<'EOF'
.order_card:hover { box-shadow: 0 2px 8px rgb(0 0 0 / 0.2); transition: box-shadow var(--duration-fast) var(--ease-out); }
EOF
cat > "$W/base.html" <<'EOF'
<link rel="stylesheet" href="{% static 'design_system/foundation/motion.css' %}">
<script src="{% static 'web/js/motion.js' %}" defer></script>
EOF
cat > "$W/order_list/order_list.html" <<'EOF'
<li data-motion="reveal">항목</li>
<div data-password-visibility><input type="password"><button type="button">표시</button></div>
EOF
cat > "$W/static/js/password_visibility.js" <<'EOF'
document.querySelectorAll('[data-password-visibility]');
EOF

# 감사 처분 회귀 표본(2026-08-25 감사 — major 2·minor 3)
# R3b 토큰 접두 오탐: 명세는 --duration-fast·구현은 --duration-faster만 사용(둘 다 정의)
cp -R "$T/proj" "$T/proj-prefix"
cat > "$T/proj-prefix/web/design_system/foundation/tokens.css" <<'EOF'
:root { --duration-fast: 0.3s; --duration-faster: 0.15s; --duration-reveal: 0.6s; --ease-out: ease-out; }
EOF
sed 's#var(--duration-fast)#var(--duration-faster)#' "$T/proj/web/order_list/order_list.css" > "$T/proj-prefix/web/order_list/order_list.css"
# R6 빈 id 행(상태 행 아님 — 조용한 증발 금지) · R7 처분 표 중복 id
cat > "$T/notes-blankid.md" <<'EOF'
| id | 요소 | 트리거 | 효과 | 재현 분류(예상) | 출처 |
|---|---|---|---|---|---|
|  | 카드 | hover | 그림자 | CSS | 실측 |
EOF
{ cat "$T/spec.md"; grep '^| m1 ' "$T/spec.md" | sed 's/| 채택 |/| 기각 |/'; } > "$T/spec-dup.md"
# G3 주석 속 @keyframes 잔재(역스윕 침묵해야) · G4 코드 펜스 안 판형 예시 표(무시해야)
cp -R "$T/proj" "$T/proj-comment"
echo '/* 구버전 잔재: @keyframes old-spin { to { opacity: 0; } } */' >> "$T/proj-comment/web/order_list/order_list.css"
{ printf '판형 예시:\n\n```\n| note id | 처분 | 분류 | 구현 좌표 | 값 | 근거 |\n|---|---|---|---|---|---|\n| m9 | 채택 | css-hover | 좌표 | 값 | 예시 |\n```\n\n'; cat "$T/spec.md"; } > "$T/spec-fenced.md"

# 변형: R1 전수성(처분 표에서 m1 삭제) · R5 판형 위반(5칼럼 행)
grep -v '^| m1 ' "$T/spec.md" > "$T/spec-missing.md"
{ cat "$T/spec.md"; echo '| m9 | 채택 | css-hover | 좌표 | 값 |'; } > "$T/spec-malformed.md"
# R2 좌표 파일 부재 · R3 값 토큰 미정의
sed 's#web/order_list/order_list.css#web/ghost.css#' "$T/spec.md" > "$T/spec-ghostfile.md"
sed 's#var(--duration-fast)#var(--duration-slow)#' "$T/spec.md" > "$T/spec-badtoken.md"
sed 's#static/js/password_visibility.js#static/js/ghost.js#' "$T/spec.md" > "$T/spec-ui-ghostfile.md"
# R4 역스윕 발명(처분 표 밖 @keyframes)
cp -R "$T/proj" "$T/proj-rogue"
echo '@keyframes rogue-spin { to { transform: rotate(360deg); } }' >> "$T/proj-rogue/web/order_list/order_list.css"
cp -R "$T/proj" "$T/proj-ui-js-comment"
cat > "$T/proj-ui-js-comment/web/static/js/password_visibility.js" <<'EOF'
// document.querySelectorAll('[data-password-visibility]');
document.querySelectorAll('button');
EOF
cp -R "$T/proj" "$T/proj-ui-js-interpolation-comment"
cat > "$T/proj-ui-js-interpolation-comment/web/static/js/password_visibility.js" <<'EOF'
const label = `${ /* [data-password-visibility] */ "button" }`;
EOF
cp -R "$T/proj" "$T/proj-ui-js-backtick"
cat > "$T/proj-ui-js-backtick/web/static/js/password_visibility.js" <<'EOF'
document.querySelectorAll(`[data-password-visibility]`);
EOF
cp -R "$T/proj" "$T/proj-ui-html-comment"
cat > "$T/proj-ui-html-comment/web/order_list/order_list.html" <<'EOF'
<li data-motion="reveal">항목</li>
<!-- <div data-password-visibility></div> -->
{% comment %}<div data-password-visibility></div>{% endcomment %}
<div data-other=" data-password-visibility "></div>
EOF
# W1 레거시 산문 notes · W2 (미관찰) 상태 행만
cat > "$T/notes-legacy.md" <<'EOF'
- 카드 / hover / 그림자 상승 / CSS
EOF
cat > "$T/notes-unobserved.md" <<'EOF'
| id | 요소 | 트리거 | 효과 | 재현 분류(예상) | 출처 |
|---|---|---|---|---|---|
| — | (미관찰) | — | — | — | 사유: 사용자 생략 |
EOF
printf '## 동적 표현 처분\n\n(관찰 없음)\n' > "$T/spec-empty.md"
# W3 전사 계수 게이트 — 실측 인벤토리는 있는데 notes 출처가 전부 문답
sed 's/| 실측 |/| 문답 |/' "$T/notes.md" > "$T/notes-nofrom.md"
cat > "$T/audit-v2.json" <<'EOF'
{"audit_version": 2, "motion": {"transitions": [{"key": "a", "property": "opacity", "duration": "0.3s", "easing": "ease"}],
 "transitionRules": [], "keyframes": ["x"], "animationRules": [], "hoverSelectors": [], "focusSelectors": [],
 "sheets": {"total": 1, "readable": 1, "blocked": []}, "blind_spots": [], "caps_hit": []}}
EOF

# ---------- G1(positive control): --spec-only 정상
OUT=$(run_py check_motion_spec.py --spec-only "$T/spec.md" "$T/notes.md"); E=$?
assert "G1 spec-only 정상" 0 "발견 0건" "FINDING" "$E" "$OUT"

# ---------- G2(positive control): full 정상 — 3형(css-hover·css-keyframes·러너)
OUT=$(run_py check_motion_spec.py "$T/spec.md" "$T/notes.md" "$W"); E=$?
assert "G2 full 정상 3형" 0 "발견 0건" "FINDING" "$E" "$OUT"

# ---------- R1: 전수성 — notes m1이 처분 표에 없음
OUT=$(run_py check_motion_spec.py --spec-only "$T/spec-missing.md" "$T/notes.md"); E=$?
assert "R1 전수성 위반" 2 "전수성: notes m1" - "$E" "$OUT"

# ---------- R2: 좌표 파일 부재
OUT=$(run_py check_motion_spec.py "$T/spec-ghostfile.md" "$T/notes.md" "$W"); E=$?
assert "R2 좌표 파일 부재" 2 "좌표 파일 없음" - "$E" "$OUT"

# ---------- R3: 값 토큰 미정의
OUT=$(run_py check_motion_spec.py "$T/spec-badtoken.md" "$T/notes.md" "$W"); E=$?
assert "R3 값 토큰 미정의" 2 "정의가 web/ CSS 어디에도 없음" - "$E" "$OUT"

# ---------- R4: 역스윕 — 처분 표 밖 @keyframes 발명
OUT=$(run_py check_motion_spec.py "$T/spec.md" "$T/notes.md" "$T/proj-rogue/web"); E=$?
assert "R4 역스윕 발명" 2 "rogue-spin" - "$E" "$OUT"

# ---------- R4b: ui-js 좌표 파일·JS literal root·실제 HTML attribute 근거
OUT=$(run_py check_motion_spec.py "$T/spec-ui-ghostfile.md" "$T/notes.md" "$W"); E=$?
assert "R4b ui-js 유령 파일" 2 "ui-js 좌표 파일 없음" - "$E" "$OUT"
OUT=$(run_py check_motion_spec.py "$T/spec.md" "$T/notes.md" "$T/proj-ui-js-comment/web"); E=$?
assert "R4c ui-js 주석 속 JS root는 근거 아님" 2 "JS에 literal root 없음" - "$E" "$OUT"
OUT=$(run_py check_motion_spec.py "$T/spec.md" "$T/notes.md" "$T/proj-ui-js-interpolation-comment/web"); E=$?
assert "R4c2 ui-js template interpolation 주석 root는 근거 아님" 2 "JS에 literal root 없음" - "$E" "$OUT"
OUT=$(run_py check_motion_spec.py "$T/spec.md" "$T/notes.md" "$T/proj-ui-html-comment/web"); E=$?
assert "R4d ui-js HTML 주석 속 root는 근거 아님" 2 "HTML에 실제 root 속성 없음" - "$E" "$OUT"

# ---------- R5: 표 판형 위반(칼럼 수)
OUT=$(run_py check_motion_spec.py --spec-only "$T/spec-malformed.md" "$T/notes.md"); E=$?
assert "R5 판형 위반" 2 "판형 위반" - "$E" "$OUT"

# ---------- R3b: 값 토큰 접두 오탐 차단 — --duration-fast 요구에 --duration-faster 사용 → red
OUT=$(run_py check_motion_spec.py "$T/spec.md" "$T/notes.md" "$T/proj-prefix/web"); E=$?
assert "R3b 토큰 접두 false-pass 차단" 2 "사용이" - "$E" "$OUT"

# ---------- R6: id 빈칸 모션 행 — 상태 행으로 증발하지 않고 판형 위반 red
OUT=$(run_py check_motion_spec.py --spec-only "$T/spec-empty.md" "$T/notes-blankid.md"); E=$?
assert "R6 빈 id 행 조용한 증발 금지" 2 "id 판형 위반" - "$E" "$OUT"

# ---------- R7: 처분 표 중복 id(채택+기각 병존) → red
OUT=$(run_py check_motion_spec.py --spec-only "$T/spec-dup.md" "$T/notes.md"); E=$?
assert "R7 처분 표 중복 id" 2 "중복 id" - "$E" "$OUT"

# ---------- G3(positive control): 주석 속 @keyframes 잔재 — 역스윕 침묵
OUT=$(run_py check_motion_spec.py "$T/spec.md" "$T/notes.md" "$T/proj-comment/web"); E=$?
assert "G3 주석 keyframes 역스윕 침묵" 0 "발견 0건" "old-spin" "$E" "$OUT"

# ---------- G4(positive control): 코드 펜스 안 판형 예시 표 — 실표로 오파스 금지
OUT=$(run_py check_motion_spec.py --spec-only "$T/spec-fenced.md" "$T/notes.md"); E=$?
assert "G4 펜스 예시 표 무시" 0 "발견 0건" "m9" "$E" "$OUT"

# ---------- G5(positive control): ui-js web/ 선행 경로도 같은 파일로 해소
sed 's#static/js/password_visibility.js#web/static/js/password_visibility.js#' "$T/spec.md" > "$T/spec-ui-web-prefix.md"
OUT=$(run_py check_motion_spec.py "$T/spec-ui-web-prefix.md" "$T/notes.md" "$W"); E=$?
assert "G5 ui-js optional web prefix" 0 "발견 0건" "FINDING" "$E" "$OUT"

# ---------- G6(positive control): backtick 안 literal root는 구조 근거로 인정
OUT=$(run_py check_motion_spec.py "$T/spec.md" "$T/notes.md" "$T/proj-ui-js-backtick/web"); E=$?
assert "G6 ui-js backtick literal root" 0 "발견 0건" "FINDING" "$E" "$OUT"

# ---------- W1: 레거시 산문 notes → warn + exit 0 (합법 재빌드 비차단)
OUT=$(run_py check_motion_spec.py --spec-only "$T/spec.md" "$T/notes-legacy.md"); E=$?
assert "W1 레거시 산문 warn" 0 "레거시 산문 판형" "FINDING" "$E" "$OUT"

# ---------- W2: (미관찰) 상태 행만 + 처분 0행 → 미검증 warn (없음-확인과 구별)
OUT=$(run_py check_motion_spec.py --spec-only "$T/spec-empty.md" "$T/notes-unobserved.md"); E=$?
assert "W2 미관찰 미검증 warn" 0 "미검증(관찰 생략" "FINDING" "$E" "$OUT"

# ---------- W3: --audit 전사 계수 게이트 — 실측 인벤토리 있는데 출처=실측/스캔 행 0
OUT=$(run_py check_motion_spec.py --spec-only "$T/spec.md" "$T/notes-nofrom.md" --audit "$T/audit-v2.json"); E=$?
assert "W3 전사 이음매 warn" 0 "전사 이음매" - "$E" "$OUT"

# ---------- W3p(positive control): 출처=실측 행이 있으면 게이트 침묵
OUT=$(run_py check_motion_spec.py --spec-only "$T/spec.md" "$T/notes.md" --audit "$T/audit-v2.json"); E=$?
assert "W3p 전사 게이트 침묵" 0 "발견 0건" "전사 이음매" "$E" "$OUT"

# ---------- U1: 사용법 → exit 1
OUT=$(run_py check_motion_spec.py); E=$?
assert "U1 사용법" 1 "사용" - "$E" "$OUT"

# ---------- U2: 파일 부재 → exit 1 (미실행 취급)
OUT=$(run_py check_motion_spec.py --spec-only "$T/none.md" "$T/notes.md"); E=$?
assert "U2 파일 부재 fail-loud" 1 "파일 없음" - "$E" "$OUT"

# ---------- DET: 결정론 — 같은 red 입력 2회 byte 동일 출력
O1=$(run_py check_motion_spec.py "$T/spec-badtoken.md" "$T/notes.md" "$W")
O2=$(run_py check_motion_spec.py "$T/spec-badtoken.md" "$T/notes.md" "$W")
if [ "$O1" = "$O2" ]; then PASS=$((PASS+1)); echo "PASS DET 결정론(2회 동일)"; else
  FAIL=$((FAIL+1)); echo "FAIL DET 결정론(2회 동일)"; diff <(echo "$O1") <(echo "$O2") | head -10 | sed 's/^/    /'
fi

echo "----------------------------------------"
echo "fixtures_motion_spec: PASS $PASS · FAIL $FAIL"
[ $FAIL = 0 ] || exit 1
