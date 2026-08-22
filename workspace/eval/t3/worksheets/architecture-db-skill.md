# T3 이관 검수표 — architecture-db-skill

- 원문: `dddjango/skills/architecture-db/SKILL.md` (47행 · 센서스 일치 · 마커 0 — 미이관 문서)
- spec: `workspace/eval/t3/specs/architecture-db-skill.spec.json`
- 자기 검증: `PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_migrate.py workspace/eval/t3/specs/architecture-db-skill.spec.json` → **exit 0** (블록 32 · Work 23 · `--write` 미사용 · 수리 루프 0회)
- 배선 준거: `check-*.py` **27종 docstring 선두 전수 실독**(§16 L-F 의무 · arch-skills 묶음 1회) 후 저작. 요약-복제 상대인 `architecture-db-final` 기이관 spec 의 정본 배선을 대조했다. **정본과 갈린 자리 1건**(24행 W1 의 D — §4 기록).
- W3 적대 리뷰 수리 반영(2026-08-22): F4(24행 basis 를 «b14 부분 승계»로 정정 + §4 갈림 기록) · F5(20행 basis 의 §7.2·§7.3 인용을 NAR 로 정정) · F6(분해 규율 우선순위 명문화) · F8(대사 사유 분리 서술) — 상세는 `workspace/eval/t3/reviews/w3-arch-skills-findings.md` «처분» 절.

## 1. census 대사 (절별 규범 수)

| 절 | 헤딩 | 발주서(센서스) | spec | 차 | 판정·사유 |
|---|---|---|---|---|---|
| s001 | (전문) | 2 | 2 | 0 | 일치 — `description` 2문(로드 조건 / 경계 위임). `name`·`user-invocable`·종결 `---` 은 메타라 prose |
| s003 | 언제 쓰나 | 4 | 4 | 0 | 일치 — 로드 조건 1 + 위임 경계 불릿 3 |
| s004 | 핵심 운영 원칙 | 10 | 15 | **+5** | **⑴ 불릿 단위 센서스의 미해상(과소) + ⑵ 규약 내 하위 문장(독립 종결절) 분해** — 두 사유를 분리해 적는다. ⑴ 센서스는 7 불릿에 10을 배분했다(불릿 해상도 — 불릿 내부 재계수 없음). ⑵ 그 위에 spec 은 «독립 종결절» 규율로 19행 2(순서 준수 §5 / 역정규화 최후 수단 §4 — 문면이 두 §를 명시 귀속) · 20행 2(구성 규율 / 액세스 패턴 기반 결정) · 21행 2(제약조건 보호 §8 / rollout 순서 §11) · 23행 3(항목 명시 / test criteria 비의무 Exception / add 한정 작성) · 24행 3(트랜잭션 내부 실행 금지 Prohibition / Outbox at-least-once / consumer 중복 무시) · 25행 2로 나눴다. 22행만 1(콜론 뒤 격리 수준 매핑은 선택지 조각). 분해가 `architecture-db-final` 의 Work 분해(§4.2·§7.4·§8·§9.4·§9.6·§9.7·§11)와 맞물리므로 **spec 이 옳다** |
| s005 | 상세 레퍼런스 | 2 | 2 | 0 | 일치 — 29행 라우팅 준거 1 + 47행 한정 독해 1. 표 15행(머리·구분 포함)은 매핑이라 미계수(P0 승계) |
| **계** | | **18** | **23** | **+5** | 불일치 1절 — 사유는 ⑴ 불릿 해상도 과소 + ⑵ 규약 내 하위 문장 분해의 합산 · 과대 산정 판정 0 |

**병합 단계 승계 요청(F8)** — «독립 종결절» 규율은 §13 «Work 채번 단위 = 문장»의 저작자 확장이다(이 문서는 23·24행이 한 문장 → 3 Work). 정본 final 분해와 맞물려 방어되나 동결 센서스(REF 539절·3,235문장) 분모 대비 무비준 확산 시 기대표 드리프트가 누적된다. 병합 단계에서 ⓐ 규율의 T3 공통 비준(§13 부기 또는 `T3-EXECUTION.md` 기록) ⓑ 기대표 diff 사유에 **arch-skills 3문서 +23(ddd +9 · db +5 · api +9)** 내역 승계를 할 것. 저작 계약 «금지» 조항상 이 에이전트는 `ontology-authoring.md`·`T3-EXECUTION.md` 를 쓰지 않는다.

