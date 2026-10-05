---
name: dddjango-web-architecture-data
description: dddjango-web 데이터 아키텍처 — Repo Either 계약(Right=성공), safe_api_call 전 예외 정규화, DataSource 도메인 엔티티 직반환(in-process api_client), OpenAPI 계약 스냅샷 체계와 계약 위험 행위. 데이터가 web 바깥(백엔드 API)과 오가는 방식을 결정·검수할 때 로드한다.
user-invocable: false
---

# 데이터 아키텍처

## 언제 쓰나

DataSource·Repo·infra service를 설계·작성·검수할 때, 실패 처리 경로를 만들 때, 서버 계약 스냅샷을 인용·검증할 때 로드한다. 전문을 읽지 말고 아래 라우팅 표로 필요한 절만 부분 적재한다. 경계:

- 파일·폴더·명명 사실, common 입장 판별 → `dddjango-web-discipline-houserules`
- 에러를 State에 담아 표시·소비하는 방식, 세션·프로세스 수명 보관 → `dddjango-web-architecture-state`
- 도메인 엔티티 모델링·판정 소유 → `dddjango-web-architecture-ddd`
- api_client·DataSource **표기법** → `dddjango-web-implementation-django`

## 핵심 운영 원칙

- Repo는 구체 클래스 하나(인터페이스 없음)로 DataSource를 감싸는 단일 진실 원천이다 (§1)
- safe_api_call은 모든 예외(상태코드 실패·JSON 파싱·필드 누락·타입 불일치)를 BadRequestResponse로 정규화한다 — Repo·infra service는 어떤 실패도 raise로 탈출시키지 않는다, 전 실패 = Either (§2)
- Either는 Right=성공 — 단 기존 프로젝트에 확립된 방향이 있으면 그것 우선 (§3)
- Either의 실패 쪽을 버리는 코드 금지 — 표시하지 않는 결정조차 State의 error 필드를 거쳐 명시적으로 (§3)
- DataSource는 도메인 엔티티를 직접 반환한다 — DTO 계층 없음, 엔티티를 저장 모델(ORM Model)로 만들지 않는다 (§4)
- web에는 로컬 저장 층이 없다 — BC 데이터는 매 요청 UseCase 재조회, 화면 간 공유 값은 SharedState(dddjango-web-architecture-state §5) (§5)
- 능동(이벤트 받아 UseCase 구동)이면 application service, 수동(호출당하는 SDK 어댑터)이면 infra service (§6)
- 서버 계약은 동결 스냅샷이 사실의 출처 — architect는 동결본에 없으면 보고(임의 가정 금지), coder·G2는 절단 경량본만 본다 (§7)
- 스냅샷으로 확인 불가한 의미 가정은 명세에 '계약 위험'으로 표기한다 — tracer 발동의 기계 앵커 (§8)

## 상세 레퍼런스

| 질문 | 위치 |
|---|---|
| infra 종류별 역할·state와의 경계(캐싱·에러) | [`references/final.md`](references/final.md) §1 |
| 실패를 어떻게 잡나 — safe_api_call 계약·골격 | final.md §2 |
| Repo 반환 계약 — Either 방향·UseCase 통과 | final.md §3 |
| 서버 JSON을 무엇이 파싱하나 — 직반환·DTO 없음 | final.md §4 |
| 로컬 저장 — web에는 해당 없음 | final.md §5 |
| SDK를 감싸는 코드 — 수동 어댑터·능동/수동 판별 | final.md §6 |
| 계약 스냅샷 2종의 의미·extract_contract 사용법·에이전트별 규율 | final.md §7 |
| '계약 위험' 표기를 언제 다나 — tracer 앵커 | final.md §8 |
| 계약 위험 판별·검증 절차 | 공유 reference `undecidable.md` §12 (dddjango-web-discipline-houserules 동봉) |

각 절은 필요한 절만 읽는다(`## §N.` 헤더로 grep 가능 — 전체 로드 불필요).
