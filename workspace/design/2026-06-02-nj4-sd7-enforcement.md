# NJ-4·SD-7 집행 보강 처방 (결정적 백스톱 + 생산자 예방 + 리뷰어)

> **상태**: **v2 (2026-06-02) — 서브에이전트 4리뷰 + 조정자 실측 검증 반영.** v1의 "SD-7 백스톱 반려" 결론은 **검증으로 뒤집힘**(아래 §3). 표준/스크립트 실제 수정은 이 v2 기준 별도 승인.
> **범위**: 평가에서 확정된 두 문제(① Codex NJ-4, ③ Claude SD-7)의 **집행(enforcement)** 보강. 표준 *내용*은 대체로 옳고 비어 있는 건 *집행 레그*다.
> **이미 집행됨**: ③의 뿌리인 **RUBRIC SD-7 미스캘리브를 교정**(바·§E 앵커·`tools/check-structure.py` ACL 면제) — 아래 §3.4.

---

## 0. 검증된 두 문제 (file:line 증거)

| 문제 | 픽스처 | 증거 | 루브릭 | 치명 |
|---|---|---|---|---|
| **① NJ-4** status별 response 선언 | `poc-codex` | `api_orders.py:209` `response={201: CreateOrderOut}`(성공만) + `:211-258` `openapi_extra`에 400/404/406/409/415/422 | NJ-4(§2.2 line111) | 비치명('강') |
| **③ SD-7** 컨텍스트 통신 | `p1a-v3-claude` | **ACL 밖** 누수: `order_api_router.py:26`(presentation)·`create_order_app.py:17`(application)이 catalog 도메인 **예외** 직접 import (예외 번역이 ACL에 안 갇힘) | SD-7(ddd §3.2(3)·§2.5) | **치명** |

> **③ 근거 정정(v2)**: v1은 ③을 "ACL이 catalog 구체 infra import(`product_stock_acl.py:17`)"로 봤으나 **그건 표준 §2 허용(거짓양성)**. 검증 결과 진짜 위반은 **ACL 밖**(presentation·application)으로 catalog 예외가 새어 결합한 것. `smoke4-claude`는 같은 catalog 결합을 ACL에 격리해 **SD-7 PASS** — 둘을 가르는 축이 "ACL 격리 여부"다.

---

## 1. 현재 집행 갭 (3중 AND-집행 중 어디가 비었나)

dddjango 품질 = **[결정적 백스톱(레그1) ∧ 생산자 예방: architect·표준(레그2) ∧ 독립 의미 감사: reviewer(레그3)]**.

| 문제 | 레그1 백스톱 | 레그2 생산자/표준 | 레그3 리뷰어 |
|---|---|---|---|
| **① NJ-4** | ❌ **없음** — `check-response-schema-bypass.py:13`이 명시적으로 "NJ-4 몫"이라며 안 봄 | 🟡 부분 — 표준은 "모든 status를 `response={}`에"(ninja final.md:111·SKILL:22) 명확하나 **"openapi_extra 수동 선언은 불충족"을 콕 집지 않음** → Codex가 "선언했다"로 빠져나감 | ❌ **없음** — discipline-reviewer 레드플래그(:39-40)에 NJ-4 항목 없음 |
| **③ SD-7** | ❌ **없음** — `check-layer-skeleton.py`는 4계층 폴더 존재만 봄, cross-context import 안 봄 | 🟡 부분 — houserules §2·architect:38이 OHS/ACL을 말하나 **"예외 번역도 ACL에 격리"를 코더가 흘림**(p1a-v3) | ✅ 있음 — discipline-reviewer:40에 "다른 컨텍스트 domain/infra 직접 import" 레드플래그. **단 의미 레인이 라이브 발화 못 함**(DR-21) |

→ **두 문제 다 레그1(결정적 백스톱)이 공백**. 결정적 스크립트는 모델과 무관하게 발화하므로(P1b·P2·P3가 양 런타임 수렴한 이유) 이 공백을 메우는 게 처방의 핵심.

---

## 2. 처방 — ① NJ-4

### 2.1 [레그1] 신규 결정적 백스톱 `check-openapi-error-declaration.py`
`check-response-schema-bypass.py`의 형제. 고정밀·저-recall, AND 합성(거짓양성 ≈0 — 실측 확인).

