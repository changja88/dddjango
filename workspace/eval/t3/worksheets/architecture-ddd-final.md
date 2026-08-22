# T3 이관 저작 검수표 — architecture-ddd-final

> 대상: 발주서 `workspace/eval/t3/orders/architecture-ddd-final.md` REF 36절 전량(파일럿 기이관 2절 제외).
> 산출: `workspace/eval/t3/specs/architecture-ddd-final.spec.json` — 검증 전용 실행 **exit 0**(`--write` 미사용).

## 0. 공정 특기 — 파일럿 2절을 spec 에 재수록한 이유(도구 계약)

`ontology_migrate.py` 는 ① ISSUED 의 `rules/architecture-ddd-final.ttl` 기존 28행을 **명세 등장 순으로 재사용**하고(불일치 시 exit 1) ② `--write` 시 `rules/<doc_key>.ttl` 을 **통째 덮어쓴다**. 따라서 발주 36절만 담은 명세는 (ㄱ) 첫 규범부터 R-0098 재사용 정합 위반으로 반송되고 (ㄴ) 통과하더라도 파일럿 2절(s051-8·s017-3.2)을 정본 ttl 에서 삭제한다. 실증: 36절만 담은 프로브가 `R-0098 재사용 정합 위반 — 기존 정본(Obligation/의사결정 1 …) ≠ 명세(…)` 로 exit 1.

→ 명세 `sections` 선두에 파일럿 spec(`workspace/design/2026-08-19-ontology-t1-migrate/spec-architecture-ddd-final.json`)의 두 절을 **바이트 동일하게** 재수록했다(등장 순 = ISSUED 등재 순 = s051-8 8건 → s017-3.2 20건). 저작 판단은 발주 36절에만 가했고 파일럿 절은 한 글자도 바꾸지 않았다(«명세의 기존 절 부분은 불변 관례»).

## 1. census 대사

