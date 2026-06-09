# dddjango 파이프라인 흐름 개선 — 4개 점검 항목 조사 (적대 리뷰 입력본)

> 조사일 2026-06-09. 근거: `dddjango/commands/dddjango.md`(코디네이터 오케스트레이션), 에이전트 7종(`acceptance-tester`·`design-architect`·`design-review-{ddd,api,db}`·`discipline-reviewer`·`coder`), 백스톱 16종 `dddjango/scripts/check-*.py`(읽기시점 정밀 매핑은 Explore 서브에이전트가 코드 근거로 수행). 이 문서는 *잠정* 발견이며, 적대 리뷰의 공격 대상이다.

## 0. 현재 오케스트레이션(검증된 사실)

- **Phase 0** 스코프(G0)
- **Phase 1** architect 초안 → 활성 lens 리뷰 **병렬**(ddd/api/db) → (선택) discipline-reviewer 경량 → architect 반영·중재 → **G1**
- **Phase 2** pytest 러너 준비 → acceptance-tester(인수 Red) → 슬라이스 도출 → 슬라이스별 coder(+슬라이스 ≥3이면 discipline-reviewer 경량) → **discipline-reviewer 홀리스틱 1회** → **백스톱 16종 일괄 실행(G2 배너 직전)** → **G2**
- **Phase 3** 마무리·검증 보고

백스톱은 현재 **전부 한 지점**(discipline 감수 *후*, G2 *전*)에서 일괄 실행되고, 하나라도 exit 2면 "게이트 거부와 동일하게 한 번에 설계로 반송"(coder/architect 피드백)으로 돌린다.

## 0.1 ⭐ 핵심 재구성 — 두 축은 다르다

사용자의 "설계군/구현군" 분류는 **반송 경로 축**(고장을 누가 고치나: architect=설계 결정 / coder=구현 수정)이다. 그런데 "구현 전 실행 가능한가"는 **읽는 대상 축**(스크립트가 *무엇*을 스캔하나: 구현 코드 / 디렉터리 골격 / 설정·스코프)이다. **두 축은 독립**이다 — architect로 반송되는 백스톱이라도 *탐지*에는 구현 코드가 필요할 수 있다.

읽기시점 3분류(Explore 코드 근거):

| 분류 | 백스톱 | 구현 전 실행? |
|---|---|---|
| **[구조-only]** 빈 패키지(`__init__.py`)만으로 탐지 | ④layer-skeleton | 골격 존재 시 가능 |
| **[구조축·산출물 필요]** *(적대리뷰 정정)* 디렉터리를 보되 *작동 산출물* 필요 | ⑦app-container(models.py·migration 내용) ⑨common-container(`.py` 존재) | ❌ 빈 골격 불가 |
| **[구현-필수]** 실제 로직(AST/본문)이 있어야 탐지 | ①mechanism ②error-central ③schema-bypass ⑤openapi-error ⑥context-isolation ⑩(코드부) ⑪anemic-sql ⑫public-surface ⑭transient-over ⑮synthetic-infra ⑯catch-all | 불가(코드 없음) |
| **[설정/스코프]** settings·pytest설정·scope.md | ⑧ninja-middleware ⑬test-config ⑩(scope부) | 해당 산출물 있으면 가능 |

**반송경로(설계군)와 읽기시점을 교차**하면:

| 설계군(→architect) | 읽기시점 | 구현 전 실행 |
|---|---|---|
| ④layer-skeleton | 구조-only | ✅(빈 골격 가능) |
| ⑦app-container | 구조축·*산출물 필요*(정정) | ❌(models.py·migration 있어야) |
| ⑨common-container | 구조축·*산출물 필요*(정정) | ❌(`.py` 내용 있어야) |
| ①mechanism | 구현-필수 | ❌ |
| ②error-central | 구현-필수 | ❌ |
| ⑥context-isolation | 구현-필수 | ❌ |
| ⑩idempotency | 구현+scope | ❌ |
| ⑪anemic-sql | 구현-필수 | ❌ |

→ **적대리뷰 코드검증 정정**: 설계군 8개 중 *빈 골격으로 실행 가능한 건 ④ 1개뿐*이고(⑦⑨도 작동 앱 산출물 필요), 나머지 7개는 코드/산출물이 있어야 탐지된다. 이 정정은 결론(조기 실행 거의 불가)을 *강화*한다.

