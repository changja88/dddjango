# T3 적대 리뷰 — architecture-ddd-final spec/worksheet 반박 기록

- 대상: `workspace/eval/t3/specs/architecture-ddd-final.spec.json` + `workspace/eval/t3/worksheets/architecture-ddd-final.md`
- 대조: 발주서 · T3-authoring-brief · 원문 `dddjango/skills/architecture-ddd/references/final.md`(마커 제거 복원본 2122행 기준) · `dddjango/scripts/check-*.py` 27종 docstring 실독
- 검증 방법: 발주 36절 + 파일럿 재수록 2절 **전수** 블록·kind·규범·배선·재진술 원문 대조. 도구 검증(exit 0)·파일럿 2절 바이트 동일·소유/클래스 분포(46/50/92 · 116/27/26/16/3)·basis 공란 0은 실측 재확인 — 기계 축은 무결. 아래는 판단 축의 반박 전건.
- 판정: **불합격(반송)** — high 1 · medium 3 · low 12.

## HIGH

### H-1. s052-9/b9 — «루트를 통해서만 접근» 규범 소실 (재진술 억제 오적용) [재진술]

- 주장: §9 애그리거트 행(2083행)은 세 문장이다 — «일관성 경계이자 트랜잭션 경계» · «루트를 통해서만 접근» · «ID로 타 애그리거트 참조». spec은 행 전체를 사본으로 억제하고 restates → s019/b1·b2·b5 로 연결했으나, **둘째 문장 «루트를 통해서만 접근»은 대상 세 블록 어디에도 없다**. 전수 검색 결과 이 규범의 산문 진술은 문서 전체에서 2083행이 유일하다(그 외는 예제 펜스 주석 755행 «모든 상태 변경은 Order를 통해서만 수행한다» — 계수 제외 관례 · 파일럿 s017-3.2 도 «판정·불변식 도메인 소유»만 있지 루트 경유 접근은 없다 · SKILL Vernon 불릿에도 없다). 센서스는 이 행을 규범 1로 계수했는데(행 단위) spec은 Work 0 — 애그리거트의 대표 규칙 하나가 그래프에서 통째로 사라진다. 담당 검사기까지 실재한다: check-domain-model #257 «상태 변경은 루트를 지난다»·#258 «애그리거트 밖에서 붙잡는 것은 루트뿐» — T2-2 alias 조인이 앵커할 Work 자체가 없어진다.
- 수정안: s052-9/b9 에 Work 1건 승격 — label «애그리거트 접근·상태 변경은 루트 경유만», class Obligation, enforcedBy `check-domain-model.py`(② #257·#258 문면 일치) · delegatedTo `agent-design-review-ddd` 병기. 나머지 두 문장 몫의 restates(s019/b2·b5)는 유지(블록은 norms+restates 동시 보유 가능 — s011-2.5/b19 판형). census 대사 s052-9 행을 −13 → −12 로, 합계 Δ·억제 원장(«s052-9/b9» 행)을 함께 정정.

## MEDIUM

### M-1. s043-6.2/b2 ↔ s021-3.4/b3 — same-doc 재진술 쌍 미기재 [재진술]

- 주장: §6.2 첫 문장 «ORM은 도메인 모델을 임포트해야 하며, 도메인 모델이 ORM에 의존해서는 안 된다»(1676행)는 §3.4 의 Cosmic Python 인용 «ORM이 도메인 모델을 임포트하게 하라. 도메인 모델이 ORM을 임포트하면 안 된다»(844행)와 같은 규칙의 같은-문서 재진술이다(같은 출처 Cosmic Python·같은 배선 check-domain-model #8 — worksheet 자신이 s043-6.2/b2 basis 에 «Data Mapper 방향, #8 문면 일치»라고 적어 동일 규칙임을 자인). 그런데 양쪽 다 Work 승격(§3.4 에 2건 + §6.2 에 1건)되고 restates 연결이 없다 — §15 «정본 1곳만 Work 승격» 위반·표류 위험. 저작자는 census 재진술 열(N)을 넘어 §9 행 13건을 스스로 억제했으므로 «census 가 N 이라서»는 면책이 안 된다.
- 수정안: 정본은 첫 등장·원문 인용인 s021-3.4/b3. s043-6.2/b2 의 첫 규범(«ORM이 도메인을 import하고 도메인은 ORM에 의존하지 않는다») Work 억제 + restates → s021-3.4/b3 추가(핸드오프 규범은 유지 — 블록 norms 1 + restates 1). census 대사에 s043-6.2 Δ −1 사유 기재. (차선: Work 유지 + restates 만 추가 — 최소한 쌍은 기록되어야 한다.)

### M-2. s046-6.5/b7 «중간 단계 실패 시 보상 행동 실행» — enforcedBy 오배선 (극성 반전) [배선]

- 주장: enforcedBy `check-event-publish.py` 의 근거 #564 는 «진행표 금지 — saga/·process_manager/ 폴더는 ⓓ 후보», 즉 saga 산출물을 **의심 후보로 반출**하는 금지-측 규칙이다. 배선된 규범은 반대 극성 — saga 채택 시 보상 실행 **의무**다. #564 는 보상 흐름의 존재·실행을 전혀 검사하지 않고, 오히려 이 규범을 따르는 코드 형태(saga 폴더)에 발화한다. basis 스스로 «saga 채택 자체를 후보로 문다 · 보상 흐름 판정은 설계 시점»이라 자인 — §16 4원 어느 것도 이 규범에 대해 성립하지 않는 과잉 배선.
- 수정안: enforcedBy 제거, delegatedTo `agent-design-review-ddd` 단독(기본값·이탈 근거 불요). #564 를 언급하려면 «saga 채택 관문» 규범이 아닌 이 규범의 basis 에서는 삭제.

### M-3. s026/b2 «소비 BC는 미지 event_type 처리 방침을 함께 정한다» — enforcedBy 오배선 (무관 규칙) [배선]

- 주장: enforcedBy `check-event-publish.py` 근거 #507 은 «event_subscription/ 은 남의 BC 를 published_event 밖으로 import 금지» — import 폭 규칙이다. 배선된 규범의 실질(미지 event_type 의 UNKNOWN 폴백 또는 명시적 거부 방침 결정)과 접점이 0이다. basis 의 «구조만 문다»는 성립하지 않는다 — 미지 타입 처리 분기의 구조는 import 폭이 아니라 match/분기 완전성 문제고, 27종 어느 docstring 에도 이 진단은 없다(«이름 기반 승격 금지»·append-only 등 같은 절의 이웃 규범들과 동일하게 위임 단독이 정합).
- 수정안: enforcedBy 제거, delegatedTo 는 유지하되 소유 재검토 — 방침 «결정»은 설계 시점(agent-design-review-ddd 유지 가능)이나 basis 를 «정적 진단 부재(27종 실독) — 위임 기본값»으로 교체.

## LOW

### L-1. s052-9/b5·b6 — 억제 사유 부정합: restates 대상이 무규범 prose [재진술]

- 주장: 컨텍스트 맵 행(b5)→s011-2.5/b2, 증류 행(b6)→s012-2.6/b2 — 두 대상 블록 모두 Work 0 인 정의 prose 다. «본문이 정본(Work 보유)이라 사본 억제»라는 원장 서사가 이 두 행에서는 깨진다 — 실제 판정은 «행이 규범이 아님(서술)»이어야 하고, 그 경우 census 계수 반박으로 기재해야 한다. 억제 자체의 결론은 유지 가능하나 사유가 틀렸다.
- 수정안: worksheet 억제 원장·census 대사에 두 행을 «사본 억제»가 아니라 «규범 아님(서술) — census 행 단위 계수 반박»으로 재분류(restates 블록 연결은 텍스트 사본 관계로서 유지 가능).

### L-2. s039-5.4/b3 «질문하는 행동이 대답을 바꾸지 않는다» — 기본값 도피 후보 [배선]

- 주장: check-transaction-boundary #197 «읽기 전용 유스케이스는 UnitOfWork 를 받지 않는다»는 CQS 의 구조 절반(질문이 쓰기 기계를 들지 않는다)을 결정적으로 집행하고, 저작자는 같은 검사기 #197 을 s023-3.6/b3(트랜잭션 관리)에 이미 배선해 인지 상태였다. §16 역방향(담당 근거가 있는데 기본값 도피) 저촉 소지. 다만 #197 의 자기 서사는 UoW 위생이라 담당성 논증이 갈릴 수 있어 low.
- 수정안: enforcedBy `check-transaction-boundary.py`(② #197) 병기 + delegatedTo 유지, basis 에 잔여(변수 수준 부작용)는 의미 레인임을 기재.

### L-3. s026/b2 — 5불릿 단일 블록 병합 (16규범/6행) [경계kind]

- 주장: b2 [1204-1209]는 배치·소유/파생 표기/수명/제외/소비자 짝 — 주제가 다른 최상위 불릿 5개(각 2~5문장)를 한 블록으로 병합했다. §13 자연 단위에 «불릿»이 명시돼 있고 표는 행 단위로 쪼갠 것과 비대칭이다. s048-6.7/b11·s011-2.5/b19·SKILL 유예 #8 의 restates 조준과 향후 #N↔Work alias 조인의 해상도가 떨어진다. 다만 이 spec 전반의 «불릿 그룹=한 블록» 관례와는 내적 일관 — 규약 명문 위반이라 단정 못해 low.
- 수정안: 불릿별 5블록 분할(b2~b6 재채번, restates 좌표 동반 갱신). 분할하지 않으면 worksheet 경계 메모에 블록 내 문장→Work 대응의 불릿 좌표를 명기.

### L-4. s049-6.8/b3 — enforcedBy 근거 부족 (열거 목록 밖 축) [배선]

- 주장: 규범 문면의 열거(리포지토리·커스텀 UoW·CQRS·이벤트 소싱·saga·outbox·ACL)에 멱등성이 없다. check-idempotency-scope-creep 는 멱등성 축의 미요청 도입만 차단하므로 «③ P0 커버»가 이 규범의 문면을 커버한다는 주장은 열거 밖 유비에 기댄다.
- 수정안: enforcedBy 를 유지하려면 basis 를 «동일 원리(미요청 무거운 패턴 금지)의 인접 축 부분 커버»로 정직하게 고쳐 쓰거나, 제거하고 delegatedTo 단독.

### L-5. s049-6.8/b10 — basis ② 인용이 규범 문면과 소유자 불일치 [배선]

- 주장: 규범 문면은 멱등성 저장을 `architecture-api` 소유로 이양하는데, 인용된 검사기 docstring 은 «architecture-db §9.6 Idempotency storage 집행»이라 다른 소유자를 명시한다 — ② 근거가 규범을 뒷받침하는 게 아니라 원문·검사기 간 소유 충돌을 노출한다(원문 자체의 잠재 모순 — 이관 스코프 밖이나 worksheet 자인란에 기록됐어야 함).
- 수정안: basis 에서 «…과 짝» 표현을 «검사기는 멱등 산출물 무단 도입 차단으로 이 라우팅 행을 배후 집행 — 단 docstring 은 소유를 architecture-db §9.6 로 적어 문면과 불일치(자인)»로 교체하고 worksheet §4 자인 목록에 추가.

### L-6. s046-6.5/b7 «보상 트랜잭션은 반드시 멱등» — #181 커버 범위 초과 주장 [배선]

- 주장: check-missable-entrance #181 의 관할은 «놓칠 수 있는 입구(cron_job·webhook·event_subscription)가 부른 유스케이스»의 멱등성이다. saga 보상 트랜잭션이 그 입구 뒤에 있다는 보장이 없어 «멱등 물음의 소유자» 인용만으로는 이 규범의 담당이 성립한다고 보기 어렵다.
- 수정안: basis 에 «보상이 event_subscription/cron 경유일 때 한정한 부분 커버»임을 명기하거나 enforcedBy 제거 후 위임 단독.

### L-7. s016-3.1/b2 — 정의 문단 내 «불변(immutable)이어야 한다» 중복 미처리 [재진술]

- 주장: 469행 정의 문단의 «불변이어야 한다»는 b3 «값 객체는 반드시 불변»(473행)과 같은 규범의 같은-절 중복인데 b2 는 restates 없는 순수 prose 로 남았다(census 3 계수 승계라 Work 누락은 아님).
- 수정안: b2 에 restates → s016-3.1/b3 추가하거나 경계 메모에 «정의문 내 중복 — 계수·연결 억제» 판정을 명기.

### L-8. s007-2.1/b3 — Evans 인용 «모델을 리팩터링한다» 인용=규칙 관례 비일관 [규범식별]

- 주장: 45행 인용문 «코드를 리팩터링하는 것이 아니라 코드 아래에 있는 모델을 리팩터링한다»에 P0 규약 ②(인용=규칙 — s019/b4 Vernon·s021-3.4/b3 Cosmic Python·s039-5.4/b2 Greg Young 에 적용)를 적용하지 않았다. census 2 승계이나 같은 규약의 비일관 적용.
- 수정안: Obligation 1건 승격(+1, census Δ 사유 기재)하거나 경계 메모에 비승격 사유(과정 서술 인용 — 명령 인용 아님)를 명기.

### L-9. s038-5.3/b2 — «주요 아키텍처 스타일로 권장한다» 미계수 [규범식별]

- 주장: 1495행 첫 문장의 «권장한다»는 권고형 규범 후보(Permission)인데 계수 밖이다(census 16 승계). «애매하면 포함» 규약(P0)과 긴장.
- 수정안: 유지 시 경계 메모에 «채택 권고는 b3 선택 조건군이 구체화 — 중복 회피로 비계수» 사유 명기, 또는 Permission 1건 승격.

### L-10. s010-2.4/b3 — «하위 도메인은 발견하고, 바운디드 컨텍스트는 설계한다» 무Work + §9 사본 억제 [규범식별]

- 주장: 219행 [B] 불릿 첫 문장의 이 격언은 승격되지 않았고(census 4 승계), §9 BC 행(2077행)의 같은 문장 사본은 s010-2.4/b2·b3 로 억제됐다 — H-1 과 같은 형태(사본 억제 + 정본 측 무Work)로 규범 후보가 그래프 밖에 남는다. 격언성이 강해 low.
- 수정안: 규범으로 본다면 s010-2.4/b3 에 승격(+1) 후 §9 restates 유지, 아니면 억제 원장에 «격언 — 규범 아님» 판정 명기.

### L-11. s025/b2 — 소유·스코프 선언 문장 prose 처리 [규범식별]

- 주장: 1186행 «…전달 메커니즘이므로 이 문서가 다루지 않는다 … 이 문서는 결정과 채택 여부만 소유한다»는 s049-6.8 소유권 표 행(순수 규범으로 계수)과 같은 장르의 소유 경계 선언인데 계수 밖이다(census 승계). +1 승격한 b5 «명시할 항목»과의 «애매하면 포함» 일관성 문제.
- 수정안: Obligation(스코프 소유 선언) 승격을 검토하거나 census 대사에 비계수 사유(b5 핸드오프 4건이 같은 내용을 구체화)를 명기.

### L-12. worksheet §2 서두 — 미사용 10종 사유 서술이 자기 메모와 모순 [배선]

- 주장: «미사용 10종은 전부 API 오류 프로필·ninja 경계·인프라 예외 축이라 접점 없음»은 부정확 — check-common-container(framework 컨테이너 위치)·check-composition-root(DI 배선)·check-public-surface-annotation(주석·assert)은 그 축이 아니고, 특히 public-surface-annotation #69 는 §4.3 단언과의 접점을 worksheet 자신의 경계 메모 ①이 다뤘다(접점이 있었고 판정으로 배제한 것).
- 수정안: 해당 문장을 «10종 중 7종은 API/ninja/인프라 예외 축 — 나머지 3종(common-container·composition-root·public-surface-annotation)은 실독 후 개별 판정으로 비배선(#69 는 경계 메모 ① 참조)»으로 교정.

## 반박 안 함 (검증 통과 확인 기록)

- 기계 축: 좌표·해시·연속 무손실·kind 5종·datatype 관례·파일럿 2절 바이트 동일·restates_paths — 도구 exit 0 재확인.
- 의사결정 blockquote 7건 억제 방향(§8 레지스트리=정본) — 파일럿 [의사결정 #1] 판형과 동형, 대상 행(b3~b10) 대응 전건 정확.
- 인용 검사기 규칙 번호 전건 실재(#257·#264·#268·#269·#272·#298·#300·#301·#507·#529·#532·#533·#564·#603·#626·#629·#631·#635·#484 등 docstring 직접 대조).
- 위임 기본값 표 준수·이탈 2건(design-review-api·design-review-db)의 문면 근거 성립.
- 교차 문서 유예 11건 — SKILL «핵심 운영 원칙» 10불릿 전건 대응 확인, spec 내 교차 문서 restates 혼입 0.
- census 대사 Δ 산식(−20+2=−18)·소유 분포·class 분포 — 실측 일치.

## 처분 (수리자 기록 — 2026-08-22)

> 대조: 원문 `dddjango/skills/architecture-ddd/references/final.md`(마커 제거 복원본 2122행) 직접 실독 · `dddjango/scripts/check-*.py` 해당 docstring 재실독. 수리 산출: `workspace/eval/t3/specs/architecture-ddd-final.spec.json` + `workspace/eval/t3/worksheets/architecture-ddd-final.md`. 검증 전용 실행 **exit 0** 재확인(`--write` 미사용).
> 집계: **fixed 12 · rejected 4**. spec Work 합계는 188 불변(H-1 +1 / M-1 −1 상쇄) · 소유 45/50/93 · class 117/27/25/16/3 · restates 35.

| # | 처분 | 근거 한 줄 |
|---|---|---|
| H-1 | **fixed** | 2083행 둘째 문장 «루트를 통해서만 접근»이 restates 대상 s019/b1·b2·b5 어디에도 없음을 원문 대조로 확인(문서 전수 검색상 산문 진술은 이 행이 유일 — 755행은 계수 제외 펜스 주석) → s052-9/b9 에 Obligation 1건 승격(enforcedBy check-domain-model #257·#258 · delegatedTo agent-design-review-ddd), restates 3 은 유지. census −13→−12 · 원장 «부분 억제» 재기재. |
| M-1 | **fixed**(1안) | 1676행과 844행이 같은 출처(Cosmic Python)·같은 규칙·같은 배선(#8)임을 원문 대조로 확인 → 첫 등장·원문 인용인 s021-3.4/b3 을 정본으로 두고 s043-6.2/b2 의 ORM 방향 Work 억제 + restates 추가(핸드오프 규범 유지). #8 축 커버는 정본 2건이 그대로 져 손실 0. census s043-6.2 Δ −1 기재. |
| M-2 | **fixed** | check-event-publish #564 는 «진행표 금지 — saga/·process_manager/ 폴더는 ⓓ 후보»로 규범 준수 형태에 발화하는 반대 극성이 맞다 → enforcedBy 제거, delegatedTo agent-design-review-ddd 단독, basis 를 «27종 실독 — 보상 흐름 진단 부재·위임 기본값»으로 교체. |
| M-3 | **fixed** | #507 은 event_subscription 의 import 폭 규칙이라 미지 타입 폴백·거부 방침과 접점 0 확인(27종 재실독에도 해당 진단 없음) → enforcedBy 제거, delegatedTo 유지, basis 를 «정적 진단 부재 — 위임 기본값»으로 교체. |
| L-1 | **fixed** | 2079·2080 행과 대상 블록(258·367행)이 모두 정의 서술이고 대상이 Work 0 임을 확인 → 억제 원장에 **판정 열** 신설, b5·b6(및 b3)을 «규범 아님(서술)»으로 재분류, census s052-9 행에 사유 병기. restates 에지는 텍스트 사본 관계로 유지. |
| L-2 | **fixed** | check-transaction-boundary #197 «읽기 전용 유스케이스는 UoW 를 받지 않는다»가 CQS 의 구조 절반을 결정적으로 집행하고 같은 검사기를 s023-3.6/b3 에 이미 배선한 것도 사실 → enforcedBy 병기 + delegatedTo 유지, 잔여(변수 수준 부작용)는 의미 레인임을 basis 에 기재. |
| L-3 | **fixed**(2안) | b2 가 최상위 불릿 5개를 병합한 것은 사실이나 §13 이 «다중 statesNorm + 블록 내 문장→Work 대응을 검수표에 기록»으로 이 형태를 명시 허용 → 분할 대신 검수표 s026 표의 블록 열에 불릿 좌표 ①~⑤(1204~1208)를 전 규범에 병기하고 경계 자인을 추가. 분할 시 s011-2.5/b19·s048-6.7/b11·SKILL 유예 #8 의 restates 좌표가 함께 흔들리는 비용도 고려. |
| L-4 | **fixed** | 2005행 열거(리포지토리·UoW·CQRS·ES·saga·outbox·ACL)에 멱등성이 없는 것 확인 → basis 의 «③ P0 커버» 단정을 «동일 원리의 인접 축 부분 커버»로 정직화(배선은 유지 — 열거 밖이지만 같은 금지 원리의 유일 기계 집행). |
| L-5 | **fixed** | check-idempotency-scope-creep docstring 선두가 «architecture-db §9.6 Idempotency storage 집행»으로 규범 문면(architecture-api)과 다른 소유자를 명시함을 확인 → basis 를 «배후 집행 + 불일치 자인»으로 교체하고 검수표 §4 자인 목록에 ③으로 추가. |
| L-6 | **fixed** | #181 관할이 «놓칠 수 있는 입구가 부른 유스케이스»로 한정됨을 docstring 재실독으로 확인 → enforcedBy 는 유지하되 basis 에 «입구 경유 보상에 한정한 부분 커버(자인)»와 잔여 위임을 명기. |
| L-7 | **fixed** | 469행 정의문의 «불변(immutable)이어야 한다»가 473행 규범의 같은-절 중복임을 확인 → s016-3.1/b2 에 restates→b3 추가(계수 불변), census 행에 사유 병기. |
| L-8 | **rejected** | 승격한 인용 3건(Vernon «제한하라»·Cosmic Python «하게 하라/하면 안 된다»·Greg Young «취급하고 적용하라»)은 전부 **명령형**이고, 45행 Evans 인용 «…모델을 리팩터링한다»는 **서술형**이다 — P0 규약 ②는 명령형 인용에 걸리므로 «같은 규약의 비일관 적용»이 성립하지 않는다. 승격하지 않고 판정 사유만 §4 «인용=규칙의 적용 조건» 메모와 census 행에 남겼다. |
| L-9 | **rejected** | 1495행은 «[C]는 …권장한다»로 **원전의 권고를 보고하는 서술**이고, 이 문서 자신의 채택 태도는 b3 선택 조건 4 + b4 회피 조건 3 이 소유한다 — 무조건 권고로 승격하면 바로 뒤 회피 조건군과 모순한다. 비계수 유지, 사유를 census 행·경계 메모에 기재. |
| L-10 | **rejected** | 219행 문장은 «[B]: "…" 는 점을 가장 강조»라는 서술틀 안의 격언 보고라 규범 문장이 아니다(L-8 과 같은 명령/서술 축). §9 사본 억제는 유지하되 원장 판정을 «규범 아님(서술·격언)»으로 적어 H-1 형태(원본 규범 소실)와 구분했다 — H-1 과 달리 이 문장은 승격 대상 자체가 아니다. |
| L-11 | **rejected** | 1186행 문면이 «(아래 handoff)»로 자기 구체화를 직접 지목하는 예고문이라 §6.8 소유권 **표 행**(소유자를 확정 지정하는 독립 규범)과 장르가 다르다 — 같은 내용을 b5 의 핸드오프 4건이 소유자별로 구체화하고 그쪽만 Work 를 받는 것이 «정본 1곳» 규율에 맞다. 비계수 유지, 사유를 census s025 행에 기재. |
| L-12 | **fixed** | 3종 docstring 재실독으로 축이 다름을 확인(common-container=횡단 framework 위치 · composition-root=DI 배선 · public-surface-annotation=타입 전면·#69 assert) → 검수표 §2 서두를 «7종은 API/ninja/인프라 예외 축 · 3종은 실독 후 개별 판정 비배선»으로 교정하고 #69 는 경계 메모 ① 참조를 명시. |