| section_key | 발주서 규범 수 | spec Work | Δ | 판정 |
|---|---:|---:|---:|---|
| s004-1.2 | 6 | 5 | -1 | **과대 산정이 센서스 쪽**. [의사결정 #6] blockquote 를 센서스가 규범 1로 셌으나 §8 표 6행의 축자 사본이라 §15 «정본 1곳만 Work 승격»에 따라 억제(restates→s051-8/b8). 파일럿이 [의사결정 #1]에 내린 판정과 동형. |
| s007-2.1 | 2 | 2 | 0 | 일치. 45행 Evans 인용(«코드 아래에 있는 모델을 리팩터링한다»)의 비승격 사유는 경계 메모 «인용=규칙의 적용 조건» 참조 — 명령형 인용 3건과 달리 서술형이라 P0 규약 ② 대상 아님(적대 리뷰 L-8 부분 반박). |
| s008-2.2 | 1 | 1 | 0 | 일치 |
| s009-2.3 | 4 | 4 | 0 | 일치 |
| s010-2.4 | 4 | 4 | 0 | 일치. 219행 «하위 도메인은 발견하고, 바운디드 컨텍스트는 설계한다»는 [B]의 강조점을 **서술**한 격언 인용(«~는 점을 가장 강조»)이라 비승격 — 같은 문장의 §9 사본(s052-9/b3)도 «규범 아님(서술)»으로 원장 재분류(적대 리뷰 L-10). |
| s011-2.5 | 17 | 16 | -1 | **과대 산정이 센서스 쪽**. b19 마지막 문장(발행 봉투 discriminator도 같은 원리)은 s026 birth-enum 정본의 재진술 — Work 억제·블록 restates 로 대체. |
| s012-2.6 | 1 | 1 | 0 | 일치 |
| s016-3.1 | 3 | 3 | 0 | 일치. 469행 정의문의 «불변(immutable)이어야 한다»는 b3 «반드시 불변»(473행)의 같은-절 중복이라 계수 밖 — 쌍 자체는 b2 에 `restates`→b3 으로 기록(적대 리뷰 L-7). |
| s019 | 17 | 16 | -1 | **과대 산정이 센서스 쪽**. [의사결정 #4] blockquote 억제(restates→s051-8/b6). 나머지 16(헤딩 4·규칙1 2·규칙2 인용 1·규칙3 ORM 확장 4·규칙4 5)은 센서스 내역과 일치. |
| s021-3.4 | 4 | 4 | 0 | 일치 |
| s022-3.5 | 6 | 6 | 0 | 일치 |
| s023-3.6 | 9 | 9 | 0 | 일치 |
| s024-3.7 | 3 | 2 | -1 | **과대 산정이 센서스 쪽**. [의사결정 #7] 억제(restates→s051-8/b9). 잔여 2 = 센서스 «수집→디스패치 2»와 일치. |
| s025 | 14 | 15 | +1 | **과소 산정이 센서스 쪽(+1)**. 센서스 내역이 «선택 조건 6 + 회피 3 + 소유 핸드오프 4 + outbox 적재 1»로 14인데, b5 선두 «Outbox 채택 시 명시할 항목» 자체가 명세 기재를 구속하는 지시문이라 «애매하면 포함»(T1 계수 규약) 준거로 1건 추가 승격. b2(1186행) «이 문서는 결정과 채택 여부만 소유한다»는 문면이 «(아래 handoff)»로 자기 구체화를 지목하는 예고문이라 비계수 — 같은 내용을 b5 의 핸드오프 4건이 소유자별로 구체화하고 그쪽만 Work 를 받는다(적대 리뷰 L-11 부분 반박). |
| s026 | 18 | 18 | 0 | 일치 |
| s029-4.1 | 1 | 1 | 0 | 일치 |
| s030-4.2 | 1 | 1 | 0 | 일치 |
| s031-4.3 | 1 | 1 | 0 | 일치 |
| s032-4.4 | 2 | 2 | 0 | 일치 |
| s033-4.5 | 1 | 1 | 0 | 일치 |
| s034-4.6 | 1 | 1 | 0 | 일치 |
| s035-5 | 1 | 0 | -1 | **과대 산정이 센서스 쪽**. 절 전체가 [의사결정 #5] blockquote 한 블록 — 전량 사본이라 절 Work 0(restates→s051-8/b7). 절이 그래프에 실리되 규범을 소유하지 않는 첫 사례. |
| s036-5.1 | 3 | 3 | 0 | 일치 |
| s037-5.2 | 2 | 2 | 0 | 일치 |
| s038-5.3 | 16 | 16 | 0 | 일치. 1495행 «[C]는 헥사고날을 주요 아키텍처 스타일로 권장한다»는 원전의 권고를 **서술**한 절이라 비계수 — 이 문서 자신의 채택 태도는 b3 선택 조건 4 + b4 회피 조건 3 이 구체화하고, 무조건 권고로 읽으면 회피 조건군과 모순한다(적대 리뷰 L-9 부분 반박). |
| s039-5.4 | 10 | 10 | 0 | **합계는 일치(10=10)하나 내역이 다름**: [의사결정 #2] 억제(−1) + b3 «질문하는 행동이 대답을 바꿔서는 안 된다»를 독립 규범으로 승격(+1). 후자는 CQRS 정의 문장이 아니라 명시적 금지문이라 포함. |
| s040-5.5 | 5 | 5 | 0 | 일치 |
| s042-6.1 | 11 | 10 | -1 | **과대 산정이 센서스 쪽**. [의사결정 #8] 억제(restates→s051-8/b10). 잔여 10 = tests 2 + 의존성 4 + 차선 허용 2 + 권위 이양 2. |
| s043-6.2 | 2 | 1 | -1 | **과대 산정이 센서스 쪽**(적대 리뷰 M-1 수용). b2 첫 문장 «ORM은 도메인 모델을 임포트해야 하며 도메인 모델이 ORM에 의존해서는 안 된다»(1676행)는 s021-3.4/b3 Cosmic Python 원문 인용(844행)과 같은 규칙·같은 출처·같은 배선(#8)의 same-doc 재진술 — §15 «정본 1곳만 Work 승격»에 따라 첫 등장·원문 인용 쪽을 정본으로 두고 여기는 Work 억제·`restates`→s021-3.4/b3. 잔여 1 = implementation-django 핸드오프. 억제해도 #8 축 커버는 s021-3.4/b3 의 2건이 그대로 진다(손실 0). |
| s044-6.3 | 3 | 3 | 0 | 일치 |
| s046-6.5 | 2 | 2 | 0 | 일치 |
| s047-6.6 | 2 | 2 | 0 | 일치 |
| s048-6.7 | 2 | 2 | 0 | 일치 |
| s049-6.8 | 14 | 14 | 0 | 일치 |
| s050-7 | 3 | 3 | 0 | 일치 |
| s052-9 | 14 | 2 | -12 | **과대 산정이 센서스 쪽(−12)**. 센서스 note 자신이 «14행 전부 본문 재진술»이라 판정했으나 **전수 대조 결과 두 행이 예외**다(적대 리뷰 H-1 수용으로 −13→−12 정정). ① 핵사고날 행(b15): 센서스가 s038-5.3 note 에서 «주제 서술이라 사본 아님»으로 이미 판정. ② 애그리거트 행(b9)의 둘째 문장 «루트를 통해서만 접근»: restates 대상 s019/b1·b2·b5 어디에도 없고, 문서 전수 검색상 이 규범의 산문 진술은 2083행이 유일하다(예제 펜스 주석 755행은 계수 제외 관례·파일럿 s017-3.2·SKILL Vernon 불릿에도 없음) — 원본 규범이라 Work 승격, 나머지 두 문장 몫 restates 는 유지(norms+restates 동시 보유 = s011-2.5/b19 판형). 잔여 12행은 본문 정본의 압축 사본으로 억제(단 b3·b5·b6 은 사유가 «규범 아님(서술)» — 아래 원장 참조). |
| **합계(36절)** | **206** | **188** | **-18** | 불일치 9절 전건 사유 기재 — Δ −18 = **억제 20**(의사결정 blockquote 6 · §9 요약 행 12 · §2.5 birth-enum 재진술 1 · §6.2 ORM 방향 1) **− 추가 승격 2**(s025 «명시할 항목» · s039-5.4 «질문이 대답을 바꾸지 않는다»). 억제한 의사결정 blockquote 는 실제 7건이나 s022-3.5 [의사결정 #3] 은 센서스 6 산입 밖(내역이 b2·b3·b4 로 채워짐)이라 Δ 에 나타나지 않는다. 적대 리뷰 반영 후에도 합계 188 은 불변 — s052-9/b9 승격(+1)과 s043-6.2/b2 억제(−1)가 상쇄한다. |

**재진술 억제 원장**(`restates` 보유 블록 24 = 의사결정 blockquote 7 · §9 요약 행 13 · §2.5 birth-enum 1 · §6.7 펜스 주석 1 · §6.2 ORM 방향 1 · §3.1 정의문 중복 1. 이 중 위 Δ 에 나타나는 **억제 20** = 의사결정 6(s022-3.5 분은 센서스 산입 밖) + §9 요약 12(b9 는 Work 를 받아 억제 아님) + §2.5 1 + §6.2 1. s048-6.7/b11·s016-3.1/b2 는 센서스 계수 밖이라 억제 계수에 들지 않고 restates 만 싣는다. **판정 열**을 두어 «사본 억제»와 «규범 아님(서술)»을 구분한다 — 적대 리뷰 L-1·L-10 수용)

| 억제 블록 | 사본 내용 | 정본(restates 대상) | 판정 |
|---|---|---|---|
| s004-1.2/b1 | [의사결정 #6] 전략 설계 우선 | s051-8/b8 | 사본 억제 |
| s019/b9 | [의사결정 #4] 결과적 일관성 | s051-8/b6 | 사본 억제 |
| s022-3.5/b1 | [의사결정 #3] 애그리거트↔도메인 서비스 분리 | s051-8/b5 | 사본 억제(센서스 산입 밖) |
| s024-3.7/b1 | [의사결정 #7] 디스패치 타이밍 명시 | s051-8/b9 | 사본 억제 |
| s035-5/b1 | [의사결정 #5] 계층+DIP 동기 흐름 | s051-8/b7 | 사본 억제 |
| s039-5.4/b1 | [의사결정 #2] CQRS 선택 적용 | s051-8/b4 | 사본 억제 |
| s042-6.1/b1 | [의사결정 #8] 4계층 분리 | s051-8/b10 | 사본 억제 |
| s011-2.5/b19(끝 문장) | 발행 봉투 discriminator도 같은 원리 | s026/b2 | 사본 억제(블록은 Work 4 보유) |
| s048-6.7/b11(펜스 주석) | birth-enum·wire 값 수용 | s026/b1 · s011-2.5/b19 | 계수 밖(펜스 주석) — restates 만 |
| s043-6.2/b2(첫 문장) | ORM→도메인 import 방향(Cosmic Python 규칙) | s021-3.4/b3 | 사본 억제(적대 리뷰 M-1) |
| s016-3.1/b2 | 정의문의 «불변(immutable)이어야 한다» | s016-3.1/b3 | 계수 밖(같은 절 정의문 중복) — restates 만(적대 리뷰 L-7) |
| s052-9/b3 | 바운디드 컨텍스트 요약 | s010-2.4/b2 · b3 | **규범 아님(서술·격언)** — 앞 문장은 정의, 뒤 문장은 [B] 강조점 인용. 대상 b2·b3 이 규범 축을 이미 소유(적대 리뷰 L-10) |
| s052-9/b4 | 유비쿼터스 언어 요약 | s009-2.3/b2 · b3 | 사본 억제 |
| s052-9/b5 | 컨텍스트 맵 요약 | s011-2.5/b2 | **규범 아님(서술)** — 행도 대상 블록(258행)도 «시각적으로 표현한 도식이다» 정의. 억제 결론은 유지하되 사유는 사본이 아니라 센서스 행 단위 계수 반박(적대 리뷰 L-1) |
| s052-9/b6 | 증류 요약 | s012-2.6/b2 | **규범 아님(서술)** — 행도 대상 블록(367행)도 «식별하고 분리하는 체계적 기법이다» 정의. 동상(적대 리뷰 L-1) |
| s052-9/b7 | 값 객체 요약 | s016-3.1/b3 | 사본 억제 |
| s052-9/b8 | 엔티티 요약 | s017-3.2/b2 · s051-8/b3 | 사본 억제 |
| s052-9/b9(1·3문장) | 애그리거트 요약 — «일관성·트랜잭션 경계»·«ID로 타 애그리거트 참조» | s019/b1 · b2 · b5 | 부분 억제 — **둘째 문장 «루트를 통해서만 접근»은 원본 규범이라 Work 승격**(적대 리뷰 H-1). 블록이 norms 1 + restates 3 을 동시에 진다 |
| s052-9/b10 | 리포지토리 요약 | s021-3.4/b2 | 사본 억제 |
| s052-9/b11 | 도메인 서비스 요약 | s022-3.5/b2 · b4 | 사본 억제 |
| s052-9/b12 | 응용 서비스 요약 | s023-3.6/b2 · b3 | 사본 억제 |
| s052-9/b13 | 도메인 이벤트 요약 | s024-3.7/b3 | 사본 억제 |
| s052-9/b14 | 계층+DIP 요약 | s036-5.1/b3 · s037-5.2/b2 | 사본 억제 |
| s052-9/b16 | CQRS 요약 | s039-5.4/b2 · b3 | 사본 억제 |

## 2. 배선 근거 표 (전 규범 188건)

소유 분포(발주 36절 188건): 검사기 단독 45 · 검사기+에이전트 병기 50 · 에이전트 단독 93. 무소유 0(도구 단언). class 분포: Obligation 117 · Permission 27 · Prohibition 25 · Exception 16 · Override 3. (적대 리뷰 반영 후 실측 — H-1 승격 +1 Obligation·M-1 억제 −1 Prohibition·M-2/M-3 병기→위임 단독 2건·L-2 위임 단독→병기 1건.)
배선 전 `dddjango/scripts/check-*.py` **27종 전수** docstring 선두를 실독했다(§16 L-F 의무). 실제 배선에 쓰인 검사기 17종 · 미사용 10종(check-api-error-controller-contract·check-common-container·check-composition-root·check-error-centralization·check-ninja-boundary-middleware·check-openapi-error-declaration·check-public-surface-annotation·check-response-schema-bypass·check-synthetic-infra-exc·check-transient-overmapping) — 이 중 **7종**(api-error-controller-contract·error-centralization·ninja-boundary-middleware·openapi-error-declaration·response-schema-bypass·synthetic-infra-exc·transient-overmapping)이 API 오류 프로필·ninja 경계·인프라 예외 축이라 본 문서(도메인 설계)의 규범 문면과 접점이 없다. **나머지 3종은 축이 달라 개별 판정으로 비배선**했다(적대 리뷰 L-12 수용) — check-common-container(횡단 `framework/` 컨테이너의 *위치*: `application/` 형제 — 배치 권위가 §6.1 이 아니라 discipline-houserules 로 이양된 자리라 s042-6.1 은 check-layer-skeleton 으로 배선), check-composition-root(BC 루트 `composition_root/` DI 배선 — 이 문서에 컴포지션 루트 규범 문면 자체가 없음), check-public-surface-annotation(«첫 대입에 타입» 규율 — 타입 표기는 discipline-houserules 소유. 단 #69 «프로덕션 assert 는 ⓓ 후보»는 §4.3 단언과 접점이 있었고 «문서가 요구하는 것은 불변식 선언이지 assert 문법이 아니다»로 판정해 비배선했다 — 아래 §4 경계 메모 자인 ① 참조).

### s004-1.2 (5)

| 블록 | Work label | class | 소유 | 4원 근거 |
|---|---|---|---|---|
| b3 | 전략 설계 1단계 — 핵심 도메인 식별 | Obligation | **delegatedTo** `agent-design-review-ddd` | 문면 역할명 없음·검사기 docstring 27종에 전략 설계 순서 진단 부재 — 위임 기본값(architecture-ddd 설계 시점→design-review-ddd) |
| b3 | 전략 설계 2단계 — 바운디드 컨텍스트 설계 | Obligation | **delegatedTo** `agent-design-review-ddd` | 동상(경계 설계는 설계 시점 판정) |
| b3 | 전략 설계 3단계 — 컨텍스트 매핑 정의 | Obligation | **delegatedTo** `agent-design-review-ddd` | 동상 |
| b3 | 전술 패턴은 전략 설계 다음에 적용 | Obligation | **delegatedTo** `agent-design-review-ddd` | 동상 — 순서 규범의 판정 주체는 Phase 1 설계 리뷰 |
| b4 | 전술 중심 실무 가이드는 구현 단계 한정 활용 | Permission | **delegatedTo** `agent-design-review-ddd` | «활용하되» 조건부 허용 — 문헌 적용 범위 판정은 설계 시점(기본값) |

### s007-2.1 (2)

| 블록 | Work label | class | 소유 | 4원 근거 |
|---|---|---|---|---|
| b3 | 도메인 전문가와 개발자의 공동 모델링 | Obligation | **delegatedTo** `agent-design-review-ddd` | 검사기 27종 docstring에 프로세스(모델링 협업) 진단 없음 — 위임 기본값(설계 시점) |
| b3 | 개발자 단독 모델링 후 검증 방식 배제 | Prohibition | **delegatedTo** `agent-design-review-ddd` | 동상 — «~은 지식 탐구가 아니다» 정의형 부정(P0 애매 보수 포함 승계) |

### s008-2.2 (1)

| 블록 | Work label | class | 소유 | 4원 근거 |
|---|---|---|---|---|
| b6 | 핵심(Core) 하위 도메인은 사내 구현 필수 | Obligation | **delegatedTo** `agent-design-review-ddd` | 표 셀 명령형 — 하위 도메인 유형 판정은 설계 시점(기본값) |

### s009-2.3 (4)

| 블록 | Work label | class | 소유 | 4원 근거 |
|---|---|---|---|---|
| b2 | 코드·문서·대화 전반의 동일 용어 사용 | Obligation | **enforcedBy** `check-business-vocabulary.py` · **delegatedTo** `agent-design-review-ddd` | ④ rule-owner-map 어휘 축은 check-business-vocabulary(#628 업무 어휘 정의 소유)이나 «전 매체 동일 용어»는 정적 진단 밖 — 설계 시점 병기 |
| b3 | 유비쿼터스 언어는 기술 용어가 아닌 업무 용어로 구성 | Obligation | **enforcedBy** `check-naming.py` · **delegatedTo** `agent-design-review-ddd` | ② check-naming docstring #28(원전 패턴 약어 금지)·#36(정도 낱말 칸 금지)·#43(패턴 낱말은 능력 이름에 안 온다)이 «이름은 업무 어휘» 축을 결정적으로 문다 |
| b3 | 용어 1개 = 의미 1개(모호성 금지) | Obligation | **delegatedTo** `agent-design-review-ddd` | 동일 축이나 의미 중복 판정은 정적 검사 밖 — 설계 시점 위임 기본값 |
| b3 | 유비쿼터스 언어의 유효 범위는 BC 경계 안 | Obligation | **enforcedBy** `check-business-vocabulary.py` · **delegatedTo** `agent-design-review-ddd` | ② check-business-vocabulary docstring 격리 절 #47·#52(계약의 업무 어휘 0·BC 이름 0)가 어휘의 BC 국지성을 집행 |

### s010-2.4 (4)

| 블록 | Work label | class | 소유 | 4원 근거 |
|---|---|---|---|---|
| b2 | 같은 용어의 의미가 갈리면 BC를 분리 | Obligation | **delegatedTo** `agent-design-review-ddd` | 경계 설계 판정 — 위임 기본값(설계 시점). 분리 «이후» 격리는 check-context-isolation 소관이라 배선을 겹치지 않음 |
| b3 | BC는 물리적·소유권 경계 — 한 팀 단독 구현·유지관리 | Obligation | **delegatedTo** `agent-design-review-ddd` | 팀 토폴로지 판정은 검사기 표면 밖 — 위임 기본값(설계 시점) |
| b3 | 한 BC는 한 프로젝트 안에 머물며 유스케이스 집합을 포함 | Obligation | **delegatedTo** `agent-design-review-ddd` | 동상 |
| b4 | 하위 도메인↔BC 1:1은 목표이되 강제 아님 | Permission | **delegatedTo** `agent-design-review-ddd` | 허용형 문면(«반드시 그래야 하는 것은 아니다») — 애매 보수 포함(P0 승계)·설계 시점 기본값 |

### s011-2.5 (16)

| 블록 | Work label | class | 소유 | 4원 근거 |
|---|---|---|---|---|
| b7 | 공유 커널은 중복 비용 > 조율 비용일 때만 채택 | Permission | **delegatedTo** `agent-design-review-ddd` | 표 선택 기준 셀 — 공유 커널 채택은 설계 시점 판정(기본값) |
| b7 | 공유 커널의 공유 범위 최소화 필수 | Obligation | **delegatedTo** `agent-design-review-ddd` | 동상 — «필수» 마커 셀 |
| b14 | 큰 진흙공 확산은 ACL로 방어 | Obligation | **enforcedBy** `check-context-isolation.py` · **delegatedTo** `agent-design-review-ddd` | 표 선택 기준 셀 명령형 — ACL 배치 자체는 check-context-isolation(#361·#363) 집행이나 «둘지 여부»는 설계 판정 |
| b16 | ACL 선택 조건 — 외부·레거시 용어의 도메인 누수 위험 | Permission | **delegatedTo** `agent-design-review-ddd` | 채택 조건절 — 설계 시점 기본값 |
| b16 | ACL 선택 조건 — 상·하류 lifecycle 상이 | Permission | **delegatedTo** `agent-design-review-ddd` | 동상 |
| b16 | ACL 선택 조건 — 공개 통합 계약과 내부 모델의 의미 상이 | Permission | **delegatedTo** `agent-design-review-ddd` | 동상 |
| b17 | ACL 회피 조건 — 외부 모델이 이미 BC 언어와 일치 | Exception | **delegatedTo** `agent-design-review-ddd` | 비채택 조건절 — 설계 시점 기본값 |
| b17 | ACL 회피 조건 — 단순 field rename 수준 | Exception | **delegatedTo** `agent-design-review-ddd` | 동상 |
| b18 | ACL은 경계 근처에 둔다 | Obligation | **enforcedBy** `check-context-isolation.py` · **delegatedTo** `agent-design-review-ddd` | ② check-context-isolation docstring ACL 절 #361(상대 BC 하나=폴더 하나)·#363(<Bc><Capability>Adapter)이 ACL 자리를 집행 |
| b18 | 번역 로직의 도메인 객체 내부 산발 배치 금지 | Prohibition | **enforcedBy** `check-context-isolation.py` · **delegatedTo** `agent-discipline-reviewer` | ② 같은 절 #13(OHS 소비는 ACL 뿐)·#12 — 번역 창구 단일화 |
| b18 | 번역 대상은 형태뿐 아니라 status·단위·식별자·lifecycle 의미 | Obligation | **delegatedTo** `agent-design-review-ddd` | 의미 번역 충실성은 정적 검사 밖 — 설계 시점 기본값 |
| b18 | published language·versioning은 architecture-api로 이양 | Obligation | **delegatedTo** `agent-design-review-api` | ① 문면이 `architecture-api` 소유를 직접 지정 — 기본값(design-review-ddd) 이탈의 문면 근거 |
| b19 | 상수·Enum은 소유 BC 내부 자산 — 타 BC 직접 import 금지 | Prohibition | **enforcedBy** `check-context-isolation.py` · **delegatedTo** `agent-discipline-reviewer` | ② check-context-isolation docstring 타 BC 절 #12(부를 수 있는 것은 OHS·published_event 둘)·#13 |
| b19 | BC 간 연결은 OHS 계약 타입 또는 wire value — 각자 선언은 published language 수용 | Obligation | **enforcedBy** `check-context-isolation.py` · **delegatedTo** `agent-design-review-ddd` | 동상 #12·#13 — 창구 한정이 곧 wire 수용 규율 |
| b19 | 공용 승격은 «같은 변경 사유로 함께 수정» 근거가 명세에 있을 때만 | Permission | **delegatedTo** `agent-design-review-ddd` | 공유 커널 결정은 설계 시점 판정 — 기본값 |
| b19 | 승격 enum 배치는 houserules 표준 트리 — 공유 커널은 domain_layer의 유일 외부 의존 | Obligation | **enforcedBy** `check-domain-model.py` · **delegatedTo** `agent-discipline-reviewer` | ② check-domain-model docstring #8(domain_layer 밖으로 나가는 import 0)·#298(shared_value_object import 범위)이 예외 축을 집행 |

### s012-2.6 (1)

| 블록 | Work label | class | 소유 | 4원 근거 |
|---|---|---|---|---|
| b5 | 핵심 도메인에 최고의 인재 투입 | Obligation | **delegatedTo** `agent-design-review-ddd` | 표 셀 명령형 — 인력 배치는 검사기 표면 밖·설계 시점 기본값 |

### s016-3.1 (3)

| 블록 | Work label | class | 소유 | 4원 근거 |
|---|---|---|---|---|
| b3 | 값 객체 동등성은 속성 조합으로 판정(식별자 없음) | Obligation | **enforcedBy** `check-domain-model.py` · **delegatedTo** `agent-discipline-reviewer` | ② check-domain-model docstring #259(후보: id 를 가진 value_object — 자리 뒤바뀜 신호)·#260이 식별자↔값 객체 축을 문다 |
| b3 | 값 객체는 반드시 불변 | Obligation | **enforcedBy** `check-domain-model.py` | ② check-domain-model #264 «값 객체 불변 — __init__/__post_init__ 밖 self 대입 금지» 문면 일치 |
| b3 | 값 객체 setter 금지 | Prohibition | **enforcedBy** `check-domain-model.py` | 동상 #264(같은 술어의 금지 축) |

### s019 (16)

| 블록 | Work label | class | 소유 | 4원 근거 |
|---|---|---|---|---|
| b1 | 규칙 1 — 진짜 불변식을 일관성 경계 안에서 보호 | Obligation | **enforcedBy** `check-domain-model.py` · **delegatedTo** `agent-design-review-ddd` | ② check-domain-model #257(상태 변경은 루트를 지난다)이 불변식 보호 축의 결정적 부분·경계 «설정»은 설계 판정 |
| b2 | 한 트랜잭션 = 애그리거트 하나 | Obligation | **enforcedBy** `check-transaction-boundary.py` | ② check-transaction-boundary docstring 선두 «「한 트랜잭션 = 애그리거트 하나」(D50) 축의 결정적 백스톱» 문면 일치(#195·#599) |
| b2 | 애그리거트 경계 = 불변식 동시 보장 범위 | Obligation | **delegatedTo** `agent-design-review-ddd` | 경계 «일치» 판정은 정적 검사 밖 — 설계 시점 기본값 |
| b3 | 규칙 2 — 작은 애그리거트 설계 | Obligation | **delegatedTo** `agent-design-review-ddd` | 크기 판정은 검사기 표면 밖 — 설계 시점 기본값 |
| b4 | 애그리거트는 루트+최소 속성·값 객체로 제한(Vernon 인용=규칙) | Obligation | **delegatedTo** `agent-design-review-ddd` | P0 규약 ② 인용=규칙 승계 — 설계 시점 기본값 |
| b5 | 규칙 3 — 다른 애그리거트는 ID로만 참조 | Obligation | **enforcedBy** `check-domain-model.py` · **delegatedTo** `agent-design-review-ddd` | ② check-domain-model #253(<A>/** 는 <B>/ 의 루트 모듈만 import)·#258(entity 직접 참조 금지) |
| b7 | BC 경계를 넘는 ORM 관계(FK·O2O·M2M) 금지 | Prohibition | **enforcedBy** `check-db-table.py` | ② check-db-table docstring #631 «타 BC 모델을 FK·O2O·M2M 으로 참조 금지(문자열 참조 포함)» 문면 일치 |
| b7 | 타 BC 애그리거트는 ID 값 참조 — 무결성은 ACL/OHS 조회와 상류 이벤트로 | Obligation | **enforcedBy** `check-db-table.py`, `check-context-isolation.py` | ② #631(ID 값 저장) + check-context-isolation #12·#13(창구는 OHS·published_event) |
| b7 | FK 경계 3분 — 애그리거트 내부 자유·같은 BC 허용·다른 BC 금지 | Permission | **enforcedBy** `check-db-table.py` · **delegatedTo** `agent-design-review-ddd` | ② #631의 대칭 허용 축(같은 BC 는 비대상) |
| b7 | 플랫폼 횡단 공유(AUTH_USER_MODEL·공유 커널 값객체)는 예외 | Exception | **enforcedBy** `check-db-table.py` · **delegatedTo** `agent-design-review-ddd` | ② #631 예외 조항 — 판정 주체 병기(설계) |
| b8 | 규칙 4 — 일관성 경계 밖은 결과적 일관성 | Obligation | **enforcedBy** `check-transaction-boundary.py` · **delegatedTo** `agent-design-review-ddd` | ② check-transaction-boundary(D50 축)가 «한 트랜잭션 하나» 쪽을 집행·전환 판정은 설계 |
| b10 | 동일 DB 단순 케이스의 복수 애그리거트 수정 용인(배경 이론) | Permission | **delegatedTo** `agent-design-review-ddd` | 원전 이론 조항 — 채택 여부 판정은 설계 시점 |
| b10 | dddjango 생성 코드의 정본은 「한 트랜잭션 = 애그리거트 하나」 | Override | **enforcedBy** `check-transaction-boundary.py` | ② check-transaction-boundary docstring 선두(D50·#546 축) — 원전 용인을 덮는 내부 정본 |
| b10 | 분산 시 즉시 결과적 일관성으로 전환 | Obligation | **delegatedTo** `agent-design-review-ddd` | 분산 전환 판정은 설계 시점 기본값 |
| b10 | 복수 애그리거트 수정 용인은 FK 결합을 허가하지 않음 | Prohibition | **enforcedBy** `check-db-table.py` | ② check-db-table #631 — 런타임 원자성과 영속성 결합의 직교 선언 |
| b10 | 「한 트랜잭션에 묶인다」를 BC 경계 FK 근거로 원용 금지 | Prohibition | **enforcedBy** `check-db-table.py` · **delegatedTo** `agent-discipline-reviewer` | 동상 #631(같은 축의 논거 차단) |

### s021-3.4 (4)

| 블록 | Work label | class | 소유 | 4원 근거 |
|---|---|---|---|---|
| b2 | 리포지토리는 애그리거트 단위로 영속성 처리 | Obligation | **enforcedBy** `check-transaction-boundary.py` | ② check-transaction-boundary #282(선언은 <aggregate>_repository.py)·#287(쓰기 인자는 애그리거트)·#355(반환 타입) |
| b2 | 인터페이스는 도메인에·구현은 인프라에(DIP) | Obligation | **enforcedBy** `check-transaction-boundary.py`, `check-port-adapter-pairing.py` | ② check-transaction-boundary #283(계약은 추상 메서드만) + check-port-adapter-pairing #460(구현은 driven_layer/adapter/)·#477(리포지토리 구현은 domain import 필수) |
| b3 | ORM이 도메인 모델을 import한다 | Obligation | **enforcedBy** `check-domain-model.py` | ② check-domain-model #8(domain_layer 의 밖으로 나가는 import 0)의 역방향 짝 — 인용=규칙(P0 규약 ②) |
| b3 | 도메인 모델의 ORM import 금지 | Prohibition | **enforcedBy** `check-domain-model.py` | ② check-domain-model #8 문면 정확 일치 |

### s022-3.5 (6)

| 블록 | Work label | class | 소유 | 4원 근거 |
|---|---|---|---|---|
| b2 | 도메인 서비스는 여러 애그리거트에 걸친 도메인 로직을 담당 | Obligation | **enforcedBy** `check-domain-model.py` · **delegatedTo** `agent-design-review-ddd` | ② check-domain-model #300(<aggregate>/domain_service/ 금지 — BC 레벨 한 칸뿐)이 자리를 집행 |
| b2 | 도메인 서비스는 무상태(stateless) | Obligation | **delegatedTo** `agent-design-review-ddd` | 상태 보유 판정은 정적 검사 표면 밖 — 설계 시점 기본값 |
| b3 | 상태 변경·상태 값 계산 로직은 도메인 서비스로 귀속 | Obligation | **delegatedTo** `agent-design-review-ddd` | 귀속 판정은 설계 시점(판정 소유 결정) — 기본값 |
| b3 | 트랜잭션·조회/저장 조율은 응용 서비스로 귀속 | Obligation | **delegatedTo** `agent-design-review-ddd` | 동상 |
| b4 | 응용 서비스가 도메인 서비스를 호출 — 애그리거트는 순수 도메인 로직만 | Obligation | **enforcedBy** `check-domain-model.py` · **delegatedTo** `agent-design-review-ddd` | ② check-domain-model #8(domain_layer 밖 import 0) — 애그리거트가 서비스를 모르는 구조를 집행 |
| b4 | 애그리거트는 외부 의존성을 받지 않는다 | Prohibition | **enforcedBy** `check-domain-model.py` | ② check-domain-model #8·#301(루트 인자 축) |

### s023-3.6 (9)

| 블록 | Work label | class | 소유 | 4원 근거 |
|---|---|---|---|---|
| b2 | 응용 서비스는 비즈니스 로직을 직접 구현하지 않고 도메인에 위임 | Obligation | **enforcedBy** `check-transaction-boundary.py`, `check-usecase-dto-placement.py` · **delegatedTo** `agent-discipline-reviewer` | ② check-transaction-boundary #195(루트 메서드 호출을 거치지 않는 쓰기 금지) + check-usecase-dto-placement #194(유스케이스 안 업무 규칙 ⓓ 후보) |
| b3 | 응용 서비스 책임 — 리포지토리에서 애그리거트 조회 | Obligation | **enforcedBy** `check-transaction-boundary.py` | ② check-transaction-boundary #195(save 인자는 같은 함수에서 루트 메서드 호출을 받은 객체) |
| b3 | 응용 서비스 책임 — 애그리거트 도메인 기능 실행 | Obligation | **enforcedBy** `check-transaction-boundary.py` | 동상 #195(UoW 를 받았는데 루트 메서드 호출 0 이면 위반) |
| b3 | 응용 서비스 책임 — 트랜잭션 관리 | Obligation | **enforcedBy** `check-transaction-boundary.py` | ② #197(읽기 전용은 UoW 를 받지 않는다)·#200(커밋 뒤 부작용은 unit_of_work.after_commit) |
| b3 | 응용 서비스 책임 — 결과 반환 | Obligation | **enforcedBy** `check-usecase-dto-placement.py` | ② check-usecase-dto-placement #635(execute 하나·계약 객체 하나 → result) |
| b4 | 응용 서비스의 도메인 로직 직접 구현 금지 | Prohibition | **enforcedBy** `check-usecase-dto-placement.py` · **delegatedTo** `agent-discipline-reviewer` | ② check-usecase-dto-placement #194(유스케이스 안 업무 규칙 — ⓓ 후보, 마무리는 discipline-reviewer) |
| b4 | 응용 서비스의 표현 영역 의존 금지(HttpRequest 인자 금지) | Prohibition | **enforcedBy** `check-usecase-dto-placement.py`, `check-event-publish.py` | ② check-usecase-dto-placement #208(command 는 schema_in 타입을 쓰지 않는다 — driving import 금지) + check-event-publish #7(application_layer import 허용은 넷) |
| b5 | 입력 자료·실행체 명명 계약 — <UseCase>Command / <UseCase>UseCase.execute | Obligation | **enforcedBy** `check-usecase-dto-placement.py` | ① 문면이 #635 를 직접 인용 · ② check-usecase-dto-placement docstring 진입점 절 #635·자료 절 #201 문면 일치 |
| b5 | …Request/…Response는 OHS contract 전용 — 두 어휘 혼용 금지 | Prohibition | **enforcedBy** `check-context-isolation.py` | ① 문면이 #484 를 직접 인용 · ② check-context-isolation docstring OHS 절 «#482/#483/#484 명명» |

### s024-3.7 (2)

| 블록 | Work label | class | 소유 | 4원 근거 |
|---|---|---|---|---|
| b3 | 도메인 이벤트는 애그리거트 안에 수집한다(즉시 발행 금지) | Obligation | **enforcedBy** `check-domain-model.py` | ② check-domain-model #272 «루트는 이벤트를 기록만 한다 — publish/dispatch 호출 금지» 문면 일치 |
| b3 | 디스패치는 uow.after_commit 한 경로(커밋 직전은 배경 이론) | Override | **enforcedBy** `check-usecase-dto-placement.py`, `check-transaction-boundary.py` | ① 문면이 #539~#541 을 직접 인용 · ② check-usecase-dto-placement 발행 절 #541(커밋 «전» 발행 금지)·#539·#540 + check-transaction-boundary #200 |

### s025 (15)

| 블록 | Work label | class | 소유 | 4원 근거 |
|---|---|---|---|---|
| b1 | 이벤트는 애그리거트와 같은 트랜잭션에 outbox 적재 후 별도 프로세스가 발행 | Obligation | **enforcedBy** `check-broker-contract.py` · **delegatedTo** `agent-design-review-ddd` | ② check-broker-contract #603 «external 에 내용이 오면 딸림이 함께 선다 — ⑴outbox …» |
| b3 | Outbox 선택 조건 — 커밋 이후 외부 전달 유실 불허 | Permission | **delegatedTo** `agent-design-review-ddd` | 채택 조건절 — 채택 판정은 설계 시점(기본값) |
| b3 | Outbox 채택은 듣는 쪽이 별도 배포 단위일 때 한정 | Permission | **enforcedBy** `check-broker-contract.py` | ① 문면이 #529 를 직접 인용 · ② check-broker-contract #529 «external 을 가르는 물음 「듣는 쪽이 다른 배포 단위에 있나」» |
| b3 | external 채택 시 outbox 필수 딸림 | Obligation | **enforcedBy** `check-broker-contract.py` | ① 문면 #603 인용 · ② check-broker-contract #603 문면 일치 |
| b3 | 같은 저장소 소비자의 유실 불허는 cron_job→주인 OHS 폴링 | Obligation | **enforcedBy** `check-missable-entrance.py` | ① 문면 #626 인용 · ② check-missable-entrance #629 설명절 «메우는 길은 cron_job 이 주인에게 «묻는» 것(#626)» |
| b3 | Outbox 선택 조건 — at-least-once 전달과 consumer 멱등성 설계 가능 | Permission | **enforcedBy** `check-broker-contract.py` · **delegatedTo** `agent-design-review-ddd` | ② check-broker-contract #532(external 계약은 at-least-once 를 요구로 적는다) |
| b3 | Outbox 선택 조건 — retry·dead-letter·dispatch ownership 필요 | Permission | **enforcedBy** `check-broker-contract.py` · **delegatedTo** `agent-design-review-ddd` | ② check-broker-contract #603 ⑷데드레터 등 «선언 유무» |
| b4 | Outbox 회피 조건 — 외부 부수효과 없음 | Exception | **delegatedTo** `agent-design-review-ddd` | 비채택 조건절 — 설계 시점 기본값 |
| b4 | Outbox 회피 조건 — transaction.on_commit()으로 충분한 in-process 후속 | Exception | **delegatedTo** `agent-design-review-ddd` | 동상 |
| b4 | Outbox 회피 조건 — 유실 수용 또는 운영 부담 과다 | Exception | **delegatedTo** `agent-design-review-ddd` | 동상 |
| b5 | Outbox 채택 시 명시 항목(트랜잭션·dispatcher owner·전달 보장·멱등 기준·retry 정책·발행 언어) | Obligation | **delegatedTo** `agent-design-review-ddd` | 명세 기재 의무 — 설계 시점 산출물 판정(기본값) |
| b5 | 전달 메커니즘 소유는 architecture-db(§9.7) | Obligation | **delegatedTo** `agent-design-review-db` | ① 문면이 `architecture-db` 를 직접 지정 — 기본값 이탈의 문면 근거 |
| b5 | Django 트랜잭셔널 outbox 구체 구현 소유는 implementation-django(§16.5) | Obligation | **delegatedTo** `agent-discipline-reviewer` | ① 문면이 `implementation-django` 지정 · 위임 기본값 표(implementation-*→discipline-reviewer) |
| b5 | 신뢰성 검증 항목은 discipline-tdd 입장 심사 제출 대상 | Obligation | **delegatedTo** `agent-discipline-reviewer` | ① 문면이 `discipline-tdd` 지정 · 기본값 표(discipline-tdd→discipline-reviewer) |
| b5 | add 결정 후 작성 mechanics만 implementation-test 소유 | Obligation | **delegatedTo** `agent-discipline-reviewer` | ① 문면 `implementation-test` 지정 · 기본값 표 동상 |

### s026 (18)

블록 경계 자인(적대 리뷰 L-3): b2 `[1204-1209]` 는 주제가 다른 최상위 불릿 **5개**를 한 블록으로 묶는다. §13 은 «한 블록의 여러 규범 문장은 statesNorm 다중 연결 + 블록 내 문장→Work 대응을 검수표에 기록»으로 이 형태를 허용하므로 분할하지 않고, 대신 아래 표의 블록 열에 **불릿 좌표 ①~⑤(원문 행 번호)** 를 병기해 조준 해상도를 회복한다 — ①1204 배치·소유 / ②1205 파생 표기 / ③1206 수명(append-only) / ④1207 제외(짝 조항) / ⑤1208 소비자 측 짝 규칙. s011-2.5/b19·s048-6.7/b11·SKILL 유예 #8 의 restates 는 블록 단위(s026/b1·b2)를 유지한다.

| 블록 | Work label | class | 소유 | 4원 근거 |
|---|---|---|---|---|
| b1 | 발행 봉투 판별자는 1종째부터 domain_layer StrEnum 하나로 선언(birth-enum) | Obligation | **enforcedBy** `check-domain-model.py` · **delegatedTo** `agent-design-review-ddd` | ② check-domain-model #269(<A>/event/ 는 BC 안에서 읽혀야)·#8(domain 소유)이 슬롯·소유 축을 집행 · 1종째 승격 판정 자체는 설계 시점 |
| b1 | 이름 기반 승격 트리거 금지(type/kind 이름 사유 승격 금지) | Prohibition | **delegatedTo** `agent-discipline-reviewer` | ① 문면이 `discipline-cleancode` §2.14 로 위임 · 기본값 표(discipline-cleancode→discipline-reviewer) |
| b2 ①(1204) | 배치 — domain_layer/<aggregate>/event/event_type.py 슬롯 | Obligation | **enforcedBy** `check-layer-skeleton.py` | ① 문면이 `discipline-houserules` §2 지정 · ② check-layer-skeleton #489·#490(트리 폐쇄)이 슬롯을 집행 |
| b2 ①(1204) | 발행 enum의 타 BC 직접 import 금지 | Prohibition | **enforcedBy** `check-context-isolation.py` | ② check-context-isolation #12·#13(부를 수 있는 것은 OHS·published_event 둘) |
| b2 ①(1204) | 경계-로컬(presentation 봉투 모듈) 배치 금지 | Prohibition | **enforcedBy** `check-layer-skeleton.py` · **delegatedTo** `agent-discipline-reviewer` | ② check-layer-skeleton #490(트리에 없는 경로 금지) — 역방향 import 회피 사유는 문면 |
| b2 ②(1205) | 파생 표기 — 봉투 Schema 태그는 Literal[EventType.X] 파생 | Obligation | **enforcedBy** `check-choices-literal-consumption.py` · **delegatedTo** `agent-discipline-reviewer` | ② check-choices-literal-consumption(선언된 심볼의 리터럴 소비 백스톱) 부분 커버 · 잔여 의미 레인은 reviewer 몫(docstring «보지 않는 것») |
| b2 ②(1205) | union-enum 동기 검증은 독자 failure·미보호일 때만 add | Obligation | **delegatedTo** `agent-discipline-reviewer` | ① 문면이 `discipline-tdd` 입장 심사 지정 · 기본값 표 |
| b2 ②(1205) | 승인 후 테스트 mechanics는 implementation-test §15.5 | Obligation | **delegatedTo** `agent-discipline-reviewer` | ① 문면 `implementation-test` 지정 · 기본값 표 |
| b2 ②(1205) | ORM default·마이그레이션 경계는 .value 평탄화 | Obligation | **enforcedBy** `check-choices-literal-consumption.py` | ② check-choices-literal-consumption docstring 회피 5 «default=OrderStatus.PENDING.value(Attribute) 는 정상(.value 평탄화)» 문면 일치 |
| b2 ③(1206) | 수명 — 멤버는 추가만 한다(append-only) | Obligation | **delegatedTo** `agent-discipline-reviewer` | 정적 검사에 enum 이력 비교 진단 부재(27종 docstring 실독) — 위임 기본값(구현 시점 규범→discipline-reviewer) |
| b2 ③(1206) | 수명 — 멤버 값 변경·삭제 금지 | Prohibition | **delegatedTo** `agent-discipline-reviewer` | 동상 — 이력 대조는 검사기 표면 밖 |
| b2 ③(1206) | 이벤트 폐기는 삭제가 아니라 발행 중단+주석 표기 | Obligation | **delegatedTo** `agent-discipline-reviewer` | 동상 |
| b2 ③(1206) | 비호환 변경은 새 버전 태그 추가+upcasting | Obligation | **delegatedTo** `agent-discipline-reviewer` | 동상 |
| b2 ④(1207) | 제외 — payload_schema_version 등 버전 태그는 리터럴 동결 유지 | Exception | **delegatedTo** `agent-discipline-reviewer` | 짝 조항(비대상 선언) — 구현 시점 판정 기본값 |
| b2 ④(1207) | 제외 — 상류 중계 소비 측 스키마 태그 비대상 | Exception | **delegatedTo** `agent-discipline-reviewer` | 동상(published language 수용) |
| b2 ④(1207) | 제외 — OHS published contract의 discriminator 자리 비대상 | Exception | **enforcedBy** `check-context-isolation.py` | ② check-context-isolation OHS 절 #472 «contract 는 stdlib·같은 BC 계약만» — contract 무의존이 wire Literal 유지의 집행 근거 |
| b2 ④(1207) | 드리프트 검증 후보도 입장 심사에서 판정 | Obligation | **delegatedTo** `agent-discipline-reviewer` | ① 문면이 `discipline-cleancode` §2.14 재예외로 위임 · 기본값 표 |
| b2 ⑤(1208) | 소비 BC는 미지 event_type 처리 방침을 함께 정한다 | Obligation | **delegatedTo** `agent-design-review-ddd` | 27종 전수 실독 — 미지 타입 폴백·거부 방침(분기 완전성)을 무는 정적 진단 부재. 초안의 `check-event-publish` #507 은 event_subscription 의 *import 폭* 규칙이라 접점 0 이어서 철회했다(적대 리뷰 M-3 수용) — 위임 기본값(설계 시점) |

### s029-4.1 (1)

| 블록 | Work label | class | 소유 | 4원 근거 |
|---|---|---|---|---|
| b1 | 이름은 무엇(what)을 드러내고 어떻게(how)는 숨긴다 | Obligation | **enforcedBy** `check-port-adapter-pairing.py`, `check-naming.py` · **delegatedTo** `agent-discipline-reviewer` | ② check-port-adapter-pairing #485 «메서드는 의도(확정: notify·handle·execute… / 후보: 동사 아님)» + check-naming #43(패턴 낱말은 능력 이름에 안 온다) |

### s030-4.2 (1)

| 블록 | Work label | class | 소유 | 4원 근거 |
|---|---|---|---|---|
| b1 | 도메인 로직은 가능한 한 부작용 없는 함수로 배치 | Obligation | **enforcedBy** `check-domain-model.py` · **delegatedTo** `agent-discipline-reviewer` | ② check-domain-model #264(값 객체 불변 — self 대입 금지)가 대표 자리를 집행 · 잔여 «가능한 한» 판정은 구현 리뷰 |

### s031-4.3 (1)

| 블록 | Work label | class | 소유 | 4원 근거 |
|---|---|---|---|---|
| b1 | 사후 조건·클래스 불변식의 명시적 선언 | Obligation | **enforcedBy** `check-domain-model.py` · **delegatedTo** `agent-discipline-reviewer` | ② check-domain-model #268 «후보: __init__/__post_init__ 에 raise 0 인 값 객체(잘못된 값이 불가능한가)» — 불변식 선언 축 |

### s032-4.4 (2)

| 블록 | Work label | class | 소유 | 4원 근거 |
|---|---|---|---|---|
| b1 | 도메인의 자연스러운 경계선을 따라 설계를 분해 | Obligation | **delegatedTo** `agent-design-review-ddd` | 경계 분해 판정은 설계 시점 — 위임 기본값 |
| b1 | 함께 변하는 것은 함께·따로 변하는 것은 분리 | Obligation | **delegatedTo** `agent-design-review-ddd` | 동상(변경 이유 기준 응집 판정) |

### s033-4.5 (1)

| 블록 | Work label | class | 소유 | 4원 근거 |
|---|---|---|---|---|
| b1 | 클래스 간 결합 최소화 — 독립적 이해 가능성 확보 | Obligation | **delegatedTo** `agent-discipline-reviewer` | 결합도 판정은 정적 검사 표면 밖 — 구현 시점 규범 기본값(discipline-reviewer) |

### s034-4.6 (1)

| 블록 | Work label | class | 소유 | 4원 근거 |
|---|---|---|---|---|
| b1 | 연산의 닫힘 — 반환 타입을 인자 타입과 동일하게 정의 | Permission | **delegatedTo** `agent-design-review-ddd` | 조건형 권고(애매 보수 포함·P0 승계) — 설계 시점 기본값 |

### s035-5 — Work 0 (전량 재진술 사본)

### s036-5.1 (3)

| 블록 | Work label | class | 소유 | 4원 근거 |
|---|---|---|---|---|
| b3 | 의존은 상위→하위 단방향(하위→상위 금지) | Obligation | **enforcedBy** `check-context-isolation.py` | ② check-context-isolation 방향 절 #2·#251(domain 으로 들어오는 화살표)·#322 문면 일치 |
| b3 | 도메인·응용·표현의 인프라 구현 기술 직접 사용 금지 | Prohibition | **enforcedBy** `check-context-isolation.py`, `check-transaction-boundary.py` | ② check-context-isolation #2(안쪽 두 칸은 구체 기술을 모른다) + check-transaction-boundary #4(application_layer import 에 django 금지) |
| b3 | DIP — 도메인이 정의한 인터페이스를 인프라가 구현 | Obligation | **enforcedBy** `check-port-adapter-pairing.py` | ② check-port-adapter-pairing #457(선언 자리)·#460(구현 자리)·#351(선언↔구현 1:1) |

### s037-5.2 (2)

| 블록 | Work label | class | 소유 | 4원 근거 |
|---|---|---|---|---|
| b2 | 고수준 모듈은 저수준이 아니라 추상화에 의존 | Obligation | **enforcedBy** `check-context-isolation.py`, `check-port-adapter-pairing.py` | ② check-context-isolation #2·#9(driven 은 domain·port 만) + check-port-adapter-pairing #212(선언만·구현 0줄) |
| b2 | 인터페이스는 고수준 영역에 위치 | Obligation | **enforcedBy** `check-port-adapter-pairing.py` | ② check-port-adapter-pairing #457 «선언은 application_layer/port/ 아래뿐»·#313(domain_layer/<agg>/port/ 금지) — dddjango 구체화 자리 |

### s038-5.3 (16)

| 블록 | Work label | class | 소유 | 4원 근거 |
|---|---|---|---|---|
| b2 | 의존 방향은 항상 정책(도메인·응용) 쪽 — 포트는 역할·어댑터는 번역 | Obligation | **enforcedBy** `check-context-isolation.py` | ② check-context-isolation #2·#251(방향)이 결정적 부분을 집행 |
| b3 | 핵사고날 선택 조건 — 외부·레거시가 도메인 모델을 오염시킬 위험 | Permission | **delegatedTo** `agent-design-review-ddd` | 아키텍처 스타일 채택 판정 — 설계 시점 기본값 |
| b3 | 핵사고날 선택 조건 — 영속성 형태와 도메인 언어 상이 | Permission | **delegatedTo** `agent-design-review-ddd` | 동상 |
| b3 | 핵사고날 선택 조건 — 프레임워크 없는 유스케이스 테스트 가치 | Permission | **delegatedTo** `agent-design-review-ddd` | 동상 |
| b3 | 핵사고날 선택 조건 — 교체 가능성·장애 격리·계약 안정성 요구 | Permission | **delegatedTo** `agent-design-review-ddd` | 동상 |
| b4 | 핵사고날 회피 조건 — Django 관례가 더 명확 | Exception | **delegatedTo** `agent-design-review-ddd` | 비채택 조건절 — 설계 시점 기본값 |
| b4 | 핵사고날 회피 조건 — 포트가 기술명만 감춘 얇은 wrapper | Exception | **delegatedTo** `agent-design-review-ddd` | 동상 |
| b4 | 핵사고날 회피 조건 — 단일 구현·저변동·테스트 seam 불요 | Exception | **delegatedTo** `agent-design-review-ddd` | 동상 |
| b5 | 포트 이름은 기술이 아니라 역할 | Obligation | **enforcedBy** `check-port-adapter-pairing.py`, `check-naming.py` | ② check-port-adapter-pairing #594(폴더 이름에 누가·언제·어떻게 금지)·#220(<Capability>Port) + check-naming #41 |
| b5 | 포트 메서드는 좁고 유스케이스 언어를 따른다 | Obligation | **enforcedBy** `check-port-adapter-pairing.py` · **delegatedTo** `agent-discipline-reviewer` | ② check-port-adapter-pairing #485(메서드는 의도) |
| b5 | 포트 입출력은 도메인·응용 DTO·값 객체·식별자 | Obligation | **enforcedBy** `check-port-adapter-pairing.py` | ② check-port-adapter-pairing #228(<data>_in/_out 에 도메인·유스케이스 DTO 금지)·#227 |
| b5 | 구조적 협력은 Protocol 우선·상속/런타임 등록 필요 시 ABC | Permission | **enforcedBy** `check-port-adapter-pairing.py` · **delegatedTo** `agent-discipline-reviewer` | ② check-port-adapter-pairing #551(계약은 ABC+@abstract) — 선택 기준 잔여는 구현 리뷰 |
| b5 | 모든 클래스에 인터페이스를 만들지 않는다 | Prohibition | **delegatedTo** `agent-discipline-reviewer` | 과잉 추상화 판정은 정적 검사 밖 — 구현 시점 기본값 |
| b6 | 인터페이스 어댑터 분류 — view·router·serializer·command·task·handler | Obligation | **enforcedBy** `check-port-adapter-pairing.py` | ② check-port-adapter-pairing #319(네 갈래)·#460(구현 자리) |
| b6 | 인프라 어댑터 분류 — ORM 리포지토리·SDK·publisher·cache/filesystem | Obligation | **enforcedBy** `check-port-adapter-pairing.py` | 동상 #319·#349·#367 |
| b6 | 어댑터의 핵심 정책 소유 금지 | Prohibition | **enforcedBy** `check-context-isolation.py` · **delegatedTo** `agent-discipline-reviewer` | ② check-context-isolation #2(안쪽 두 칸)·#9 구조 축 · 정책 «소유» 의미 판정은 reviewer |

### s039-5.4 (10)

| 블록 | Work label | class | 소유 | 4원 근거 |
|---|---|---|---|---|
| b2 | CQRS는 보조 패턴으로 취급·일부 BC에만 선택 적용(Greg Young 인용=규칙) | Permission | **delegatedTo** `agent-design-review-ddd` | P0 규약 ② 인용=규칙 승계 — 패턴 채택 범위 판정은 설계 시점 |
| b3 | 커맨드와 쿼리의 모델 분리 | Obligation | **enforcedBy** `check-usecase-dto-placement.py` · **delegatedTo** `agent-design-review-ddd` | ② check-usecase-dto-placement #464(command/query 분할 금지 — 어댑터 층)·#201(자료 세 파일) 구조 축 |
| b3 | 질문하는 행동이 대답을 바꾸지 않는다 | Prohibition | **enforcedBy** `check-transaction-boundary.py` · **delegatedTo** `agent-discipline-reviewer` | ② check-transaction-boundary #197 «읽기 전용 유스케이스는 UnitOfWork 를 받지 않는다»가 CQS 의 구조 절반(질문이 쓰기 기계를 들지 않는다)을 결정적으로 집행 — §16 역방향(담당 근거가 있는데 기본값 도피) 해소(적대 리뷰 L-2 수용). 잔여(변수 수준 부작용·조회 중 상태 변경)는 의미 레인이라 구현 리뷰 병기 |
| b3 | 전체가 아닌 필요 컨텍스트 한정 선택 적용 | Permission | **delegatedTo** `agent-design-review-ddd` | «안전하다» 애매 보수 포함(P0 승계) — 설계 시점 기본값 |
| b4 | CQRS 선택 조건 — 쓰기 불변식과 읽기 projection의 모델 상이 | Permission | **delegatedTo** `agent-design-review-ddd` | 채택 조건절 — 설계 시점 기본값 |
| b4 | CQRS 선택 조건 — 읽기 성능·비정규화·reporting이 커맨드 모델을 왜곡 | Permission | **delegatedTo** `agent-design-review-ddd` | 동상 |
| b4 | CQRS 선택 조건 — 커맨드와 쿼리의 변경 이유 분리 | Permission | **delegatedTo** `agent-design-review-ddd` | 동상 |
| b5 | CQRS 회피 조건 — selector·QuerySet 최적화로 충분 | Exception | **delegatedTo** `agent-design-review-ddd` | 비채택 조건절 — 설계 시점 기본값 |
| b5 | CQRS 회피 조건 — 단순 CRUD를 더 어렵게만 만듦 | Exception | **delegatedTo** `agent-design-review-ddd` | 동상 |
| b5 | CQRS 회피 조건 — eventual consistency 감당 기준 부재 | Exception | **delegatedTo** `agent-design-review-ddd` | 동상 |

### s040-5.5 (5)

| 블록 | Work label | class | 소유 | 4원 근거 |
|---|---|---|---|---|
| b5 | 진화하는 질서 — 대규모 구조를 처음부터 완성하지 말고 함께 진화 | Obligation | **delegatedTo** `agent-design-review-ddd` | 표 셀 명령형(애매 보수 포함·P0 승계) — 대규모 구조는 설계 시점 기본값 |
| b6 | 시스템 은유 — 관통 비유를 찾아 명시화 | Obligation | **delegatedTo** `agent-design-review-ddd` | 동상 |
| b7 | 책임 계층 — 도메인 모델을 책임 계층으로 구조화 | Obligation | **delegatedTo** `agent-design-review-ddd` | 동상 |
| b8 | 지식 수준 — 운영 수준을 구성하는 메타 수준 분리 | Obligation | **delegatedTo** `agent-design-review-ddd` | 동상 |
| b9 | 플러그형 컴포넌트 — 핵심 추상화와 구현을 플러그인으로 분리 | Obligation | **delegatedTo** `agent-design-review-ddd` | 동상 |

### s042-6.1 (10)

| 블록 | Work label | class | 소유 | 4원 근거 |
|---|---|---|---|---|
| b3 | tests/ 레이아웃은 discipline-tdd 입장 심사 승인 후 적용 | Exception | **enforcedBy** `check-test-config.py` · **delegatedTo** `agent-discipline-reviewer` | ① 문면이 `discipline-tdd` 지정 · ② check-test-config #383/#384(test/ 직계 자식 다섯)가 승인 후 구조를 집행 |
| b3 | 구조 규칙만으로 빈 test 패키지·파일·case 생성 금지 | Prohibition | **enforcedBy** `check-layer-skeleton.py` · **delegatedTo** `agent-discipline-reviewer` | ② check-layer-skeleton #489 «<…> 자리표시자 칸만 그 개념이 생길 때 생긴다» 문면 일치 |
| b4 | domain 계층은 어디에도 의존하지 않는다 | Prohibition | **enforcedBy** `check-domain-model.py` | ② check-domain-model #8 «domain_layer 의 밖으로 나가는 import 0» 문면 일치 |
| b4 | application 계층은 domain에만 의존 | Obligation | **enforcedBy** `check-event-publish.py`, `check-transaction-boundary.py` | ② check-event-publish #7(application_layer import 허용은 넷) + check-transaction-boundary #4(django import 금지) |
| b4 | infrastructure 계층은 domain·application에 의존(인터페이스 구현) | Permission | **enforcedBy** `check-context-isolation.py` | ② check-context-isolation #9 «driven 은 domain·port 만»·#322 |
| b4 | interface 계층은 application에 의존(유스케이스 호출) | Obligation | **enforcedBy** `check-context-isolation.py`, `check-event-publish.py` | ② check-context-isolation #93/#94/#95(driving 잎의 import 폭) + check-event-publish #96 |
| b5 | 프레임워크 제약 시 [A] 간소화 구조 차선 허용(원전 이론) | Permission | **delegatedTo** `agent-design-review-ddd` | 원전 이론 조항 — 채택 판정은 설계 시점 |
| b5 | [A] 간소화 구조를 dddjango 생성 코드에 적용 금지 | Prohibition | **enforcedBy** `check-layer-skeleton.py` | ② check-layer-skeleton #486·#490(트리에 없는 경로 금지)이 생성 코드 배치를 폐쇄 |
| b6 | 생성 코드 표준 파일트리 소유는 discipline-houserules | Obligation | **enforcedBy** `check-layer-skeleton.py` · **delegatedTo** `agent-discipline-reviewer` | ① 문면이 `discipline-houserules` 를 직접 지정 · ② check-layer-skeleton docstring «트리 데이터는 standard_tree.py(정본 140행의 기계 사본) 하나에서 온다» |
| b6 | 생성 코드 배치 권위는 §6.1이 아니라 houserules 문서 | Override | **enforcedBy** `check-layer-skeleton.py` · **delegatedTo** `agent-discipline-reviewer` | 동상 — §6.1 을 이론적 배경으로 강등하는 권위 이양 조항 |

### s043-6.2 (1)

| 블록 | Work label | class | 소유 | 4원 근거 |
|---|---|---|---|---|
| b2 | Django ORM 적용(모델 분리 비용·서비스/셀렉터 경계) 소유는 implementation-django §16 | Obligation | **delegatedTo** `agent-discipline-reviewer` | ① 문면이 `implementation-django` 지정 · 기본값 표(implementation-*→discipline-reviewer) |

첫 문장(ORM→도메인 import 방향)은 s021-3.4/b3 의 same-doc 재진술로 Work 억제·`restates` 로 대체했다(적대 리뷰 M-1 — 위 census 대사 s043-6.2 행).

### s044-6.3 (3)

| 블록 | Work label | class | 소유 | 4원 근거 |
|---|---|---|---|---|
| b2 | Repository는 컬렉션 추상화·UnitOfWork는 트랜잭션 경계 단위 | Obligation | **enforcedBy** `check-transaction-boundary.py`, `check-port-adapter-pairing.py` | ② check-transaction-boundary #282·#283·#597(save/remove 접두) + check-port-adapter-pairing #240(uow 선언은 port/unit_of_work/)·#245(계약 셋) |
| b2 | 도메인·응용은 추상 인터페이스에만 의존·구체 구현은 인프라 | Obligation | **enforcedBy** `check-port-adapter-pairing.py`, `check-context-isolation.py` | ② check-port-adapter-pairing #460(구현 자리)·#476(선언↔구현 1:1) + check-context-isolation #9 |
| b4 | Django 실현(Repository §16.3·UoW transaction.atomic §16.4) 소유는 implementation-django | Obligation | **delegatedTo** `agent-discipline-reviewer` | ① 문면이 `implementation-django` 지정 · 기본값 표(implementation-*→discipline-reviewer) |

### s046-6.5 (2)

| 블록 | Work label | class | 소유 | 4원 근거 |
|---|---|---|---|---|
| b7 | 중간 단계 실패 시 완료 단계의 보상 행동 실행 | Obligation | **delegatedTo** `agent-design-review-ddd` | 27종 전수 실독 — 보상 흐름의 존재·실행을 진단하는 검사기 없음. 초안의 `check-event-publish` #564 는 «진행표 금지 — saga/·process_manager/ 폴더는 ⓓ 후보»로 **극성이 반대**(규범 준수 형태에 발화)라 철회했다(적대 리뷰 M-2 수용) — 위임 기본값(설계 시점) |
| b7 | 보상 트랜잭션은 반드시 멱등 | Obligation | **enforcedBy** `check-missable-entrance.py` · **delegatedTo** `agent-design-review-ddd` | ② check-missable-entrance #181 «멱등성은 유스케이스가 갖는다 … 「두 번 와도 결과가 같나」» — 단 #181 관할은 «놓칠 수 있는 입구(cron_job·webhook·event_subscription)가 부른 유스케이스»라 **보상이 그 입구 뒤에 있을 때 한정한 부분 커버(자인)**, 잔여(오케스트레이터 직접 호출 보상)는 설계 시점 위임(적대 리뷰 L-6 수용) |

### s047-6.6 (2)

| 블록 | Work label | class | 소유 | 4원 근거 |
|---|---|---|---|---|
| b2 | 전술 패턴 만능 금지 — 단순 로직용 패턴도 알아야 한다 | Obligation | **delegatedTo** `agent-design-review-ddd` | 패턴 선택 지식 규범 — 설계 시점 기본값 |
| b3 | 트랜잭션 스크립트는 지원 하위 도메인에 적합 | Permission | **delegatedTo** `agent-design-review-ddd` | «적합하다» 권고형(애매 보수 포함·P0 승계) — 설계 시점 기본값 |

### s048-6.7 (2)

| 블록 | Work label | class | 소유 | 4원 근거 |
|---|---|---|---|---|
| b2 | 마이크로서비스 1개 = BC 1개 · 자체 DB 소유 · API/이벤트 통신 | Obligation | **enforcedBy** `check-context-isolation.py`, `check-db-table.py` · **delegatedTo** `agent-design-review-ddd` | ② check-context-isolation #12·#13(창구는 OHS·published_event) + check-db-table #631(타 BC 모델 FK 금지 = DB 소유 분리) |
| b8 | Shared Kernel 공유 라이브러리는 최소화 필수 | Obligation | **delegatedTo** `agent-design-review-ddd` | 표 셀 «최소화 필수» — 공유 커널 결정은 설계 시점(기본값) |

### s049-6.8 (14)

| 블록 | Work label | class | 소유 | 4원 근거 |
|---|---|---|---|---|
| b1 | 전술·구현 패턴은 도메인 전략을 대신하지 않는다 | Prohibition | **delegatedTo** `agent-design-review-ddd` | 패턴 선택 절차의 선행 조건 — 설계 시점 기본값 |
| b1 | 도메인 모델 확인 후 가장 가벼운 패턴을 순서대로 고른다 | Obligation | **delegatedTo** `agent-design-review-ddd` | 동상 |
| b2 | 절차 1 — BC·애그리거트·불변식·유스케이스·외부 통합 경계 확인 | Obligation | **delegatedTo** `agent-design-review-ddd` | 설계 절차 규범 — 위임 기본값(설계 시점) |
| b2 | 절차 2 — 실제 압력 분류 | Obligation | **delegatedTo** `agent-design-review-ddd` | 동상 |
| b2 | 절차 3 — 현재 압력을 푸는 가장 가벼운 패턴 선택 | Obligation | **delegatedTo** `agent-design-review-ddd` | 동상 |
| b2 | 절차 4 — 미선택 무거운 패턴과 사유 기록 | Obligation | **delegatedTo** `agent-design-review-ddd` | 동상(설계 산출물 기재 의무) |
| b3 | 단순 CRUD·지원 하위 도메인에 무거운 패턴 기본 도입 금지 | Prohibition | **enforcedBy** `check-idempotency-scope-creep.py` · **delegatedTo** `agent-design-review-ddd` | ③ **부분 커버(정직 기록)** — 규범 문면의 열거(리포지토리·커스텀 UoW·CQRS·이벤트 소싱·saga·outbox·ACL)에 멱등성은 없다. check-idempotency-scope-creep 는 «미요청 무거운 산출물의 무단 도입 금지»라는 동일 원리의 **인접 축**만 결정적으로 차단하고, 열거된 7축 자체의 도입 판정은 설계 시점 위임(적대 리뷰 L-4 수용 — «③ P0 커버» 단정을 철회) |
| b4 | Risky Write — 패턴 선택은 이 문서·세부 구현·검증은 소유 영역 이양 | Obligation | **delegatedTo** `agent-design-review-ddd` | 라우팅 선언 — 설계 시점 기본값 |
| b7 | 소유 — 패턴 결정은 이 문서(§5~§6) | Obligation | **delegatedTo** `agent-design-review-ddd` | 소유권 표 행(순수 규범·행 단위 계수) — 설계 시점 기본값 |
| b8 | 소유 — 트랜잭션 owner·부수효과 타이밍은 implementation-django §16 | Obligation | **enforcedBy** `check-transaction-boundary.py` · **delegatedTo** `agent-discipline-reviewer` | ① 문면 `implementation-django` 지정 · ② check-transaction-boundary #200(after_commit)이 타이밍을 집행 |
| b9 | 소유 — 락·격리 수준·인덱스·rollout은 architecture-db | Obligation | **enforcedBy** `check-mechanism-ownership.py` · **delegatedTo** `agent-design-review-db` | ① 문면 `architecture-db` 지정(기본값 이탈 근거) · ② check-mechanism-ownership(DB 엔진 트랜잭션·락 메커니즘 교체 백스톱) |
| b10 | 소유 — 멱등성 저장·Idempotency-Key·status code는 architecture-api | Obligation | **enforcedBy** `check-idempotency-scope-creep.py` · **delegatedTo** `agent-design-review-api` | ① 문면 `architecture-api` 지정(기본값 이탈 근거) · ② 검사기가 미요청 멱등 산출물 도입을 차단해 이 라우팅 행을 배후 집행 — **단 그 docstring 은 소유를 «architecture-db §9.6 Idempotency storage 집행»으로 적어 규범 문면(architecture-api)과 어긋난다**(원문·검사기 간 소유 충돌 — 이관 스코프 밖·아래 §4 자인 ③. 적대 리뷰 L-5 수용) |
| b11 | 소유 — 테스트 후보 입장 결정은 discipline-tdd | Obligation | **delegatedTo** `agent-discipline-reviewer` | ① 문면 `discipline-tdd` 지정 · 기본값 표(discipline-tdd→discipline-reviewer) |
| b12 | 소유 — add된 통합·동시성·멱등성 테스트 mechanics는 implementation-test | Obligation | **enforcedBy** `check-test-config.py` · **delegatedTo** `agent-discipline-reviewer` | ① 문면 `implementation-test` 지정 · ② check-test-config(pytest↔settings 바인딩·test/ 구조) |

### s050-7 (3)

| 블록 | Work label | class | 소유 | 4원 근거 |
|---|---|---|---|---|
| b3 | 복잡한 것을 불변성으로 감싸 복잡성을 낮춘다 | Obligation | **enforcedBy** `check-domain-model.py` · **delegatedTo** `agent-design-review-ddd` | ② check-domain-model #264(값 객체 불변)·#257(루트 경유) — 통찰의 기계 실현 축 |
| b3 | 값 객체의 상태 관련 비즈니스 로직은 자기 경계 안에 둔다 | Obligation | **enforcedBy** `check-domain-model.py` · **delegatedTo** `agent-discipline-reviewer` | ② check-domain-model #264·#265(<A>/value_object/ 는 애그리거트 밖에서 안 쓰인다) |
| b3 | 비즈니스 로직은 불변성을 감싸 자유도를 줄인다 | Obligation | **enforcedBy** `check-domain-model.py` · **delegatedTo** `agent-design-review-ddd` | ② check-domain-model #257(상태 변경은 루트를 지난다) · 자유도 판정은 설계 리뷰 |

### s052-9 (2)

| 블록 | Work label | class | 소유 | 4원 근거 |
|---|---|---|---|---|
| b9(둘째 문장) | 애그리거트 접근·상태 변경은 루트 경유만 | Obligation | **enforcedBy** `check-domain-model.py` · **delegatedTo** `agent-design-review-ddd` | ② check-domain-model #257(상태 변경은 루트를 지난다)·#258(entity 직접 참조 금지 — 애그리거트 밖에서 붙잡는 것은 루트뿐) 문면 일치 · **원본 규범**(restates 대상 s019/b1·b2·b5 어디에도 없고 문서 전수 검색상 산문 진술은 2083행이 유일 — 적대 리뷰 H-1 수용) · 경계 «설정» 판정은 설계 시점 병기 |
| b15 | 핵사고날 — 포트와 어댑터로 내부/외부 분리 | Obligation | **enforcedBy** `check-port-adapter-pairing.py` · **delegatedTo** `agent-design-review-ddd` | 센서스가 §9 핵사고날 행을 «주제 서술이라 사본 아님»으로 판정 — 사본 아님 판정 2행 중 하나. ② check-port-adapter-pairing #457·#460(선언·구현 자리) |

## 3. 재진술 유예 (교차 문서 — spec 미기재, 소급 패스 대상)

판정 절차: 센서스 restate 열(`Y:architecture-ddd-skill/s004` 3절)에서 출발해 `dddjango/skills/architecture-ddd/SKILL.md` §«핵심 운영 원칙»(s004, 17–29행) 10불릿을 **직접 실독**하고, 각 불릿이 자기 문면에 인용한 final 절(§1.2 등)로 대응을 확정했다. 방향은 전건 **final 본문 = 정본 / SKILL 불릿 = 압축 사본**(사본 측이 전문·근거를 갖지 않음).

| # | 사본(상대 문서/절/좌표) | 사본 문면 요지 | 정본(이 문서) |
|---|---|---|---|
| 1 | architecture-ddd-skill/s004 19행 불릿 | 전략 설계가 전술보다 먼저 — 식별→BC→맵→전술 (§1.2, §2) | s004-1.2/b3 · b4 |
| 2 | architecture-ddd-skill/s004 20행 불릿 | 유비쿼터스 언어는 BC 내에서만 유효 (§2.3) | s009-2.3/b3 |
| 3 | architecture-ddd-skill/s004 21행 불릿 | Vernon 4규칙 + BC 경계 ORM FK 금지·같은 BC 허용 (§3.3) | s019/b1 · b3 · b5 · b7 · b8 |
| 4 | architecture-ddd-skill/s004 22행 불릿 | 엔티티는 애그리거트의 일부로만 사용 (§3.2, §8) | s051-8/b3 (파일럿 기이관 정본) |
| 5 | architecture-ddd-skill/s004 23행 불릿 | 도메인 서비스는 무상태·애그리거트는 서비스를 모른다 (§3.5) | s022-3.5/b2 · b4 |
| 6 | architecture-ddd-skill/s004 24행 불릿 | 응용 서비스는 흐름·트랜잭션만·비즈니스 로직 금지 (§3.6) | s023-3.6/b2 · b3 · b4 |
| 7 | architecture-ddd-skill/s004 25행 불릿 | 이벤트 수집 + 디스패치 타이밍 명시 (§3.7) | s024-3.7/b3 |
| 8 | architecture-ddd-skill/s004 26행 불릿 | birth-enum·append-only·버전 태그 리터럴 동결·소비 BC import 금지 (§3.7) | s026/b1 · b2 |
| 9 | architecture-ddd-skill/s004 27행 불릿 | 4계층+DIP — 도메인에 인터페이스·인프라에서 구현 (§5.1, §5.2) | s036-5.1/b3 · s037-5.2/b2 |
| 10 | architecture-ddd-skill/s004 28행 불릿 | 구현 패턴은 필요 확인 시점 선택 + Risky Write 라우팅 (§6.8) | s049-6.8/b1 · b2 · b3 |
| 11 | architecture-ddd-skill/s004 (절 전체) | final §9 핵심 요약과 SKILL 요약의 3중 사본 축 — 센서스가 s052-9 restate 열에 명시 | s052-9 (이미 본문 사본으로 판정·in-spec restates 보유 — 3중 축의 셋째 변) |

유예 건수 **11**. spec `restates` 에는 같은 문서 쌍 35건(보유 블록 25 — 파일럿 s017-3.2/b1 포함)만 실었다(브리프 «다른 문서 상대는 spec 에 넣지 말고 worksheet 에 기록»). 33→35 증가분은 적대 리뷰 반영 2건(M-1 s043-6.2/b2→s021-3.4/b3 · L-7 s016-3.1/b2→s016-3.1/b3)이다.

**유예 후보이나 재진술로 판정하지 않은 것**: s042-6.1/b6·s025/b5·s049-6.8 표 6행의 `discipline-houserules`·`architecture-db`·`architecture-api`·`implementation-*` 지목은 **소유권 이양(handoff)**이지 같은 규범의 사본이 아니다 — 상대 문서에 같은 문장이 없고, 이쪽 문면은 «누가 소유하는가»만 진술한다. 따라서 유예 목록에 넣지 않고 `delegatedTo` 배선으로만 처리했다.

## 4. 경계 판단 메모

- **블록 자연 단위**: 문단(빈 줄 구분)·펜스 전체·표 행 하나를 단위로 잡고, 블록 간 구분자(빈 줄)는 §13 대로 **선행 블록 후행 스팬**에 귀속시켰다. 절 선두 빈 줄만 첫 블록 선두에 붙였다(§13 유일 예외). 파일럿 s017-3.2 의 b4=[548,581]·b6=[584,631](닫는 펜스 다음 빈 줄 포함)이 같은 규약의 실물이라 그대로 따랐다. 도구의 «헤딩+블록 연결 == 절 스팬» 단언이 36절 전건 통과 — 무손실 실증.
- **kind 는 운반체이지 규범 유무가 아니다**: 규범을 실은 표 행은 `table-row`, 규범 주석을 실은 펜스는 `code` 를 유지했다(파일럿 s051-8 의사결정 표 행이 `table-row`+norms 인 판형과 동형). 발주 36절의 규범 보유 블록 87 중 `table-row` 17 · `code` 1 · `norm` 69. §16 datatype 규약(code/table-row=xsd:string)과 정합.
- **펜스 안 규범의 채택 경계**: 원칙은 «예제 코드는 규범 계수 밖»(센서스 §3 E03 정정)이다. 예외로 승격한 것은 s023-3.6/b5 의 주석 2건뿐 — 그 주석은 예제 동작 설명이 아니라 `#635`·`#484` 를 명시 인용한 **현행 표준 선언**(«두 어휘를 섞지 말 것»)이고 센서스도 P0 규약 ③ 으로 계수했다. 반대로 s021-3.4 펜스의 «별도 리포지토리는 만들지 않는다», s042-6.1 트리 펜스의 `tests/` 주석, s024-3.7/b4 의 `uow.after_commit` 주석은 본문에 동일 규칙이 이미 있어 제외(센서스 판정 승계).
- **의사결정 blockquote 의 방향**: §8 표가 의사결정 **레지스트리**이고 본문 blockquote 는 «[의사결정 #N] External 채택» 형태로 그 레지스트리를 **인용**한다 — 그래서 §8 이 정본이다. 파일럿이 [의사결정 #1]에 이미 이 방향으로 판정했으므로(s017-3.2/b1 → s051-8/b3) 나머지 7건 전부 동형 처리했다. 방향을 뒤집으면 파일럿과 충돌한다.
- **§9 핵심 요약의 방향**: §8 과 달리 §9 는 레지스트리가 아니라 본문의 **압축**이다(근거·예외·인용이 전부 본문에만 있다). 그래서 본문이 정본, §9 행이 사본이다. 유일 예외인 핵사고날 행은 센서스 자신이 s038-5.3 note 에서 «주제 서술이라 사본 아님»으로 판정했으므로 그 행만 Work 를 줬다.
- **«조건절»의 class 선택**: «~을 선택하는 조건» 불릿군은 `Permission`(조건 충족 시 채택 허용), «회피하는 조건» 불릿군은 `Exception`(채택 규범의 배제 조건)으로 통일했다(ACL·핵사고날·CQRS·Outbox 4곳). 파일럿의 «선택적 적용=Permission»(adv 중재 L-E) 판정을 조건절로 확장한 것이다.
- **`Override` 를 쓴 3건**: 원전 이론을 dddjango 내부 정본이 덮는 자리에만 썼다 — s019/b10 「한 트랜잭션 = 애그리거트 하나」(원전 «복수 애그리거트 수정 용인»을 덮음), s024-3.7/b3 `uow.after_commit` 한 경로(«커밋 직전 디스패치» 배경 이론을 덮음), s042-6.1/b6 배치 권위의 houserules 이양. 파일럿이 [의사결정 #6]에 Override 를 쓴 판정과 같은 자([외부 이론 vs 내부 정본])다. 나머지 «단, ~» 단서 문장은 Exception 으로 뒀다.
- **기본값 도피 방지(§16 역방향 검증)**: 초안에서 위임 기본값으로 두려던 규범 중 27종 docstring 재대조로 검사기를 찾아 배선을 옮긴 것 — §2.3 «업무 용어로 구성»→`check-naming`(#28·#36·#43), §2.3 «BC 경계 안에서만 유효»→`check-business-vocabulary`(#47·#52), §3.7 birth-enum 파생 표기·`.value` 평탄화→`check-choices-literal-consumption`(docstring 회피 5 문면 일치), §3.7 OHS discriminator 비대상→`check-context-isolation` #472, §6.8 소유 표 3행→`check-mechanism-ownership`·`check-idempotency-scope-creep`·`check-test-config`. 반대로 «기본값 이탈»에 문면 근거를 붙인 것 — §2.5 published language→`agent-design-review-api`, §3.7 Outbox 전달 메커니즘→`agent-design-review-db`(둘 다 문면이 상대 문서를 직접 지목).
- **«인용=규칙»(P0 규약 ②)의 적용 조건 — 명령형 인용 한정**: 승격한 인용 3건은 전부 명령형이다 — s019/b4 Vernon «…로 제한하라», s021-3.4/b3 Cosmic Python «…하게 하라. …하면 안 된다», s039-5.4/b2 Greg Young «…취급하고, …적용하라». 반면 s007-2.1/b3 Evans «코드 아래에 있는 모델을 리팩터링한다»(45행)와 s010-2.4/b3 [B] «하위 도메인은 발견하고, 바운디드 컨텍스트는 설계한다»(219행)는 **서술형**이고, 후자는 «~는 점을 가장 강조»라는 서술틀 안에 놓여 화자의 태도를 보고하는 문장이다. 두 건은 규약 ② 대상이 아니라고 판정해 비승격했다(센서스 계수와 일치 — 적대 리뷰 L-8·L-10 은 «비일관 적용»으로 봤으나 명령/서술 축으로 갈린다고 판단해 승격은 하지 않고 사유만 남긴다). 같은 자로 s038-5.3/b2 «[C]는 …권장한다»(1495행)도 원전의 권고를 보고하는 서술이라 비계수했다 — 이 문서 자신의 태도는 b3 선택 조건 4·b4 회피 조건 3 이 소유한다(적대 리뷰 L-9 동상).
- **§9 요약 행의 «억제»와 «규범 아님»은 다른 판정이다**(적대 리뷰 L-1 수용): 억제 원장의 판정 열을 신설했다. s052-9/b5(컨텍스트 맵)·b6(증류)·b3(BC)의 restates 대상은 Work 0 인 정의 prose 라 «본문 정본의 사본»이라는 서사가 성립하지 않는다 — 실제 판정은 «행이 규범이 아님(정의·격언 서술)»이고, 센서스의 행 단위 계수를 반박하는 쪽이다. restates 에지 자체는 텍스트 사본 관계로서 유지했다(§9 행이 §2.5·§2.6·§2.4 정의문의 압축인 것은 사실). 역으로 b9 는 사본 서사가 부분적으로만 맞아 Work 1 + restates 3 이 됐다(H-1).
- **검사기 문면과 본문이 어긋나는 자리(배선 시 자인)**: ① §4.3 «단언» 은 사후 조건·불변식의 명시 선언을 요구하지만 `check-public-surface-annotation` #69 는 프로덕션 `assert` 를 ⓓ 후보로 낸다 — 문서가 요구하는 것은 «불변식 선언»이지 `assert` 문법이 아니라고 읽고 `check-domain-model` #268(생성자 raise 축)으로 배선했다. ② §5.2 는 «인터페이스는 고수준(도메인) 영역» 이라 하지만 dddjango 표준 트리의 포트 자리는 `application_layer/port/` 다(`check-port-adapter-pairing` #457·#313). 원전 문면이 아니라 실집행 자리를 근거로 배선하고, 표기 차이를 여기 남긴다. ③ §6.8 소유권 표 «멱등성 저장·`Idempotency-Key`·status code → `architecture-api`»(2014행)와 배선한 `check-idempotency-scope-creep` docstring 선두 «architecture-db §9.6 Idempotency storage 집행»이 **다른 소유자를 명시한다** — 원문·검사기 간 소유 충돌이고 이관 스코프 밖이라 고치지 않되, 배선 근거를 «짝»에서 «배후 집행 + 불일치 자인»으로 낮춰 적었다(적대 리뷰 L-5 수용).
- **절 Work 0 사례**: s035-5(§5 서두)는 블록이 [의사결정 #5] blockquote 하나뿐이라 Work 0 · restates 1 이 된다. Section·Block 노드는 그대로 서고 규범 소유만 §8 로 간다 — 셰이프상 문제 없음을 도구 exit 0 로 확인.
- **드리프트 처리**: 발주서가 «현재 2124행(센서스 2122행에서 드리프트)» 을 경고했다. 실측 원인은 파일 변경이 아니라 파일럿 이관이 삽입한 `graph-owned` 마커 2행(현재 540·2060행)이었다. `ontology_migrate.py` 가 좌표 해석 전에 마커 라인을 제거해 «복원 원문» 위에서 절 해시를 대조하므로, spec 행 번호는 **센서스 좌표(마커 제거본 1-indexed)** 가 정답이다 — 마커 제거본에서 전 헤딩을 재확인했고 36절 전건이 센서스 좌표·sha256 대조를 통과했다(도구 단언).

## 5. 자기 검증 로그

```
PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_migrate.py \
  workspace/eval/t3/specs/architecture-ddd-final.spec.json
→ 38절(파일럿 2 + 발주 36) · 블록 236 · Work 216 · 신규 채번 188 · 재사용 28 소진 · exit 0
```

- `--write` 미사용(브리프 금지 조항).
- 추가 자체 점검(도구 미검사 항목): spec 내 `restates` 35건 전건이 실재 블록 좌표로 해소 · Work label 188건 중복 0 · 전 규범 `basis` 비어 있지 않음 · 파일럿 2절이 원본 spec 과 바이트 동일.
- **적대 리뷰 반영 후 재검증**(2026-08-22): 같은 명령 exit 0 재확인 — 블록 236·Work 216(신규 188·재사용 28) 불변. 발주 36절 실측 재집계: 소유 45/50/93 · class Obligation 117·Permission 27·Prohibition 25·Exception 16·Override 3 · restates 35. 처분 내역은 `workspace/eval/t3/reviews/architecture-ddd-final-findings.md` §처분.