추가 제약: **"최종 계획이 나온 시점"(G1 직후)엔 `design-spec.md`(마크다운)만 존재하고 코드·골격·settings 변경이 전무**하다(architect는 "코드를 쓰지 않는다", 골격은 coder가 Phase 2에서 materialize). 즉 구조-only 3개조차 *그 시점엔 스캔할 대상이 없다*.

## Q1. acceptance-tester가 implementation-test·architecture-api·architecture-ddd·discipline-tdd를 쓰는 게 맞나

**사실**: frontmatter `skills: [implementation-test, architecture-api, architecture-ddd, discipline-tdd]`. 역할=승인 명세의 *외부 관찰 가능 행위·계약*을 실패하는 인수 테스트(블랙박스)로 작성. 본문 근거: "implementation-test 계약 테스트 패턴(Ninja TestClient), discipline-tdd 바깥 루프(Outside-In), architecture-api·architecture-ddd의 계약·행위 정의."

**발견**:
- **implementation-test** ✅ 정당 — 테스트 코드를 *어떻게* 쓰나(pytest 관용구·TestClient·factory). 직접 필요.
- **discipline-tdd** ✅ 정당 — 바깥 루프 Outside-In·좋은 인수 테스트 4특성. 직접 필요.
- **architecture-api** ✅ 정당(api lens 활성 시) — 컨트롤러 URL 합성(`@api_controller`+`@route.*`)·올바른 TestClient 선택·operationId 규칙 인지가 계약 단언에 직접 쓰임.
- **architecture-ddd** ❓ **가장 약한 고리** — 블랙박스 계약 테스터에게 애그리거트 경계·불변식·도메인 이벤트(ddd 내부 구조 지식)가 정말 필요한가. 명세의 "외부 관찰 가능 행위 목록"이 *이미* architect(ddd 보유)가 도메인 규칙을 관찰 행위로 번역한 결과물이라, 테스터는 그 목록을 근거로 쓰면 된다. 방어 논거(유비쿼터스 언어 일관·무엇이 의미있는 행위 경계인가)는 있으나 약하다.

**잠정 권고**: 3종 유지. architecture-ddd는 **유보적 재검토** — 블랙박스 독립성과 "행위 목록=명세 소유" 원칙상 명세가 단일 근거이면 ddd 스킬 로드는 잉여일 수 있다. 단 "도메인 어휘로 테스트를 명명·범위화" 효용이 실재하면 유지. **N=0 라이브 근거** — 제거가 인수 테스트 품질을 떨어뜨리는지 미검증.

## Q2. 설계군 백스톱을 구현 전(최종 계획 시점) 실행하면 효율적인가

**발견(§0.1이 직접 답함)**:
- 제안의 전제("설계군=구현 전 검사 가능")는 **반송경로 축과 읽기시점 축의 혼동**이다. 설계군 8개 중 **①②⑥⑩⑪ 5개는 구현 코드가 있어야만 탐지**되어 구현 전 실행이 *원리상 불가*다.
- 구조-only 3개(④⑦⑨)만 골격 기반 탐지가 가능한데, **G1 직후엔 골격조차 없다**(coder가 만든다). 따라서 "최종 계획 시점"엔 16개 전부 스캔 대상이 없다.
- **효율 실측 관점**: 백스톱 실행 자체는 결정적 스크립트라 거의 즉시·저비용이다. 비용은 *실패 시 재-실행 루프*(coder/architect 재호출)다. "더 일찍 실행"의 이득은 *탐지 시점을 앞당겨 헛구현을 절약*할 때만 발생 → 구조-only(④⑦⑨)에서만 성립(골격이 틀리면 본문 작성 전에 잡음).

**잠정 권고(MODIFY)**: 문자 그대로의 "구현 전 실행"은 폐기. **달성 가능한 축소판** = Phase 2에 **골격-우선 단계** 신설: coder가 빈 4계층 골격을 먼저 깔면 → ④⑦⑨만 즉시 실행(fast-fail) → 통과 후 본문 작성. 이는 문서화된 catalog-container 회귀(DR-26/50)류 구조 위반을 본문 작성 전에 잡는 실효가 있다. 단 "구현 단계 *전*"이 아니라 "구현 *초입*(골격 후·본문 전)"이다. **설계 시점 구조 검증의 더 정석 레버는 Q4**(명세 자체를 houserules로 리뷰).

## Q3. 구현군 백스톱을 규율 감수 후 실행 + 실패 시 자동 재구현 (토끼굴 위험)

**사실**: "규율 감수 후 실행"은 **이미 현행**이다(백스톱은 discipline-reviewer *후*, G2 전). 새 제안은 "실패 시 *자동으로* 구현을 다시"(무인 자동 루프)다.

