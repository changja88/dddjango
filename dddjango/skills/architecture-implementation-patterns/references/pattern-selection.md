# Pattern Selection

Load this when deciding whether to use layered, clean, hexagonal, CQRS, event sourcing, saga, service layer, straightforward service functions, or a simpler Django-native structure.

## 선택 순서

1. DDD 모델을 확인한다: bounded context, aggregate, invariant, use case, integration boundary.
2. 실제 압력을 분류한다: framework leakage, persistence mapping, transaction boundary, read/write divergence, external side-effect reliability, legacy language conflict, test seam, replacement need.
3. 그 압력을 해결하는 가장 가벼운 패턴을 선택한다.
4. 선택하지 않은 무거운 패턴과 그 이유를 함께 말한다.
5. DB locking/isolation, REST idempotency, Django 구현, pytest 구현 상세는 owning skill로 넘긴다.

## 기본값

- Layered call flow를 기본으로 둔다: interface/presentation -> application -> domain, infrastructure는 세부 구현을 맡는다.
- 많은 Django 프로젝트는 model methods plus services/selectors로 충분하다.
- Supporting subdomain이나 simple CRUD는 no extra pattern 또는 straightforward service function이 더 명확할 수 있다.
- DDD처럼 보이기 위해 repository, Unit of Work, ports, CQRS를 도입하지 않는다.

## 패턴 선택표

| Pattern | Consider when | Avoid when |
|---|---|---|
| Layered architecture | presentation/application/domain/infrastructure 책임을 분명히 해야 한다 | 작은 앱에서 폴더만 늘어나 흐름을 숨긴다 |
| Clean/hexagonal architecture | framework, ORM, SDK, broker가 domain policy를 흔들 위험이 있거나 replacement, failure isolation, contract stability가 중요하다 | Django conventions가 더 명확하고 domain이 단순하다 |
| Ports/adapters | core use case가 framework 또는 external service detail에서 독립해야 한다 | 구현이 하나뿐이고 testing/replacement 가치가 낮다 |
| Service layer | 여러 model, transaction, external port를 조율하는 write/use case가 있다 | 단일 model method가 invariant를 명확히 캡슐화한다 |
| Repository/UoW | aggregate persistence와 transaction boundary를 application 언어로 표현해야 한다 | thin QuerySet wrapper가 된다 |
| CQRS | command model과 read model 요구가 실제로 갈라지고 eventual consistency를 제품/운영 기준이 수용한다 | selector 또는 QuerySet 최적화로 충분하거나 eventual consistency를 수용할 기준이 없다 |
| Event sourcing | history, audit, replay, temporal reconstruction이 domain 핵심이다 | notification이나 단순 audit log만 필요하다 |
| Saga | long-running/distributed process에 compensation이 필요하다 | 하나의 local transaction으로 invariant를 보호할 수 있다 |
| Outbox | DB commit과 external message delivery를 안정적으로 연결해야 한다 | external side effect가 없거나 `transaction.on_commit()`으로 충분하다 |
| ACL | upstream/legacy language가 downstream domain language를 오염시킨다 | external model이 bounded context language와 이미 일치한다 |

## Django 실용 기준

- Django admin, migrations, forms, QuerySet, model behavior의 이점을 유지할 수 있으면 유지한다.
- ORM lifecycle, lazy loading, schema shape, framework concerns가 domain rule을 왜곡할 때만 pure domain/ORM model 분리를 고려한다.
- 패턴은 전체 프로젝트가 아니라 지금 문제가 있는 boundary에 점진적으로 적용한다.
