# L1 재설계 — G1 트레이드오프 처리 (스펙 v3)

> 상태: **구현 완료(2026-06-10) — 4파일+미러 편집, dual 라이브 미검증.** 변경: `dddjango/agents/design-architect.md`(입력 절 G1 override 항목 + §36 멱등성 가드 Y화)·`dddjango/commands/dddjango.md`(Phase 1 step4~5 + G1 결정 처리 + G1')·Codex 미러 2(`codex-dddjango/skills/dddjango-design-architect/SKILL.md`·`.../dddjango/SKILL.md`). 새 스크립트·coordinator의 design-spec 쓰기 0. 다음 = 버전 bump·커밋(사용자 확인)·dual 라이브.
> 출처: `workspace/flow/flow-review.md` 트랙 C → L1. v1(결정적 mutator 스크립트)=NO-GO. v1.5(3분기 Y/X/Z)=X 폐기·Y 한정 요구. v2(2분기)=FIX-THEN-SHIP(override 경로 디테일 공백). **v3 = override(Z)·백스톱 ⑩ 충돌·Y 결정적 앵커 보강.**
> ROI: **확정** — 사용자 경험 N≈20 "G1 기본 수락 흔함". 날짜: 2026-06-10.

---

## 1. Context — 왜 바꾸나

### 문제 (flow-review 트랙 C)
G1에서 사용자가 트레이드오프를 결정하면, coordinator가 그 결정을 `design-spec.md`에 반영하려고 **design-architect를 통째로 재호출("잠금")**한다. 비용: architect 풀 스핀업(~5~10분, 서브 compute ~5~8%) + LLM 프로즈 재작성 → **비결정적**. duplive·cbvlive 라이브서 관측.

### 중요 사실 — 이 잠금은 *문서에 없는* 동작
현행 `commands/dddjango.md` Phase 1은 architect를 **2번**만 명시(step 1 초안 line 72, step 4 반영·중재 line 75 — "미해결 트레이드오프는 G1 배너에 옵션으로 제시"). 둘 다 **G1 배너(line 76) *전***. 사용자 결정 *후* "잠금 재호출"은 문서에 없고 coordinator가 추론해 한다. → L1이 새로 명문화해야 하며, 검증된 기존 인터페이스가 아니다.

### v1·v1.5·v2가 다듬어진 이유 (부록 §A)
- **v1**(스크립트): 결정성 이동·mutator 안전계약 파괴·미러 붕괴·doctrine 위반 → 폐기.
- **v1.5**(3분기): **X(coordinator가 design-spec 직접 Edit)** = Claude `Edit` 미허가·Codex 역할계약(SKILL.md:135) 위반·LLM 비결정 치환 → X 폐기.
- **v2**(2분기): 뼈대 견고하나 **override(Z) 경로가 백스톱 ⑩과 충돌**(아래 §3.4)하고 Y 앵커가 회색지대 판정을 남김 → v3에서 보강.

---

## 2. 핵심 통찰

결정의 *성격*이 다르다: (a) 결정 *기록*(라벨, 변수 거의 없음) vs (b) 설계 *내용* 반영(실작업, architect 필요). 그리고 **architect는 G1 대화에 없다**(step 1·4서 돌고 끝). "무엇을 물었나/사용자가 뭐라 했나"는 coordinator가 보관 — `design-architect.md:50`("결정 이력은 coordinator 대화·게이트 배너가 가짐"). override 시 coordinator가 architect에 결정을 전달하며, 그 전달 형식은 §4에서 명문화한다.

**소유권 사실**(v3 핵심): `scope.md`는 **coordinator 소유**(`commands/dddjango.md:59`·Codex SKILL.md:135 "coordinator는 스코프 메모와 검증 보고를 쓴다"). `design-spec.md`는 **architect 소유**. v3는 coordinator가 design-spec은 안 건드리되 *자기 소유*인 scope.md는 갱신할 수 있음을 활용한다(§3.4).

---

## 3. 설계 v3 — 2분기 (Y / Z)

| # | 결정 성격 | 빈도 | 처리 | architect 재호출 | 결정성 |
|---|---|---|---|---|---|
| **Y** | **scope.md가 "범위 아님 / 필요 시 G1 제안"으로 명시한 항목** (기본 = 미적용) | **흔함** (N≈20) | architect가 step 4에서 **기본(미적용)을 명세에 현재-상태로 commit** + 배너에 "추가 안 함 — 추가할래?" | **0** (수락 시) | ✓ |
| **Z** | **그 외 전부** — 양자택일·순수 비즈니스 선택·리뷰어 충돌·override·ripple | 나머지 | **architect**(현행 "G1 옵션 제시" + override 시 재호출) | 1 (발생 시) | 오늘과 동일 |

**coordinator는 design-spec.md를 전혀 안 건드린다.** (scope.md는 §3.4 한정 갱신)

**한 줄 원칙:** *scope.md에 "범위 아님"으로 이미 적힌 항목만 기본을 미리 commit해(Y) 수락 시 재호출을 없애고, 나머지 모든 결정은 architect에 맡긴다(Z).*

### 3.1 Y의 앵커 — *판정*이 아니라 scope.md의 명시 목록 (B1-b·결정성 해소)
Y는 architect가 "이게 추가형이냐 / Y감이냐"를 *판정*하지 않는다. **`scope.md`의 "범위 아님" 절에 `필요 시 G1 제안`으로 적힌 항목**에만 적용한다(이 목록은 coordinator가 Phase 0에서 `commands:59` 규칙으로 작성). 그 항목은 정의상 **기본 = 미적용**(스코프가 미요청). 닫힌 앵커이므로 architect 판정 여지가 0이다.
- 예: 미요청 멱등성, 미요청 재시도 정책 등 — **단, scope.md에 명시된 것만.** scope.md에 없으면 Y 대상 아님.
- scope.md에 안 적힌 트레이드오프(양자택일·순수선택·리뷰어 충돌)는 **전부 Z**.

### 3.2 doctrine 호환 + 제자리 수정 타깃 (M2 정정)
- Y의 commit은 *현재 상태*("멱등성 미적용") → `design-architect.md:44`·`:50` 위반 아님.
- 행위 변경(열어 제시 → 기본 commit)이 닿는 정확한 위치는 **`design-architect.md:36`**(멱등성·견고성 G1 표면화 문장). 이 문장을 *제자리 수정*한다.
- **`design-architect.md:21`(BC 배치)·:40(판정소유/blast)·:52(일반 트레이드오프 옵션 제시)는 Z 영역 → 손대지 않는다.** (v2가 :21·:52를 타깃으로 잘못 지목한 것 정정)

### 3.3 적대 리뷰 이력
- **R1** (v1 스크립트): NO-GO×2 → 스크립트·mutator 폐기.
- **R2** (v1.5 3분기): FIX-THEN-SHIP + NO-GO, 수렴 → X 폐기·Y 한정·Z 인터페이스 신설·측정.
- **R3** (v2 2분기): FIX-THEN-SHIP×2 → **B1(⑩ 충돌)·Y 앵커·Z 인터페이스 형식·M2 타깃·댕글링 참조** 보강 = 본 v3.

### 3.4 override → 백스톱 ⑩ 충돌 해소 (B1, v3 신설)
**문제**: Y가 "멱등성 미적용"을 commit했는데 사용자가 G1에서 **override해 "멱등성 추가"를 택하면(Z)** → architect가 멱등성을 명세에 씀 → 그러나 scope.md는 여전히 "미요청" → **백스톱 ⑩(idempotency-scope-creep)이 정당한 G1-승인 멱등성을 거짓 차단(exit 2)**. ⑩의 면제는 "G1 승인 배너" 토큰을 요구하나 design-spec doctrine(:44·:50)이 그 배너를 금지 → 상호 배타. (R3 파이프라인 리뷰가 파이썬으로 실증.)

**해소**: override로 **scope-미요청 기능을 채택**하면, **coordinator가 자기 소유 파일 `scope.md`를 갱신**한다 — 해당 항목을 "범위 아님 / 필요 시 G1 제안"에서 **"G1 채택 (사용자 승인)"**으로 옮긴다. 그러면:
- ⑩의 `_scope_says_not_requested`가 False가 되거나 `_user_adopted` 면제가 발화 → **거짓 차단 소멸.**
- **design-spec은 doctrine-clean**(architect는 멱등성을 현재-상태로만 쓰고 배너 불요).
- **경계 위반 아님**(scope.md는 coordinator 소유, design-spec과 다름 — X 부활 아님).
- **면제 문구 규약**(M1-fragility): scope.md 채택 줄은 `아님`·`않는다` 등 ⑩의 `_REJECT_TOKENS`를 같은 줄에 두지 않는다(예: "멱등성: G1 채택 (사용자 승인)" 단독 줄).
- §6 "백스톱 변경=비목표"는 **유지**된다 — ⑩을 바꾸는 게 아니라 coordinator가 scope.md를 갱신해 ⑩의 *기존* 면제를 발화시키는 것이다.

### 3.5 v1.5와의 차이 (안전 근거 요약)
스크립트 0 · coordinator의 **design-spec 쓰기 0**(scope.md만, 소유 파일) · 단일 작성자(design-spec=architect) 보존 · 양 런타임 동형.

---

## 4. 변경 대상 (파일) — 새 스크립트·coordinator의 design-spec 쓰기 *없음*

1. **`dddjango/agents/design-architect.md:36`** — *제자리 수정*: 멱등성·견고성 문장을 "**scope.md가 '범위 아님 / 필요 시 G1 제안'으로 명시한 항목은 기본(미적용)을 명세에 현재-상태로 commit하고 배너용 'override 가능' 항목으로 산출**한다"로. line 21·40·52는 불변(Z).
2. **`dddjango/agents/design-architect.md` "입력" 절** (line 14~21 영역) — **override 입력을 1급 항목으로 신설** (M1): 형식 = `G1 override (있으면): [항목명] 기본=미적용 → 채택  |  [항목명] 옵션A → 옵션B. 지시: 해당 절만 제자리 갱신, 타 절 불변.` Claude·Codex byte-identical.
3. **`dddjango/commands/dddjango.md` Phase 1** (line 75~76):
   - step 4 산출: Y는 commit+override 항목, Z는 옵션(현행).
   - G1 배너 *후* 분기 명문화: **수락 → 무작업 진행** / **Y 항목 override 채택 → coordinator가 scope.md를 "G1 채택"으로 갱신(§3.4) + architect 재호출(Z, §4 항목 2 형식)** / **그 외 override·순수선택 → architect 재호출(Z)**. coordinator의 design-spec Edit 절은 두지 않는다.
4. **수정 모드 G1'** (commands 수정 모드 절) — Y/Z 분기·§3.4 ⑩ 처리가 G1'에도 동일 적용됨을 1줄 명시(m2).
5. **Codex 미러** byte-identical: `codex-dddjango/skills/dddjango/`(coordinator) + `codex-dddjango/skills/dddjango-design-architect/`. coordinator가 design-spec을 안 쓰므로 Codex 역할계약(SKILL.md:135)과 충돌 없음.

---

## 5. 결정성 분석

| 경로 | 사후 LLM 작성 | 결정성 |
|---|---|---|
| Y 수락 | 없음 | 완전(명세=step 4 architect 1회, 단일 작성자) |
| Y override 채택 | coordinator scope.md 1줄(규약 고정) + architect 재작성 | scope.md=규약 고정 줄(결정적) / 명세=architect(오늘과 동일) |
| Z (옵션/override) | architect 재작성 | 오늘과 동일 |

coordinator는 design-spec을 안 쓴다 → 단일 작성자 보존. 어느 경로도 현행보다 결정성이 나빠지지 않고, 흔한 Y 수락은 *더* 결정적.

---

## 6. 비목표
- Z 최적화 — 의도적 architect 유지(위험·드묾).
- 백스톱·리뷰 단계 *코드* 변경 — flow-review 트랙 A·B 결론. (§3.4는 ⑩을 *바꾸지 않고* coordinator의 scope.md 갱신으로 기존 면제를 쓴다.)
- 새 결정적 스크립트·coordinator의 design-spec 쓰기 — 폐기.

---

## 7. 검증 계획
1. **측정** — ✅ 불요 (N≈20).
2. **구현 후 dual 라이브 N≥2** (Claude·Codex):
   - (a) Y 수락 시 architect 재호출 **0회**,
   - (b) override 시 architect 재호출 + §4 항목 2 입력 형식 작동,
   - (c) **Y override 채택 시 백스톱 ⑩ exit 0** (coordinator scope.md 갱신이 면제를 발화 — B1 회귀 검증),
   - (d) 같은 입력 → 같은 명세(결정성),
   - (e) Codex 역할계약·도구셋 충돌 없음.
3. 미러 byte-identical 확인.

---

## 8. 리스크
- **R1** (잔존): Y의 "기본 commit + 배너 override"가 rubber-stamp 유발? → 배너가 기본 선택을 분명히 드러내야(현행 G1과 동급).
- **R2·R3** (해소): X 경계/도구/미러 → X 폐기. ROI → N≈20.
- **R4** (작음): L1 천장 = 수락 run당 architect 1회(~5~8%). 실효 있으나 작음. 더 큰 레버는 L2.
- **R5** (해소): override↔⑩ 충돌 → §3.4(scope.md 갱신).
- **R6** (잔존·작음): scope.md 채택 줄의 ⑩ 면제 토큰 규약을 architect/coordinator가 어겨 면제 미발화 가능 → 검증 7.2-c로 포착. 규약을 §4에 명시.

---

## 부록 §A — v1·v1.5·v2 적대 리뷰 요지
`workspace/flow/flow-review.md` "부록 — L1 NO-GO"(v1) + 본 §3.3. v1=스크립트 4결함, v1.5=X의 도구·역할·미러 붕괴, v2=override(Z) 경로 공백·⑩ 충돌·Y 앵커 회색지대.