**발견 — 토끼굴 위험(적대리뷰 인용 정정)**:
- **33분 토끼굴**(DR-06)은 실측이나 원인은 *백스톱 자동 루프가 아니다* — 백스톱 *부재* 시절 coder가 커스텀 락 백엔드를 자작한 것이고, 백스톱·메커니즘 가드레일은 그 *해결책*이다. 현행 `coder.md:50`은 막히면 "멈춰 설계로 반송"(stop-and-report).
- 1h12m+ 런은 **"회귀 *의심*"이지 실측이 아니다** — 메모리가 교락 4개(태스크 상이·catalog 풀이주·N=1·미종료)를 *인정*한다(조사 초안이 "실측"으로 격상한 것은 과장).
- 즉 위험은 *제안된* 무인 자동 루프(현재 없음)에 대한 것이고, 현행은 이미 1-shot 반송·stop-and-report라 진동·무한루프를 구조적으로 막는다.

위험 3종:
1. **진동**: 백스톱 A 수정이 B를 유발, B 수정이 A 재유발(NJ-2↔415 이력처럼 백스톱 간 긴장 존재).
2. **우회 수정**: coder가 한 슬라이스·한 환경만 보고 근본수정 대신 체크 회피로 "수정"(메커니즘-대체 토끼굴의 정체).
3. **오-라우팅**: exit 2의 절반이 **architect로 반송**(설계 결정)인데 "자동 *구현* 재시도"는 그들에겐 틀린 처방 — 명세가 구조를 잘못 박았으면 coder를 아무리 돌려도 안 고쳐진다.

**잠정 권고(조건부)**: "구현군(coder 반송)에 한정"하면 라우팅은 옳다(③⑤⑧⑫⑬⑭⑮⑯). 자동화하려면 **반드시**: (a) coder-반송 그룹만 자동, architect-반송은 무조건 사용자에게 표면화, (b) 재시도 횟수 상한 + 초과 시 게이트로 에스컬레이션, (c) 같은 백스톱 2회 발화=진동 감지→정지. 무제한·무인 자동 루프는 문서화된 토끼굴 재현 위험.

## Q4. 3 독립 리뷰에 discipline-houserules가 참여하면 어떤가

**사실**: 현재 3 리뷰어는 각 architecture-* 1개만 로드(ddd→ddd, api→api, db→db). **design-architect는 *이미* discipline-houserules를 로드**(frontmatter)하여 명세의 구조·계층·명명 결정을 *작성*할 때 적용. **Phase 2 discipline-reviewer**도 houserules를 로드해 *코드*와 §0 불변식을 대조. 백스톱 ④⑦⑨⑫는 houserules 뿌리.

**발견 — 설계 시점 houserules *독립* 검증 공백**:
- 명세의 구조·계층·명명 결정(§0/§1/§4)은 architect(작성자)가 박지만, **그것을 설계 시점에 독립적으로 검증하는 리뷰어가 없다**. 3 리뷰어는 ddd/api/db만 본다.
- houserules 위반(앱 오배치·계층 골격 누락·common 오배치·명명)은 **Phase 2 discipline-reviewer(코드 작성 후)나 백스톱(코드 후)에 가서야** 잡힌다.
- 이게 **문서화된 catalog-container 회귀(DR-26/50)의 구조**다 — 구조 결정이 설계 시점에 안 잡히고 구현 후 백스톱 ⑦에 잡힘.
- "독립성이 architect 블라인드스팟을 잡는다"는 *3 리뷰어를 정당화하는 바로 그 논리*가 houserules 차원에도 적용된다(architect가 houserules를 보유해도 *작성자*다).