**문장 분해 규율(이 묶음 3문서 공통 · 명문화)** — §13 «Work 채번 단위가 문장»을 적용할 때 단위는 **독립 종결절**이다. 다음 넷 중 하나면 한 문장 안이라도 분리 채번했다: ⑴ **행위 대상(주어·목적)이 다름** ⑵ **규범 유형(class)이 갈림** ⑶ **문면이 서로 다른 § 또는 규칙 번호를 명시 귀속** ⑷ **문면이 스스로 규칙 수를 선언**. 반대로 다음은 병합했다: 같은 축의 **부정면 재진술**, **근거·결과 서술**, **열거 조각**(콜론 뒤 명사구 나열·항목명), **같은 결정 대상의 기록 의무**. 이 규율은 arch-skills 3문서에 동일하게 적용했다.

**트리거 충돌의 우선순위(F6 수리 — 3문서 공통 명문화)** — ⑵(class 갈림 → 분리)와 «부정면 재진술»(→ 병합)이 한 문장에 동시에 걸릴 때는 **긍정절의 배타 표지(«만»·«한정»·«…뿐») 유무**로 가른다. 배타 표지가 있으면 부정절의 금지 대상이 이미 배제돼 독자 위반 표면이 없으므로 **병합**(실물: ddd 24행 «흐름 제어와 트랜잭션 관리**만** 담당하고, 비즈니스 로직을 두지 않는다» → 1 Work), 없으면 부정절이 독자 금지 대상·독자 위반 표면을 가지므로 **⑵ 우선 분리**(실물: api 22행 «명사·복수형·케밥케이스로 설계하고 동사 행위를 포함하지 않는다» → `/orders/{id}/cancel` 이 세 속성을 지키면서 동사를 포함하므로 2 Work). 이 문서에는 두 트리거가 동시에 걸린 자리가 없다(22행 격리 수준은 금지 단독, 24행은 세 행위 대상이 갈리는 ⑴ 사유).

이 문서에서 병합한 자리 2건(과대 방지 실증): ⑴ 22행 «격리 수준은 필요 이상으로 높이지 않는다: 대부분의 OLTP 는 Read Committed, …» — 콜론 뒤는 **선택지 매핑 조각**이라 분리하지 않고 금지 1 Work. ⑵ 23행의 항목 열거(Transaction owner·Locking strategy·Idempotency storage·Side-effect timing·Isolation/retry)는 **명시 대상 조각**이라 «명시한다» 1 Work 로 묶었다(final §9.6 은 표 행마다 Work 를 냈지만 SKILL 은 한 문장에 접혀 있다 — 소급 패스에서 1:다 재진술로 연결).

## 2. 배선 근거 표 (전 규범 23건)

> `enforcedBy` 는 «담당 검사기의 문면·docstring 근거가 실재하는가»로만 달았고, 없으면 §16 위임 기본값 표를 따랐다(기본값 이탈·기본값 도피 양쪽 다 근거 병기). 근거 기호 ①문면 역할명 ②docstring § 인용 ③P0 커버 ④registry #N.
>
> **표는 spec JSON 에서 기계 생성한다**(라벨·class·enforcedBy·delegatedTo·basis 전 열이 spec 실물의 사본 — agent-coder 검수표 R2-3 재발 방지 조치 승계). spec 을 고치면 이 표를 다시 생성한다.