**AND 조건(전부 참이어야 blocker):**
1. `presentation_layer/` 프로덕션 `.py`(test 제외) + ninja import.
2. operation 데코레이터 `openapi_extra={...}`의 `responses` 키에 **4xx/5xx status**가 리터럴로 선언.
3. **동시에** 같은 operation의 `response={...}`엔 그 4xx/5xx **부재**(2xx만).
4. (git) 신규/수정.

→ blocker: "오류 status를 `openapi_extra`로 선언하고 `response={}`엔 누락 = NJ-4 위반. ninja가 타입으로 미인지(OpenAPI 문서 가시성만)."

**거짓양성 회피 (실측 0)**: `openapi_extra`가 security/examples 전용(responses 키 없음)·responses에 2xx만·이미 response=에 이중선언이면 제외. → `p1a-v3-codex`·정상 픽스처 exit 0 확인.

**저-recall 한계(정직 표기 — 적대 리뷰 실측)**: AST가 리터럴만 보므로 **(a) `responses` dict를 변수로 호이스트**(`{**EXTRA}`/`responses=_ERRORS`), **(b) `get_openapi_schema` 오버라이드로 사후 주입**하면 같은 결함이 통과한다(Goodhart). (a)는 저-recall 수용. (b)는 **별도 신호 추가 검토** — presentation에 `def get_openapi_schema` 오버라이드 + 4xx `response=` 부재. "정조준"이 아니라 "흔한 형태 차단 + 변종은 레그3"으로 정직 표기.

### 2.2 [레그2] 생산자 예방 — ninja 표준 보강 (skill-creator 리뷰 반영 문구)
`implementation-django-ninja` final.md:111 다음 신규 불릿(:111 선언규칙과 :112 생성규칙 사이):
> "`openapi_extra`·`get_openapi_schema`로 status를 수동 선언하는 것은 이 요구를 충족하지 않는다 — 그렇게 하면 Swagger 문서엔 드러나지만 ninja는 그 status를 응답 타입으로 인지하지 못해 검증·직렬화 계약 밖이다. 오류 status는 `response={...}`에 넣는다(문서 가시성과 타입 인지는 다른 것)."

SKILL.md:22는 새 불릿 대신 기존 문장에 괄호 절: "…`response={...}`에 schema로 선언하되(`openapi_extra` 수동 선언은 ninja 미인지라 불충족), …" (progressive disclosure 유지).

### 2.3 [레그3] 리뷰어 — **discipline-reviewer**(design-review-api 아님 — v2 정정)
최적성 리뷰가 적발: `design-review-api`는 **명세만 보고 코드를 안 본다**(`:13` "구현 코드를 보지 않는다"). NJ-4는 *생성 코드*(operation 데코레이터)에서만 드러나 design-review-api로는 **원리상 못 잡는다(죽은 규칙)**. → **discipline-reviewer:39**("API 오류 응답 중앙화" 인접·코드 열람)에 1구절. 단 NJ-4는 구문적이라 §2.1 백스톱이 결정적으로 잡으면 레그3 한계효용 낮음 — **선택(2레그로 충분)**.

---

## 3. 처방 — ③ SD-7 (백스톱 **부활** — v1 반려 뒤집힘)

### 3.0 검증 반전 (왜 부활하나)
적대 리뷰는 프로토타입을 `smoke4-claude`에 돌려 거짓양성(exit 2)을 보고 **백스톱 반려**를 권고했다. 그러나 조정자 실측(`check-structure.py` ACL 면제판):
- `smoke4-claude` → **PASS-신호**(ACL 밖 catalog import 0; 결합이 ACL에 격리).
- `p1a-v3-claude` → **FAIL-신호**(ACL 밖 `order_api_router.py:26`·`create_order_app.py:17` 예외 누수).

→ 적대 리뷰는 **ACL 파일만 보고** presentation·application 누수를 놓쳐 "구별 불가"라 단정했다. **ACL을 면제하면 거짓양성 0 ∧ 진짜 위반 포착** = 백스톱이 정확히 작동한다.

