---
name: implementation-django
description: Django 코어 구현 지식 — 모델·ORM·QuerySet/Manager, 마이그레이션, 서비스·셀렉터 레이어, 트랜잭션 경계, 설정·미들웨어·캐싱·보안·시그널, 트랜잭셔널 outbox 구현. Django 모델·ORM·서비스 레이어·트랜잭션 코드를 새로 작성하거나 리팩터링할 때 먼저 로드한다. 표현계층(템플릿/폼/HTMX)은 implementation-django-web, JSON API는 implementation-django-ninja, 신규 REST 계약은 architecture-api로 위임.
---

# Django 코어 구현

## 언제 쓰나

Django 코어(모델·ORM·서비스 레이어·트랜잭션·설정·마이그레이션·시그널·캐싱·보안) 코드를 설계·작성할 때 로드한다. 경계:

- 서버렌더 표현계층(뷰=어댑터·템플릿·웹폼·HTMX/CSRF) → `implementation-django-web`
- JSON API 어댑터(Router/Schema) → `implementation-django-ninja`
- 신규 REST API 계약 설계 → `architecture-api`
- 도메인 전략·애그리거트·도메인이벤트 채택 → `dddjango-architecture-ddd`
- DB 신뢰성·인덱스·트랜잭션 격리·outbox 전달 보장 → `architecture-db`
- Python 관용구 → `implementation-python`, 클린코드 원칙 → `dddjango-discipline-cleancode`

## 핵심 운영 원칙

- 비즈니스 로직은 뷰가 아니라 모델·도메인에 — 평면 Django 맥락은 fat model(§4.1), dddjango 표준 4계층은 `domain_layer` 애그리거트 소유(`architecture-ddd` §3.2)
- 서비스 레이어 도입 시점과 HackSoft service/selector 패턴 (§16.1–§16.2)
- 트랜잭션·일관성 경계는 `transaction.atomic()`, 외부 부수효과는 `transaction.on_commit()` (§16.4)
- 메시지 유실이 불가하면 트랜잭셔널 outbox로 구현 (§16.5 — 채택 기준 `dddjango-architecture-ddd` §3.7, 전달 보장 `architecture-db` §9.7)
- Choices 계층 소유: 도메인 상태 값 집합은 domain Enum 파생(TextChoices 자체 선언은 순수 인프라 필드 한정), `default=`는 `.value` 평탄화, 비교·`.filter()`는 심볼로만 (§2.5, 마이그레이션 동결 §10.4)
- QuerySet 최적화·N+1 방지는 selector/QuerySet 메서드로 (§5, §11.1)
- 마이그레이션은 안전·무중단 순서 준수 (§10)
- 설정은 환경별 분리, 직접 접근 주의 (§3.3–§3.4)

## 상세 레퍼런스

주제별로 [`references/final.md`](references/final.md)의 해당 절을 따른다:

| 주제 | 절 |
|---|---|
| 설계 철학 | §1 |
| 코딩 스타일·임포트 순서·Choices 정의(계층 소유·`.value` 평탄화·소비 규율 §2.5) | §2 |
| 프로젝트/앱/설정 분리 | §3 |
| 모델 설계 (fat model·상속·필드·검증) | §4 |
| QuerySet과 Manager | §5 |
| REST API 경계와 기존 DRF 유지보수 | §8 |
| 시그널 가이드라인 | §9 |
| 마이그레이션 베스트 프랙티스 | §10 |
| 성능 최적화 (N+1·인덱스) | §11 |
| 캐싱 전략 | §12 |
| 보안 | §13 |
| 테스트 패턴 | §14 |
| 미들웨어 | §15 |
| 서비스 레이어·트랜잭션·outbox | §16 |
| Django 5.x 새 기능 | §17 |
| Django admin·폼 타이핑(django-stubs 제네릭 기저) | §18 |

각 절은 [`references/final.md`](references/final.md)에서 필요한 항목만 읽는다(전체 로드 불필요).
