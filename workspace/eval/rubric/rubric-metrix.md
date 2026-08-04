# dddjango v4 frozen baseline 채점 결과지 템플릿 (rubric-metrix)

> **상태**: `active` · **FROZEN** · **SCORING ENABLED**.
> 사용자 명시 승인(`2026-08-04T11:59:05+0900`) 이후 새 v4 결과에 이 템플릿을 사용한다.
> historical v3 결과에는 소급 적용하지 않는다.
> **동결 epoch/profile/version**: `2026-08-03-code-json` / `dddjango-code-json` /
> `v4-candidate`.
> **결과 identity**: `epoch + error profile + rubric version + dimension ID`.
> **v3 locator**: full SHA `d1fce5b43b13f8447b2a4b78f6c94e74efe8ff19`.
> working tree의 historical v3 결과 14개는 byte 불변이며 소급 판정·재작성하지 않는다.

## 사용 조건

- 이 파일은 동결된 v4 보고 형식이다. 기준 변경에는 명시적 unfreeze 또는 새 epoch 승인이 필요하다.
- 승인 이후 새 v4 평가에서 `EVAL-METHOD.md` 절차를 따라 한 runtime당 결과 파일 하나를 만든다.
- 결정·의미·종합은 `✅ PASS · ❌ FAIL · 🟡 WEAK · ⏸️ 보류 · ➖ N/A`로 기록한다.
- Result에는 조정자가 직접 확인한 `file:line` 근거를 쓴다. 결정 PASS여도 의미 판정을 생략하지 않는다.
- 치명 후보 마스크는 **SD-1~7 · FC-1~3 · SH-1·2·3·4·7 · (HTTP operation이 있을 때) NJ-1·2 · Q-4**다.

## 1. 헤더 블록

> **상태**: active · FROZEN · SCORING ENABLED
> **epoch**: 2026-08-03-code-json
> **error profile**: dddjango-code-json
> **rubric version**: v4-candidate
> **dimension set**: SD-1..7 + SH-1..10 + NJ-1..7 + FC-1..3 + Q-1..7
> **identity rule**: epoch + error profile + rubric version + dimension ID
> **채점일**:
> **픽스처(절대경로·기존규약 상태)**:
> **런타임 / N_grader**:
> **태스크 요지 / 고정 게이트 답**:
> **fixture 도구 환경(env / produced / used)**:
> **단서**: 동결 이후 신규 v4 결과 전용 · 조정자 직접 검증 · 해당 시 리허설/FC 미실행

## 2. 종합 판정 (사전식 집계)

| 단계 | 결과 |
|---|---|
| ① C 마스크(MQ0/MQ1/MQ2) |  |
| ② 치명 후보 게이트 FAIL 수 |  |
| ②.5 실질성 관문 |  |
| ③ 비치명·의미적 변종 |  |
| ④ TIER-Q 등급 |  |

> **한 줄 요지**:
> **2차원 라벨**: 정적(준수/WEAK/FAIL) × 라이브(발화/미발화/미검증)

## A. TIER-S 척추 — DDD 도메인 충실도 (S-DDD)

| ID | 항목 | §근거 | Result | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|---|
| **SD-1** | 빈혈: 판정 소유 | 핵심 규칙·불변식이 도메인 행위로 존재 |  |  |  |  | 치명 |
| **SD-2** | 빈혈: 프로덕션 호출 | 응용이 조회→도메인 행위→저장으로 실제 호출 |  |  |  |  | 치명 |
| **SD-3** | 빈혈: 무복제 | 비즈 판정이 SQL/ORM 조건으로 복제되지 않음 |  |  |  |  | 치명 |
| **SD-4** | 애그리거트 경계 | 일관성 경계·참조·트랜잭션 범위 적정 |  |  |  |  | 치명 |
| **SD-5** | 모델 표현력 | 값 객체·도메인 서비스·식별자 의미 적정 |  |  |  |  | 치명 |
| **SD-6** | 계층 HTTP 무지 + controller 소유 | domain/application은 HTTP·Ninja를 모르고, 알려진 자기 BC 예외→status는 소유 controller가 직접 선택. application `status` DTO 우회도 Goodhart FAIL; 중앙 handler는 PASS 아님 |  |  |  |  | 치명 |
| **SD-7** | 컨텍스트 통신 | 타 BC는 OHS/ACL 포트로만 소비 |  |  |  |  | 치명 |

## B. TIER-S 척추 — houserules 충실도 (S-HR)

| ID | 항목 | §근거 | Result | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|---|
| **SH-1** | 컨테이너 | 신규/touched 앱이 `application/<app>/` 아래 |  |  |  |  | 치명 |
| **SH-2** | 4계층 | domain/application/infra/presentation 물리 분리 |  |  |  |  | 치명 |
| **SH-3** | 종류 폴더+골격 | 종류 2차 폴더와 필요한 애그리거트 골격 실현 |  |  |  |  | 치명 |
| **SH-4** | Django 앱 위치 | ORM/migration이 `infra_layer/django_<app>/`에 위치 |  |  |  |  | 치명 |
| **SH-5** | ORM 명명 | ORM `<Name>Model`, 도메인 bare 이름 |  |  |  |  | — |
| **SH-6** | 포트/구현 명명 | 역할 접미사·기술 접두 규약 준수 |  |  |  |  | — |
| **SH-7** | 협력 포트 위치 | 협력 포트가 domain aggregate의 `port/`에 위치 |  |  |  |  | 치명 |
| **SH-8** | ACL 분리 | ACL이 infra `acl/`에 있고 repository와 분리 |  |  |  |  | — |
| **SH-9** | 단일 레이아웃 | 한 앱에 상충 레이아웃이 공존하지 않음 |  |  |  |  | — |
| **SH-10** | 테스트 의미군 | unit/integration/e2e 의미군 분리 |  |  |  |  | — |