### 3.1 [레그1] 신규 결정적 백스톱 `check-context-isolation.py` (ACL 면제판)
**AND 조건:**
1. `application/<bc-A>/` 하위 프로덕션 `.py`(test 제외).
2. `from application.<bc-B>.(domain_layer|infra_layer)…` import (**bc-B ≠ bc-A**).
3. **그 파일이 `infra_layer/acl/` 가 아님** — ACL은 표준 §2(houserules final.md:128/141)가 업스트림 모델·예외 번역을 허용하므로 **면제**(주의신호로만 분리).
4. 표준 레이아웃(`application/` 존재) + (git) 신규/수정.

→ blocker: "ACL 밖(도메인/응용/presentation)에서 타 BC `domain_layer`/`infra_layer`(예외 포함) 직접 import = SD-7 위반. ACL이 번역해 격리하거나 OHS 경유하라."

**거짓양성 회피**: ACL 면제(3)가 핵심 — `smoke4`·`p1a-v3` ACL 자체는 면제. `application_layer` import는 보수적 불-차단(루브릭=domain/infra). OHS(`published_service`) import 허용. → eval `check-structure.py`로 **검증 완료**(smoke4 PASS·p1a-v3 FAIL·poc-codex/final PASS).

> 로직은 이미 `tools/check-structure.py:check_sd7`에 구현·검증됨(§3.4). 플러그인 백스톱은 이를 단독 스크립트로 포팅(기존 4종 docstring·git가드 패턴).

### 3.2 [레그2] 생산자 예방 — houserules + architect (in-place·최소)
- **houserules §2**: 기존 §2(final.md:131/141)에 **1구절만** — "ACL은 OHS(`published_service`)를 *호출*하는 번역기다. ACL이 업스트림 모델·**예외**를 번역해 격리하지 않고 도메인/응용/presentation으로 흘리면 cross-context 결합이 샌다." (소비측 규칙에 "예외 번역 격리" 보강 — 중복 아닌 보완.)
- **design-architect:38**: 기존 OHS/ACL 블록(390자) **안에** "ACL 설계 시 업스트림 예외의 번역·격리를 명세에 박는다(presentation·application이 타 BC 예외를 직접 잡지 않게)" 끼워넣기(새 문장 분산 금지 — 원칙06).

### 3.3 [레그3] 리뷰어 — discipline-reviewer:40 **in-place 수정**(중복 위험)
:40에 "다른 컨텍스트 domain/infra 직접 import" 레드플래그가 이미 존재. 새 불릿 추가는 중복 → **기존 문장 제자리 수정**: "…ACL 어댑터도 예외가 아니다 — ACL은 업스트림 OHS를 *호출*하는 번역기이지 업스트림 내부를 직접 import하는 곳이 아니며, **번역한 예외를 ACL에 격리**한다(presentation·application이 타 BC 예외 직접 import = 누수)."

### 3.4 [이미 집행] RUBRIC SD-7 미스캘리브 교정 (2026-06-02)
- `RUBRIC.md` SD-7 바: FAIL 정의를 "**ACL 밖** 직접 import / OHS 미경유 / ACL 번역누수"로, PASS에 "ACL 격리된 미이주 직접통합" 추가. 레인 결정→**결정+의미**.
- `RUBRIC.md` §E 앵커: FAIL 예시를 `p1a-v3 order_api_router.py:26`(진짜 누수)로 교체, `smoke4 product_stock_acl.py`는 PASS 예시로.
- `tools/check-structure.py:check_sd7`: ACL 경로를 FAIL-신호에서 분리해 "주의(표준§2 허용)"로 강등.
- SD-7 주의박스 신설(SD-6 주의 옆).

### 3.5 published_service 방향 — (B) 유지하되 "생산자 예방, 차단 아님"
(B)(소비되면 OHS 노출)는 권고로 유지하나 **SD-7 차단은 §3.1 백스톱이 한다**(최적성 리뷰: (B)는 생산자 예방이지 차단 수단 아님). (A) 빈-골격 강제는 기각(YAGNI). architect가 "소비되는 컨텍스트 OHS 노출"을 명세에 유도하되 강제 백스톱은 §3.1.

---

## 4. 배선 / 3미러 동기화 (플러그인 구조 리뷰 반영)

신규 백스톱 **2종(4종→6종)**. v1이 "4종→6종"이라 적고도 **실제 배선 텍스트를 안 고친** 갭을 정정:

| 산출물 | Claude | Codex |
|---|---|---|
| `check-openapi-error-declaration.py`·`check-context-isolation.py` (신규) | `scripts/` | `skills/dddjango/scripts/` (byte-identical) |
| **배선 텍스트 정정** | `commands/dddjango.md:80` "네 스크립트"→"여섯", ⑤⑥ 추가 | `skills/dddjango/SKILL.md:99` 동일 + "네이티브 셸"→"Bash(또는 sh 호환)" |
| ninja 표준 | `skills/implementation-django-ninja/{SKILL,final}` | 동 + `workspace/reference/implementation-django-ninja/...` |
| houserules §2 | `skills/discipline-houserules/{SKILL,final}` | 동 + `workspace/reference/discipline-houserules/reference/final` |
| architect/reviewer | `agents/{design-architect,discipline-reviewer}.md` | `skills/dddjango-{design-architect,discipline-reviewer}/` |

**확인 필요(리뷰 적발)**: Claude `.claude-plugin/plugin.json`이 `scripts/` 자동 포함을 보장하는지(Codex는 `"skills":"./skills/"` 명시 → 자동). 미보장이면 등록 추가. shebang `#!/usr/bin/env python3` 실행 환경 전제(Unix) 명시.

---

## 5. 리스크 / 미해결
- **NJ-4 Goodhart**: 변수 호이스트·`get_openapi_schema` 우회(저-recall). (b)는 신호 추가 검토(§2.1).
- **SD-7 application_layer 갭**: 표준 line131은 application_layer 직접 import도 금지하나 백스톱은 domain/infra만(루브릭 정합·거짓양성↓). presentation·application의 *예외* import는 domain_layer 경유라 포착됨(p1a-v3 실증).
- **공유 헬퍼 6중 복제**: `_is_new_or_modified` 등이 6스크립트 복제(원칙06 부채). **별건 리팩터링**(원칙08 — 기능과 분리), 이 처방 밖.
- **별건(범위 밖)**: poc-codex 루트 catalog 중복(SH-9), Codex C2~C5 의미 변종.

---

## 6. 검증 계획·결과
1. ✅ **SD-7 정적(완료)**: `check-structure.py` ACL면제판 → smoke4 PASS·p1a-v3 FAIL·poc-codex/final PASS(거짓양성 0).
2. **NJ-4 정적**: 플러그인 백스톱 포팅 후 poc-codex exit 2·p1a-v3-codex exit 0 재확인.
3. **라이브 발화**: fresh 위반-주입 런으로 두 백스톱 blocker 발화(정적 통과 ≠ 라이브 발화 — DR-21).

---

## 부록. 서브에이전트 4리뷰 + 검증 종합

| 리뷰어 | 핵심 발견 | 처방 반영 |
|---|---|---|
| **적대적 정합성** | 프로토타입 실측 → SD-7 백스톱 smoke4 거짓양성, NJ-4 거짓양성 0, NJ-4 회피구멍 2종 | NJ-4 출하·회피구멍 정직표기. **SD-7 "반려"는 조정자 검증으로 뒤집힘**(ACL 밖 누수 간과) |
| **최적성/단순성** | NJ-4 레그3 design-review-api 오라우팅(코드 안 봄), (B)=생산자예방≠차단, 헬퍼 6중복제 | 레그3→discipline-reviewer, (B) 약화, 헬퍼 별건 |
| **skill-creator 렌즈** | 텍스트 보강 양호(why·중복아님), §3.3 in-place 필요, docstring 동급 요건 | §2.2 문구·§3.3 in-place·docstring 요건 명문화 |
| **플러그인 구조** | "4종→6종" 배선 텍스트 미반영, plugin.json scripts/ 불명, 셸 용어 | §4 배선 정정·plugin.json 확인 |

**조정자 검증 반전(핵심)**: 적대 리뷰의 "SD-7 백스톱 반려"는 ACL 파일만 본 결론. 실측으로 ACL 면제 시 smoke4(PASS)·p1a-v3(FAIL) 정확 구별 → 백스톱 부활. ③의 진짜 근거도 "ACL infra import"(거짓양성)에서 "ACL 밖 예외 누수"로 정정.