**잠정 권고(적대리뷰 후: GO 유력 → 보류)**: "공백의 *존재*"(3 리뷰어는 ddd/api/db만·architect는 작성자)는 구조적 사실로 견고하나, 4 렌즈가 효과·정당성을 강등시킴 — (i) **DR-50 반례**: 코드를 본 discipline-reviewer도 catalog 잔재를 백스톱 ⑦ G3 면제 구멍으로 놓쳤다 → *명세만 보는* 새 리뷰어가 더 잘 잡을 근거 없음; (ii) **DR-26 인과 반증**: catalog 회귀 근본은 "설계 시점 리뷰 부재"가 아니라 architect 코인플립·산문 탈출구; (iii) 결정적 백스톱 ④⑦⑨가 구조 회귀를 *결정적으로* 잡는데 LLM 리뷰어를 얹으면 안전망을 비결정으로 희석(DO-NOT-RETRY #10/#11/#14 = LLM 리뷰어 강등·합리화 3회 박제); (iv) N=0·dual 미러·동결 RUBRIC 부담. **정 한다면**: 새 에이전트 금지 — *이미 houserules 보유·이미 양 런타임 존재*하는 Phase 1 step 3 (선택) discipline-reviewer 경량 점검을 "선택→구조-결정 검토 상시"로 *승격*(dual 미러 비용 0)하고, "4번째 lens"가 아니라 별도 discipline 검토로 분류(lens=concern 불변식 보존).

## 교차 주제 — Q2와 Q4는 수렴한다

둘 다 "구조·계층을 설계 시점에 검증"을 노린다. Q2(코드 백스톱 조기실행)는 *코드가 없어* 대체로 불가. **Q4(명세를 houserules로 독립 리뷰)가 설계 시점 구조 검증의 올바른 메커니즘**이다. 달성안: ① Q4로 명세의 구조 *결정*을 조기 검증 + ② (선택) Phase 2 골격-우선 단계에서 구조-only 백스톱 ④⑦⑨를 골격에 돌려 결정적 백스톱으로 보강.

## 검증 안 된 것 / 한계

- **N=1·N=0 라이브**: 4건 모두 라이브 dual 런으로 효과·부작용 미측정. Q1 ddd 제거 영향·Q4 리뷰어 추가의 재현성/비용 영향 미관측.
- **dual 미러 부담**: 어떤 변경이든 Claude(`dddjango/`)·Codex(`codex-dddjango/skills/`) 양쪽 + 동결된 RUBRIC·EVAL-METHOD까지 동기 필요.
- **결정성 vs LLM 호출 수**: Q4는 LLM 리뷰어를 1개 늘림 → 비결정 표면이 증가하는지 vs 구조 회귀를 줄여 재현성이 오르는지 trade-off 미검증.
- 이 문서의 분류·권고는 *읽기시점 매핑(Explore)*과 *현행 파일*에 근거한다.

## 적대 리뷰 종합 (4 렌즈: skill-creator·plugin-creator·도메인 스켑틱·결정성/회귀/비용)

**우선순위(할 가치 큼 → 만지지 마라)**:
1. **Q2 골격-우선** — 유일하게 결정성을 *높이는*(결정적 스크립트 조기화·LLM 추가 0) 소폭 순이득. 단 빈 골격 실행 가능은 ④뿐이라 이득 작음 → 새 Phase 아닌 **Phase 2 내부 fast-fail 1줄**로 최소화. Q4를 채택하면 한계효용 급감(중복).
2. **Q4 houserules 설계 검증** — *보류*. 공백은 실재하나 효과가 DR-50으로 반증·과설계·비결정 추가. 정 하면 새 에이전트 대신 기존 discipline-reviewer 승격.
3. **Q1 ddd 제거** — *보류/재서술*. 제거 금지(N=0 회귀 위험·이득 노이즈). 본문 문구를 "ddd=유비쿼터스 *언어 사전*"으로 좁혀 블랙박스 single-responsibility와 화해하는 MODIFY만 검토.
4. **Q3 자동 재구현** — **NO-GO**. 문서화된 토끼굴의 직접 재현 위험 + hook 없는 LLM 자기집행 루프라 상한·진동감지를 결정적으로 집행 불가. 현행 1-shot 반송이 더 안전. (정 자동화하려면 루프 제어를 결정적 wrapper 스크립트로 빼야.)

**가장 중요한 미발견(도메인 스켑틱)**: 조사가 "설계 시점 구조 검증"의 진짜 구멍을 *엉뚱한 곳(4번째 리뷰어 부재)*에 짚었다. DEVLOG·코드가 가리키는 실제 구멍은 **생산시점 백스톱 ⑦ check-app-container의 G3 면제 로직(`_has_migrated_counterpart`)이 모델-이주 후 옛 루트 잔재를 놓치는 것**(DR-50 후속 ①·미커밋 DR-51 ⑰ check-duplicate-app과 동일 전선). Q4에 쏟을 노력은 그 *결정적 백스톱 보강*으로 돌리는 게 정석이다.

**합의된 정정(본문 반영 완료)**: §0.1·Q2 분류표 ⑦⑨ 사실 오류(구조-only 아님), Q3 1h12m "실측"→"의심"·33분 인과 오귀속, Q4 "GO 유력"→"보류".