## TIER-S(조건부) — django-ninja 충실도 (S-NINJA)

> HTTP/JSON operation이 없으면 NJ-1~7 전체를 N/A로 기록한다.

| ID | 항목 | §근거 | Result | 결정 | 의미 | 종합 | 치명(조건부) |
|---|---|---|---|---|---|---|---|
| **NJ-1** | 스택 채택 | 신규 JSON API는 Ninja/Ninja Extra, plain view·DRF 누수 없음 |  |  |  |  | 치명 |
| **NJ-2** | operation 얇음(비오류) | 비즈 규칙·ORM·수동 parsing 없이 응용 호출과 schema 매핑 |  |  |  |  | 치명 |
| **NJ-3** | Schema 입출력 분리 | 요청/응답 Schema 분리, domain 직접 직렬화 없음 |  |  |  |  | — (강) |
| **NJ-4** | BC 오류 OpenAPI 선언 | controller가 직접 반환하는 BC status를 같은 BC base ErrorOut으로 선언; 직접 BC 반환이 없는 framework 401/403/route 404/422/429/500은 BC ErrorOut으로 광고하지 않음. status별 식별자 subset 과다노출은 승인된 단순화 |  |  |  |  | — (강) |
| **NJ-5** | operation 문서화 | summary/tags와 정보 있는 반환 타입 |  |  |  |  | — (경미) |
| **NJ-6** | Ninja 버전 핀 | 신규 도입 시 버전 핀과 기존 관례 일치 |  |  |  |  | — (경미) |
| **NJ-7** | BC 오류 직접 계약 | application 호출 한 문장만 감싼 좁은 try, 구체 catch, no-arg concrete ErrorOut 또는 BC base 직접 생성, controller의 직접 Status 반환, framework 기본 처리. helper/handler/catch-all·broad catch·raw 오류 응답은 FAIL |  |  |  |  | — (강) |

## TIER-S(핵심) — 기능 정확성 (FC)

| ID | 항목 | Result | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|
| **FC-1** | 코드 열람 전 골든 행위표의 status·부작용 전수 확인 |  |  |  |  | 치명 |
| **FC-2** | M1 차감 부호·M2 판정 경계·M3 controller HTTP status 표현 mutation이 red. slot 6이 body status property를 승인한 fixture만 해당 field mutation과 HTTP/body 일치도 red인지 확인 |  |  |  |  | 치명 |
| **FC-3** | 음수 재고·차감 역전·인과 역전 같은 명백한 도메인 오류 부재 |  |  |  |  | 치명 |

## C. 기존규약 마스크 (필수 적용 메모)

| 질문 | Y/N | 근거 |
|---|---|---|
| **MQ0** 기존 앱이 이번 런에서 삭제·대체됐는가? |  |  |
| **MQ1** 기존/대체 앱의 런 변경 집합에 핵심 규칙 분기·불변식 메서드가 있는가? |  |  |
| **MQ2** 그 코드가 판정 없는 단순 상류 데이터 소스인가? |  |  |

> **마스크 결론**: greenfield라도 이 섹션을 생략하지 않고 `N/A — 신규 앱뿐`으로 남긴다.

## D. TIER-Q 품질

| ID | 항목 | §근거 | Result | 결정 | 의미 | 종합 |
|---|---|---|---|---|---|---|
| **Q-1** | 스코프/과설계·G1 | 요청 외 발명과 고-blast 결정의 승인 여부 |  |  |  |  |
| **Q-2** | 선택 error profile 계약 일관성 | 선택한 profile의 승인 exact wire shape·HTTP status·필요 header·version 정책이 일관함; body status property는 승인된 scope만 비교 |  |  |  |  |
| **Q-3** | Risky Write 형식+테스트 실현 | 동시성 기준과 실제 테스트 일치 |  |  |  |  |
| **Q-4** | 메커니즘 소유권 [치명] | 승인 없는 DB backend/PRAGMA/monkeypatch 없음 |  |  |  |  |
| **Q-5** | 마이그레이션 안전 | 0001·table/label·expand/backfill 안전 |  |  |  |  |
| **Q-6** | 테스트/TDD | green bar·인수 행위·수집·도구 사용 근거 |  |  |  |  |
| **Q-7** | 경미 품질 | 공개 표면 annotation·주석·의존성 핀 등 |  |  |  |  |

## 의미적 변종 / backstop-blind 메타

| ID | 결정 근거 | 의미 근거 | 종합 영향 |
|---|---|---|---|
|  |  |  |  |

## TIER-OBS — 에러 경로 라이브 관측 (EP, 비채점)

> EP는 34개 채점 차원 밖의 관측이다. 동결 이후 새 v4 라이브 결과에서 실행·기록하며 종합 라벨을 자동 변경하지 않는다.

| 키 | probe | 기대 계약 | 관측 | 판정 |
|---|---|---|---|---|
| **EP-1** | 비-JSON/절단 body | framework 기본 400; BC shape/code 아님; exact body snapshot 금지 |  |  |
| **EP-2** | request validation 실패 | framework 기본 422; BC shape/code 아님; exact body snapshot 금지 |  |  |
| **EP-3** | (a) raw infra/미식별, (b) G1 승인된 공개 retryable | (a) 기본 500, (b) 자기 BC 예외→소유 controller 503 또는 계약상 409 + 승인 code/header; raw catch-all 없음 |  |  |
| **EP-4** | 재고 부족 | 409 + slot-6 승인 BC exact application/json body; body status property가 승인된 fixture만 HTTP와 일치 |  |  |

## 조정자 노트


## 부록 (선택)