| # | 절/블록(행) | Work label | class | enforcedBy | delegatedTo | 4원 근거 |
|---|---|---|---|---|---|---|
| 1 | s001/b2 (3) | 로드 조건 — 데이터 신뢰성·인덱스 전략·트랜잭션 경계·outbox 전달 보장·스키마 rollout 결정 시 선행 로드 | Obligation | — | `command-dddjango`·`agent-design-review-db` | ①문면 «…결정할 때 먼저 로드한다» + 센서스 E08 s001 비고 «frontmatter = 라우터 트리거» · ②check-*.py 27종 docstring 선두 전수 실독 — 스킬 로드·라우팅 술어 0 · §16 위임 기본값 표(architecture-db→agent-design-review-db) + 스킬 배분 소유 Coordinator 병기(agent-coder s004 «작업 축별 스킬 선택 사용» 선례) |
| 2 | s001/b2 (3) | 경계 위임 — Django ORM·마이그레이션 코드 구현과 도메인 이벤트 채택 여부의 타 스킬 이양 | Obligation | — | `agent-discipline-reviewer`·`agent-design-review-ddd` | ①문면이 implementation-django·architecture-ddd 를 수임처로 직접 지목 — §16 표의 수임 문서군 기본값 병기(implementation-*→discipline-reviewer · architecture-ddd→design-review-ddd) · ②27종 docstring 에 스킬 간 위임 술어 0. [센서스 codex DIFF 비고: codex 판 description 에 미치환 구명 architecture-ddd 지시 — 이 코퍼스 정본은 현재 문면] |
| 3 | s003/b1 (10–12) | 로드 조건 — 관계형 DB 아키텍처 결정(모델링·인덱스·제약조건·격리·락·멱등성 저장소·outbox 전달·rollout) 필요 시 로드 | Obligation | — | `command-dddjango`·`agent-design-review-db` | ①문면 «…필요할 때 로드한다» — s001 description 의 정본 진술(사본 = s001/b2) · ②27종 전수 — 스킬 로드 술어 0 · §16 기본값 + 스킬 배분 Coordinator 병기(s001/b2 와 동일 처분) |
| 4 | s003/b2 (13) | Django ORM·마이그레이션 코드 작성의 implementation-django 위임 | Obligation | — | `agent-discipline-reviewer` | ①문면이 화살표로 수임처를 직접 지목 · §16 표 implementation-*→agent-discipline-reviewer(기본값 일치) · ②27종 전수 — 스킬 경계 술어 0(check-mechanism-ownership ⑵ 는 migrations «파일» 규율이라 스킬 관할 배분과 다른 판) |
| 5 | s003/b3 (14) | 도메인 이벤트 채택 여부·애그리거트 경계의 architecture-ddd 위임 | Obligation | — | `agent-design-review-ddd` | ①문면이 architecture-ddd 를 수임처로 직접 지목 · §16 표 architecture-ddd→agent-design-review-ddd(설계 시점) · ②27종 전수 — 위임 술어 0 |
| 6 | s003/b4 (15–16) | REST 계약·API 멱등성 키 정책의 architecture-api 위임 | Obligation | — | `agent-design-review-api` | ①문면이 architecture-api 를 수임처로 직접 지목 · §16 표 architecture-api→agent-design-review-api · ②check-idempotency-scope-creep 은 «미요청 멱등성 채택 금지»(G0) 축이라 «키 정책 관할 배분»은 비커버(final api s021-5.1/b6 basis 와 동일 논거) |
| 7 | s004/b1 (18–19) | 성능 최적화 순서 준수 — 슬로우 쿼리 최적화→인덱스 적용→캐시→역정규화 | Obligation | — | `agent-design-review-db` | ①문면 역할명 0 · ②27종 docstring 선두 전수 실독 — 쿼리 성능·최적화 순서 술어 0(검사기는 구조·배치·계약만 본다) · ③④ 지목 0 → §16 위임 기본값 표(architecture-db→agent-design-review-db · final s021-5 계열 배선과 동일) |
| 8 | s004/b1 (18–19) | 역정규화의 최후 수단 한정 — 정규화 선행 후 필요한 경우에만 적용 | Obligation | — | `agent-design-review-db` | final s019-4.2/b1 «정규화 먼저 · 필요한 경우에만 역정규화» 와 동형 규범 · ②27종 전수 — 정규형 판정 술어 0 → §16 기본값 |
| 9 | s004/b2 (20) | 인덱스 구성 규율 — 복합(선택도 높은 컬럼 우선)·커버링(Index-Only Scan)·부분(쓰기 비용 최소화) | Obligation | — | `agent-design-review-db` | ①문면 역할명 0 · ②27종 전수 — 인덱스 컬럼 순서·커버링 술어 0 · §16 기본값(final s028-7.1/b3 배선과 동일 — 전건 기본값). 준거 정정: 커버링(§7.2)·부분(§7.3)에 대응하는 final 절은 **NAR(대응 Work 부재 — 센서스가 규범 0으로 판정)**이라 승계할 배선이 없다(§3 유예 #3 과 정합) |
| 10 | s004/b2 (20) | 인덱스 설계의 실제 액세스 패턴 기반 결정 | Obligation | — | `agent-design-review-db` | 동상 — final s031-7.4/b4 «읽기/쓰기 비율에 따른 인덱스 증감 결정»·b6(도입 전 벤치마크)와 같은 결정 근거 축 · 검사 공백 → 기본값 |
| 11 | s004/b3 (21) | DB 경계 불변식의 제약조건 보호 — unique·FK·check constraint | Obligation | — | `agent-design-review-db` | ①문면 역할명 0 · ②27종 전수 — DB 제약조건 선언 술어 0(check-db-table 은 앱 규율·#630 db_table 값·#631 타 BC FK 축이라 «불변식을 제약조건으로 보호하는가»는 비커버) · §16 기본값(final s032-8/b1 배선과 동일) |
| 12 | s004/b3 (21) | 제약조건 rollout 의 lock risk 고려 단계적 순서 | Obligation | — | `agent-design-review-db` | 동상 — final s036-8.4·s054-11.3(제약조건 rollout·lock risk) 축 · 검사 공백 → 기본값 |
| 13 | s004/b4 (22) | 격리 수준의 필요 이상 상향 금지 | Prohibition | — | `agent-design-review-db` | ①문면 «높이지 않는다» = 금지형 · ②27종 전수 — 격리 수준 설정 술어 0(check-mechanism-ownership ⑴ 은 «커스텀 DB 백엔드로 메커니즘 교체» 형태만 차단하고 격리 «수준 선택»은 비커버) · §16 기본값(final s041-9.4/b6 Prohibition 과 동형) |
| 14 | s004/b5 (23) | Risky Write 의 Consistency Block 항목 명시 — transaction owner·locking·idempotency storage·side-effect timing·isolation/retry·test criteria | Obligation | `check-idempotency-scope-creep.py`·`check-transaction-boundary.py` | `agent-design-review-db` | ②check-idempotency-scope-creep docstring 선두 «architecture-db §9.6 Idempotency storage 집행» 직접 지목(커버 범위는 «G1 승인 없는 미요청 멱등성 산출물» 1종) + check-transaction-boundary #200(커밋 뒤 부작용은 after_commit — side-effect timing 축) · «명시» 행위 자체와 나머지 항목(transaction owner·locking·isolation/retry)은 검사 공백 → §16 기본값 병기(final s043-9.6/b1·b7·b9 배선 종합) |
| 15 | s004/b5 (23) | Test criteria 의 테스트 의무 부인 — 위험·failure 후보 기록에 한정 | Exception | — | `agent-discipline-reviewer` | ①문면이 discipline-tdd 입장 결정을 지목 → §16 표(discipline-tdd→agent-discipline-reviewer) · final s043-9.6/b11 Exception 과 동형 · ②27종 전수 — 입장 표 술어 0 |
| 16 | s004/b5 (23) | 입장 결정이 add 일 때만 coder 의 신규 테스트 작성 | Obligation | — | `agent-discipline-reviewer` | ①문면이 «독자 DB failure 와 기존 보호 비교»·«discipline-tdd 입장 결정»·«coder» 를 지목 — 입장 표 판정 소유는 discipline-reviewer(s005 영구 테스트 입장 감사) · §16 표(discipline-tdd→discipline-reviewer) · final s043-9.6/b12 배선과 동일 |
| 17 | s004/b6 (24) | 외부 결제·알림·메시지 발행의 DB 트랜잭션 내부 실행 금지 | Prohibition | `check-transaction-boundary.py` | `agent-design-review-db` | ②check-transaction-boundary #200 «커밋 뒤 부작용은 unit_of_work.after_commit — 응용이 transaction.on_commit·connection.in_atomic_block 직접 호출이면 위반»·#4(application_layer 의 django import 0) · final s043-9.6/b14 배선의 **부분 승계**(정본 b14 실물 = E:[check-transaction-boundary, check-usecase-dto-placement, check-broker-contract]·D:[agent-discipline-reviewer]). 갈린 이유: 정본 b14 는 «트랜잭션 밖 handoff + 유실 불허 시 Outbox»를 한 Work 로 지지만 SKILL 24행은 두 문장으로 갈려 Outbox 축(#603·#532)은 같은 블록의 별도 Work(#18)가 check-broker-contract 로 따로 지고, check-usecase-dto-placement #541 은 «발행» 자리 규율이라 이 Work(«외부 부수효과의 실행 위치») 축 밖이다 · D 는 정본의 discipline-reviewer 대신 §16 문서군 기본값(architecture-db→agent-design-review-db) 유지(§4 기록) |
| 18 | s004/b6 (24) | 메시지 유실 불허 시 트랜잭셔널 Outbox 의 at-least-once 전달 보장 | Obligation | `check-broker-contract.py` | `agent-design-review-db` | ②check-broker-contract #603 ⑴outbox(«선언 유무»만 잰다)·#532 «external 계약은 at-least-once 를 «요구로» 적는다» · 실제 전달 보장 «동작»은 검사 공백(선언 존재만 집행) → 기본값 병기(final s044-9.7/b2·b5·b6 배선 준거) |
| 19 | s004/b6 (24) | consumer 의 중복 수신 무시 가능성 | Obligation | `check-missable-entrance.py` | `agent-discipline-reviewer` | ②check-missable-entrance #181 «멱등성은 유스케이스가 갖는다» — check-broker-contract docstring 이 «멱등 물음의 소유자는 #181» 로 명시 위임(#532 절) · 확정/후보 혼합이라 잔여 의미 축은 구현 리뷰(final s044-9.7/b7 배선과 동일) |
| 20 | s004/b7 (25–26) | 운영 스키마 변경의 Expand / Backfill / Contract 단계 준수 | Obligation | — | `agent-design-review-db` | ①문면 역할명 0 · ②27종 전수 — 마이그레이션 «단계 순서» 술어 0(check-mechanism-ownership ⑵ #336~#338·#593 은 마이그레이션 파일 자리·모양 규율) · §16 기본값(final s051-11/b1·s052-11.1/b1 배선과 동일) |
| 21 | s004/b7 (25–26) | 대용량 backfill 의 슬롯·lock risk 고려 배치 처리 계획 | Obligation | — | `agent-design-review-db` | 동상 — final s053-11.2(Backfill 위험)·s054-11.3(lock risk) 축 · 검사 공백 → 기본값 |
| 22 | s005/b1 (28–30) | 주제별 라우팅 준거 — references/final.md 해당 절 준수 | Obligation | — | `command-dddjango`·`agent-design-review-db` | ①문면 «해당 절을 따른다» — 준거 문서 로드·인용 축 · ②27종 docstring 에 문서 로드·인용 술어 0 · §16 기본값 + 로드 절차 소유 Coordinator 병기(agent-design-architect s005 선례) |
| 23 | s005/b17 (47) | 필요 항목 한정 독해 — 전체 로드 불필요 | Exception | — | `command-dddjango`·`agent-design-review-db` | ①문면 괄호 «(전체 로드 불필요)» = 전량 로드 의무의 면제 조문이라 Exception(agent-design-review-api s003 판례) · ②27종 docstring 에 로드 범위 술어 0 · §16 기본값 + 로드 절차 Coordinator 병기 |

## 3. 재진술

### 3.1 같은 문서 안 쌍 — spec `restates` 에 반영(유예 아님)

| 사본 블록 | 정본 블록 | 판정 |
|---|---|---|
| s001/b2 (3행 `description`) | s003/b1(10–12) · b2(13) · b3(14) | 센서스 s001 restate 열 «Y:architecture-db-skill/s003» 의 실물. §15 대로 **사본(frontmatter) → 정본(본문 절)** 단일 방향. 부분 재진술이라 양쪽 Work 유지. **s003/b4(15–16 `architecture-api` 위임)는 연결하지 않았다** — description 에 대응 문면이 없어(수임처 2종만 열거) 사본 관계가 성립하지 않는다 |

### 3.2 교차 문서 유예 (T3-EXECUTION «교차 문서 쌍 전량 유예» 결정 — 소급 패스 재료)

좌표는 **마커 제거본(센서스) 기준**이다(`architecture-db-final` 은 기이관 문서라 현재 파일에는 마커가 삽입돼 있다).

| # | 사본(이 문서) | Work | 상대 정본(센서스 좌표) | 비고 |
|---|---|---|---|---|
| 1 | s004/b1 (19) | 성능 최적화 순서 준수 | `architecture-db-final` s021-5/b1 (170–172) | |
| 2 | s004/b1 (19) | 역정규화 최후 수단 한정 | 동 s019-4.2/b1 (152–154) | 정본 b1 은 Obligation+Prohibition 2 Work — SKILL 은 한 문장이라 1:2 부분 재진술 |
| 3 | s004/b2 (20) | 인덱스 구성 규율(복합·커버링·부분) | 동 s028-7.1/b3 (231–232 — 복합 컬럼 순서) | **커버링(§7.2)·부분(§7.3)은 상대 Work 부재** — 센서스가 두 절을 NAR(규범 0)로 판정했고 `architecture-db-final` spec 실물에도 두 절이 없다(F5 대조 확인). 소급 패스에서 «SKILL 고유 지시력»으로 남길지 판단 필요. spec basis 도 이 NAR 사실에 맞춰 정정했다(수리 전 «s029-7.2·s030-7.3 계열 배선과 동일» 문구 = 부재 대상 인용) |
| 4 | s004/b2 (20) | 인덱스 설계의 액세스 패턴 기반 결정 | 동 s031-7.4/b4 (268) · b6 (270–271) | |
| 5 | s004/b3 (21) | DB 경계 불변식의 제약조건 보호 | 동 s032-8/b1 (277–279) | |
| 6 | s004/b3 (21) | 제약조건 rollout 의 단계적 순서 | 동 s036-8.4/b1 (324–326) · s054-11.3/b5~b8 (541–545) | |
| 7 | s004/b4 (22) | 격리 수준 상향 금지 | 동 s041-9.4/b6 (371–372) | class 도 Prohibition 으로 일치 |
| 8 | s004/b5 (23) | Risky Write Consistency Block 항목 명시 | 동 s043-9.6/b1 (394–396) + 항목 행 b4·b5·b7·b9·b10 (399–405) | 1:다 — SKILL 한 문장이 정본 표의 여러 행을 접었다 |
| 9 | s004/b5 (23) | Test criteria 의 테스트 의무 부인 | 동 s043-9.6/b11 (406–407) | class Exception 일치 |
| 10 | s004/b5 (23) | add 일 때만 신규 테스트 작성 | 동 s043-9.6/b12 (408–409) | |
| 11 | s004/b6 (24) | 외부 부수효과의 트랜잭션 내부 실행 금지 | 동 s043-9.6/b14 (412–413) · s044-9.7/b1 (417–419) | |
| 12 | s004/b6 (24) | Outbox at-least-once 보장 | 동 s044-9.7/b2 (420–421) · b5 (424) · b6 (425) | |
| 13 | s004/b6 (24) | consumer 의 중복 수신 무시 | 동 s044-9.7/b7 (426) | |
| 14 | s004/b7 (25) | Expand/Backfill/Contract 단계 준수 | 동 s051-11/b1 (509–511) · s052-11.1/b1 (513–515) | |
| 15 | s004/b7 (25) | 대용량 backfill 배치 처리 계획 | 동 s053-11.2/b2 (528) · b3 (529) | |

**유예 15건.** 상대는 전부 웨이브 2 기이관분(`architecture-db-final`)이라 소급 연결이 기술적으로 가능하다.

비-재진술로 판정한 것: s001/b2·s003/b2~b4 의 «→ `implementation-django` / `architecture-ddd` / `architecture-api`» 는 **관할 지시(준거 포인터)** 지 규범 사본이 아니다. 특히 s003/b4(«REST 계약·API 멱등성 키 정책 → architecture-api»)는 `architecture-db-final` s043-9.6/b8(«Idempotency-Key replay/conflict 계약을 architecture-api 와 정합»)과 **같은 관할 배분의 두 진술**이지만, 한쪽은 «위임하라», 다른 쪽은 «정합시켜라»로 행위가 갈려 사본이 아니다 — 소급 패스가 다시 볼 수 있게 여기 남긴다.

## 4. 경계 판단 메모

- **블록 경계 규약**: 후행 빈 줄은 선행 블록 귀속, 절 첫 블록만 헤딩 직후 빈 줄을 흡수(§13). s005 의 마지막 데이터 행은 후행 빈 줄(46)을 물어 [45,46]이고, 47행 «필요한 항목만 읽는다»가 독립 norm 블록이다. 도구가 byte 등가·무손실을 단언했고 **exit 0**(수리 루프 0회).
- **s001 헤딩 = 1행 `---`** · frontmatter 는 code 가 아니라 행 단위 prose/norm(웨이브 2 판례). 규범을 지는 것은 `description`(3행) 하나다.
- **kind 판정**: 코드 펜스 0 · 체크박스 0 — norm/prose/table-row 3종. s005 라우팅 표는 머리·구분행 포함 행 단위 `table-row` 이고 데이터 13행은 규범 미계수(P0 승계).
- **class 판정**: `Prohibition` 2곳(22행 격리 수준 상향 금지 · 24행 트랜잭션 내부 실행 금지 — 둘 다 정본 class 와 일치). `Exception` 2곳(23행 «Test criteria 자체는 테스트 의무가 아니며» = 의무 부인 조문 · 47행 «(전체 로드 불필요)» = 면제 조문). 나머지 Obligation. **Override 0** — 이 문서에는 다른 규범을 눌러 이기는 문면이 없다.
- **기본값이 지배적인 이유(정직 기록)**: 15 Work 중 10건이 `agent-design-review-db` 단독이다. 27종 docstring 전수 실독 결과 **정규화·인덱스·격리 수준·rollout 단계에는 검사기 술어가 하나도 없다** — 검사기 로스터는 파일트리·import 방향·오류 계약·테스트 구조 축에 몰려 있고 DB 스키마 «내용»을 보는 것은 `check-db-table`(앱 규율·#630 db_table 값·#631 타 BC FK) 하나뿐이다. `architecture-db-final` spec 이 같은 축에서 «①②③④ 어느 축도 지목하지 않음 → §16 기본값» 을 반복한 것과 같은 실측이다.
- **기본값 이탈(enforcedBy 병기) 3계열**:
  1. **docstring 이 이 문서를 이름으로 지목** — `check-idempotency-scope-creep.py` 선두 «architecture-db §9.6 Idempotency storage 집행». §16 «역도 성립»상 23행을 기본값으로만 두면 오배선이라 병기했고, **커버 범위는 «G1 승인 없는 미요청 멱등성 산출물» 1종**뿐임을 basis 에 명기했다(정책을 «정하라»는 의무는 비커버 — final api s021-5.1/b6 과 같은 논거).
  2. **문면 축이 검사기 술어와 축자 대응** — 24행 트랜잭션 내부 실행 금지 ↔ `check-transaction-boundary` #200(«커밋 뒤 부작용은 `unit_of_work.after_commit`»), Outbox ↔ `check-broker-contract` #603 ⑴outbox·#532(at-least-once «요구» 명시), consumer 중복 무시 ↔ `check-missable-entrance` #181(«멱등성은 유스케이스가 갖는다» — broker-contract docstring 이 «멱등 물음의 소유자는 #181» 로 명시 위임).
  3. **정본 문서의 기이관 배선 승계** — 23·24행은 `architecture-db-final` s043-9.6·s044-9.7 의 배선을 따랐다(24행은 아래 «정본과 갈린 자리»대로 **부분** 승계).
- **정본과 갈린 자리 1건(F4 수리 · 2026-08-22)** — **24행 W1 «외부 부수효과의 트랜잭션 내부 실행 금지»**. 정본 `architecture-db-final` s043-9.6/b14 실물은 E:[`check-transaction-boundary`, `check-usecase-dto-placement`, `check-broker-contract`]·D:[`agent-discipline-reviewer`]인데 이 spec 은 E 1종·D:`agent-design-review-db` 다. 판정: **부분 승계가 옳다**. ⓐ 정본 b14 는 «트랜잭션 밖 handoff + 유실 불허 시 Outbox»를 한 Work 에 접었지만 SKILL 24행은 두 문장으로 갈려 Outbox 축은 이 문서의 별도 Work(#18)가 `check-broker-contract`(#603·#532)로 이미 진다 — 같은 검사기를 두 Work 에 중복 배선하면 축이 흐려진다. ⓑ `check-usecase-dto-placement` #541 은 «발행 자리»(pull_events·publish 호출 위치) 규율이라 이 Work 의 축(«외부 부수효과의 실행 위치»)과 대상이 다르다. ⓒ D 는 이 문서 전체가 §16 문서군 기본값(architecture-db→`agent-design-review-db`)으로 통일돼 있고 24행만 정본을 따라 `agent-discipline-reviewer` 로 바꿀 문면 근거가 없다. 수리 전 basis 의 «b14 배선 준거» 문구가 이 갈림을 감췄으므로 «부분 승계 + 사유»로 정정했다.
- **오배선 회피 기록 3건**:
  1. **21행 제약조건** — `check-db-table.py` 는 «앱 규율»(#329~#335 apps/모델 파일 규칙)과 #630(db_table 값)·#631(타 BC FK) 축이라 «비즈니스 불변식을 unique/check 로 보호했는가»를 묻지 않는다. 달면 반대 의미(테이블 이름·FK 금지)를 집행하게 되므로 비웠다.
  2. **22행 격리 수준** — `check-mechanism-ownership.py` ⑴ 은 «프로덕션 DB 엔진의 트랜잭션·락·격리 «메커니즘»을 커스텀 백엔드로 교체한 정확한 형태»만 AND 게이트로 차단한다(AND-1 = stock 아닌 ENGINE). «Read Committed 를 고를 것인가»는 그 술어 밖이라 기본값 유지 — 실측 근거를 가진 기본값이라 도피가 아니다. 단 23행의 **동시성 테스트용 백엔드 교체 금지**(final s043-9.6/b13)는 SKILL 문면에 없어 이 문서에는 대응 Work 가 없다.
  3. **25행 Expand/Backfill/Contract** — `check-mechanism-ownership.py` ⑵(#336~#338·#593)은 마이그레이션 «파일»의 자리·이름·손편집 금지 규율이고, «단계 순서를 지켰는가»는 산출물 형태로 갈리지 않는다(검사 공백).
- **로드·라우팅·위임 경계 규범의 소유**: ddd 판 검수표와 동일 처분 — 로드 조건·라우팅 준거는 문서군 기본값(`agent-design-review-db`) + `command-dddjango`(스킬 배분 소유), «X → skill-y» 불릿은 **수임 문서군 기본 Agent**(implementation-*→`agent-discipline-reviewer` · architecture-ddd→`agent-design-review-ddd` · architecture-api→`agent-design-review-api`).
- **센서스 codex DIFF 비고 처리**: 발주서 s001 비고의 «codex description 에 미치환 구명 `architecture-ddd` 지시»는 **codex 판 코퍼스의 표류**이고 이 저장소 정본 문면은 현재 그대로다(정규화 대조 대상 아님). spec 은 현재 문면 verbatim 을 잘라 담았고, 그 사실만 basis 에 각주로 남겼다.
