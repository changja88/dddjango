# dddjango-web 모션 검증 결정론화 — 인수 기록 (계획 §2 런북 완주)

- 실행: 2026-08-25 · 준거: `workspace/plan/2026-08-25-web-motion-determinism-plan.md` v2 §2.
- **판정: 런북 1~6 전건 충족.**

## 1. make verify — 전 그룹 green

verify-web 포함 전체 green. 신규 픽스처: `fixtures_audit.sh` 22케이스(V2·S2·RV·W1v·MIX·
Wb·Ws·Wz·A1v2·DETv2 등 — 기존 11케이스 회귀 0) · `fixtures_motion_spec.sh` 14케이스
(G1·G2 green 짝 ↔ R1 전수성·R2 좌표 부재·R3 값 토큰·R4 역스윕 발명·R5 판형 위반 red ·
W1 레거시 산문·W2 미관찰·W3 전사 이음매 warn·U1/U2·DET). 모든 negative가 실제 red를
내는 것을 positive-control 짝과 함께 확인. verify-web의 codex 미러 byte 대조
(scripts·assets) 신설분도 green.

## 2. 실물 실증 — 2-origin 합성 페이지 + 실제 브라우저 (세션 브라우저 자동화 도구)

합성 페이지: `@keyframes fadein`+`.hero` animation · `.cta` transition+`:hover` ·
상태 클래스 게이트 transition(`.status.on`) · `@media (prefers-reduced-motion)` 내
`[data-motion]` 은닉 판형 · cross-origin 시트(`127.0.0.1:8766/remote.css` — CORS 없음) ·
`window.gsap` 전역 스텁 · `[data-aos]` DOM 흔적. 실행: 스니펫 v2 전문을 fetch+eval로
실행 후 `window.__renderAudit` 평가 채널 회수(재량 대행 경로의 판형 그대로).

실측 결과(전 축 설계 일치):
- `transitions` 2건 — duration 술어가 정확히 `.cta`(box-shadow)·`.status`(color)만 포착
  (**`transition-property` 초기값 all 오탐 0** — 계획 blocker 수리 실증). 텍스트 리프
  키(`확인 중 #명` — 숫자 접기)·비텍스트 시그니처 키 규약 동작.
- `transitionRules` 3건 — **@media 내부의 상태 클래스 게이트형**
  (`html.motion-ready [data-motion].motion-in`) 포착(그룹 규칙 재귀 실증).
- `keyframes` [fadein] · `animationRules` 1건(`.hero`) · `hoverSelectors` [.cta:hover] ·
  `focusSelectors` [a:focus-visible].
- `sheets {total 3, readable 2, blocked [remote.css]}` — cross-origin 자기 신고 실증.
- `blind_spots` [global:gsap, dom:[data-aos]] — 전역+DOM 흔적 이중 감지 실증.
- 요약 행에 `motion tr 2/kf 1/hover 1 · 차단 시트 1 · 측정 밖 엔진 2` 표기.

회수 JSON을 `--validate --require-version 2`로 왕복: **validate OK** + 커버리지 warn
2행(부분성·측정 밖 엔진) 정확 발화.

## 3. compare 판형 3조합 (픽스처로 고정)

- v1↔v1: exit·diff 판정 불변 + `[warn] v1 실측 — motion 축 미대조` 1행(W1v).
- v1↔v2: `[warn] 실측 버전 불일치` (MIX).
- v2↔v2: `INFO 모션 인벤토리(계수 요약…)` + 커버리지 warn(A1v2·Wb·Ws·Wz). DET·DETv2
  결정론(2회 byte 동일) 유지.

## 4. check_motion_spec 왕복 (픽스처로 고정)

red 5형(전수성·좌표 부재·값 토큰 미정의·역스윕 발명·판형 위반) · warn 3형(레거시 산문
exit 0·미관찰 미검증·--audit 전사 계수 게이트) · green 3형(css-hover·css-keyframes·
러너[data-motion+base.html 로드 태그+은닉 판형] 합성 web/ 트리) · --spec-only/--audit 왕복.

## 5. 미러·문면 전수 반영

- byte 동일: `scripts/`(compare·check_motion_spec·fixtures 2종)·`assets/`(render_audit.js)
  ↔ codex 대응 — verify-web의 diff 대조가 상시 소유.
- 의미 미러: codex Coordinator SKILL.md 15쌍·에이전트 SKILL.md 3종 5쌍 — 전 쌍 1회 매치
  강제 스크립트로 적용(`${SKILL_DIR}`·«네이티브 셸» 토큰 변환·«Agent 위임»→«서브에이전트
  위임» 중립화).
- 문면 6종: commands + design-architect-web + design-review-web + architecture-web §8 +
  implementation-ui §7 + discipline-reviewer-web(분업 1줄). coder-web 불요(근거: 모션
  소비는 implementation-ui §7 로드 경유 — 자체 문면에 관련 언급 없음).
- 스펙 D13 v2 행 교체(사용자 확정 2026-08-25 — 러너 폐기·재량 대행 4조건 공인).
- Makefile 수정에 따른 T2-0b 봉인 재발행(manifest_seal --write) 완료.

## 6. 조감도

`workspace/design/ontology-adoption-map.html`에 이력 행 1건 추가(2026-08-25 — 모션 검증
결정론화).

## 추기 — 구현 대조·코드 감사 처분 (2인 패널 → 전건 해소)

**대조 리뷰(계획↔구현 57조항)**: 이행 52·부분 4·무해 누락 1·개선성 이탈 1(A1v2 픽스처) ·
**무단 이탈 0**(미커밋 28파일 전수 소속 판정). 수리 1건 — review-web :13 입력 판형을 양
미러에 보강. 수용 4건 — :124(원문이 이미 신 의미론과 정합)·blocked↔동결 대응은 Coordinator
문면 소관(등가)·러너 로드 태그 검사 비한정(완화 방향 근사)·focusSelectors는 합산에 추가.

**코드 감사(발견 20·REFUTED 15 — 실브라우저 재현 포함)**: major 3 전건 수리 —
① **@import 1단 하강**(walkRules CSSImportRule — 실패는 blocked 신고. 수리 후 실브라우저
재실증: imported keyframes·hover 수집 확인) ② **값 토큰 사용 검사 정규식화**
(`var(--x[,)])` — 접두 부분 문자열 false-pass 차단·R3b 픽스처) ③ **빈 id 행 증발 차단**
(STATUS_IDS에서 "" 제거 — 판형 위반 FINDING·전수성 모수는 유효 id만·R6 픽스처).
minor 수리 12 — 코드 펜스 skip(G4)·주석 strip(역스윕·존재 검사 — G3)·`\|` 이스케이프·
러너 행 토큰 정의 검사·data-motion 홑따옴표+동적 값 FINDING·partial v2 골격 선대입·
0s 리셋 규칙 제외·상태 행 마커 전 칼럼 검색+무마커 warn·중복 id FINDING·sheets 타입
검증·S2/R3 단언 조이기·focusSelectors 합산·pinned 비교기·shadow-root 자기 신고·
«전부 동기·결정적» 주석 한정 조건·역스윕 문면 축소(@keyframes·data-motion 한정 — 양 미러).
PLAUSIBLE 수용 1 — 동적 페이지에서 실행이 상태를 바꿀 수 있음(주석 명기로 갈음).

수리 후: `fixtures_motion_spec` 19케이스·`fixtures_audit` 22케이스 green ·
미러 재동기(byte diff 0) · `make verify` 전 그룹 green 재확인.
