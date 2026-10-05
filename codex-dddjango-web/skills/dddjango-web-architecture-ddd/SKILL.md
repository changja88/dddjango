---
name: dddjango-web-architecture-ddd
description: dddjango-web 도메인 아키텍처 — 간소화 DDD의 채택/비채택 지도, frozen dataclass 애그리거트의 루트 경유 변경 규율, 판정 소유(1곳째부터 domain)와 강등, 도메인 서비스 주어 귀속, Specification, UseCase 관문. 도메인 모델을 설계·작성·검수하거나 판정·계산의 소유자를 정할 때 로드한다.
user-invocable: false
---

# 도메인 아키텍처

## 언제 쓰나

도메인 모델(애그리거트·엔티티·VO)을 설계·작성·검수할 때, 판정·계산의 소유자를 정할 때, BC 어휘·경계를 판단할 때, full-DDD 패턴(이벤트·CQRS 등) 제안이 올 때 로드한다. 전문을 읽지 말고 아래 라우팅 표로 필요한 절만 부분 적재한다. 경계:

- 파일트리·폴더·명명 **사실**(domain 5종 폴더·골격) → `dddjango-web-discipline-houserules`
- VM·State·SharedState 동작, 화면 동기화 → `dddjango-web-architecture-state`
- Repo 구체·Either·직반환 계약 → `dddjango-web-architecture-data`
- 캡슐화·SOLID·이름 일반론 → `dddjango-web-discipline-cleancode`
- frozen dataclass **표기법** → `dddjango-web-implementation-python`

## 핵심 운영 원칙

- dddjango-web은 간소화 DDD다 — 비채택 목록(§10)에 있는 패턴은 제안하지 않는다: 도메인 이벤트·CQRS·Event Sourcing·Saga·Repo 인터페이스·DIP·핵사고날·ACL·DTO (§1·§10)
- 도메인 어휘로 진술되는 판정·계산은 1곳째부터 domain이 기본 — VM의 일은 변환, VM 소유 주장에는 *왜*를 적는다 (§5)
- 같은 판정이 Model 밖 2곳(VM·view·section·ui_extension·State 프로퍼티)에 복제되면 domain_service/specification으로 강등 (§5)
- 조건·계산·상태 전이가 걸린 갱신은 애그리거트 루트의 메서드가 새 인스턴스를 반환하는 형태로만 — `dataclasses.replace` 직접 호출은 도메인 의미 없는 복제에만 (§4)
- 불변식은 변경 메서드 안에서 검증(도메인 예외 raise), 생성 시점 검증은 비강제 — 생성자 검증이 서버 직파싱의 길을 막지 않게 (§4)
- 타 애그리거트 참조: 서버 중첩은 그대로, 클라가 새로 조립하는 관계만 ID 우선 (§4)
- 여러 애그리거트에 걸치는 판정·계산은 규칙의 주어(그 규칙이 누구의 속성·정책인가) 애그리거트의 domain_service에 — 공용 위치 없음, 애그리거트는 서비스를 모른다 (§6)
- Specification은 재사용·조합되는 판정 — 풀네임, Model에서만 평가, 조합 계층은 수요가 실재할 때만 (§7)
- UseCase는 Model의 관문 — 도메인 위임·Either 통과(새 raise 금지)·UI 호출 금지·도메인 개념 단위 명명(화면명 금지) (§8)
- 새 판정이 그 BC domain에 0개이고 VM·view에만 살면 빈혈 blocker — 단 도메인 어휘 없는 변환·조립을 억지로 domain에 넣지도 않는다 (§9)

## 상세 레퍼런스

| 질문 | 위치 |
|---|---|
| 무엇을 채택하고 무엇을 버렸나 — 간소화 지도 | [`references/final.md`](references/final.md) §1 |
| BC·유비쿼터스 언어 — 같은 개념 같은 철자 | final.md §2 |
| VO·엔티티를 어떻게 쓰나 — frozen dataclass·직파싱 | final.md §3 |
| 애그리거트 갱신·검증·참조 — 루트 경유 3규칙 | final.md §4 |
| 이 판정은 누구 것인가 — 소유·강등 | final.md §5 |
| 여러 애그리거트에 걸친 로직 — 주어 귀속 | final.md §6 |
| 재사용·조합되는 판정 규칙 | final.md §7 |
| UseCase가 하는 일·금지·명명 | final.md §8 |
| 빈혈인가 과잉인가 | final.md §9 |
| full-DDD 패턴 제안을 반송할 때 | final.md §10 |
| 판별이 갈리는 경계(BC 어휘·게이트 입장·판정 귀속·UseCase 명명) | 공유 reference `undecidable.md` §3·§4·§8 (dddjango-web-discipline-houserules 동봉) |

각 절은 필요한 절만 읽는다(`## §N.` 헤더로 grep 가능 — 전체 로드 불필요).
