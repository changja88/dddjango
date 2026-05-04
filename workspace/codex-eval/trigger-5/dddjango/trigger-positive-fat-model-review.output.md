현재 상태로는 특정 Django 모델이 fat model인지 판정할 수 없습니다. `/private/tmp/dddjango-codex-eval`가 비어 있고, `models.py`, `manage.py`, `pyproject.toml`, `config.toml` 모두 해당 작업 디렉터리 아래에서 발견되지 않았습니다. `AGENTS.md`가 가리킨 `config.toml`도 현재 경로에는 없습니다.

확인한 내용:
- `pwd` → `/private/tmp/dddjango-codex-eval`
- `rg --files` → 결과 없음
- `/private/tmp/dddjango-codex-eval` → 파일 없음
- `/private/tmp` 전체에서 Django/Python 후보 검색 → 모델 코드 없음

모델 코드를 받으면 아래 위험도 순서로 리뷰하겠습니다.

1. **High: 모델이 트랜잭션/외부 I/O/영속성 흐름을 직접 조율하는지**
   - `save()` 안에서 결제, 메일, API 호출, 다른 Aggregate 갱신이 있으면 fat model입니다.
   - 개선: Django model은 상태와 최소 불변식 중심으로 두고, use case 조율은 application service로 이동합니다.

2. **High: 여러 Aggregate의 상태를 한 모델 메서드에서 함께 바꾸는지**
   - 예: `Order.complete()`가 `Payment`, `Inventory`, `Shipment`까지 직접 변경.
   - 개선: 즉시 일관성이 필요한 자기 Aggregate 내부만 변경하고, 나머지는 domain event 또는 application service에서 조율합니다.

3. **Medium: 비즈니스 규칙과 ORM 쿼리가 섞여 있는지**
   - `can_cancel()` 같은 규칙 메서드 안에서 DB 조회가 반복되면 테스트와 변경이 어려워집니다.
   - 개선: 규칙은 순수 메서드로, 조회 조건은 repository/query service 또는 manager/queryset으로 분리합니다.

4. **Medium: 상태 전이가 단순 필드 대입으로 열려 있는지**
   - `self.status = "paid"`가 여러 곳에 흩어져 있으면 불변식이 깨지기 쉽습니다.
   - 개선: `pay()`, `cancel()`, `ship()` 같은 도메인 언어 메서드로 전이를 닫고, 잘못된 전이는 도메인 예외로 막습니다.

5. **Low: 값 객체가 원시 타입으로 흩어져 있는지**
   - 금액, 수량, 기간, 주소 같은 개념이 `int`, `str`로만 있으면 규칙 중복이 생깁니다.
   - 개선: 복잡한 개념부터만 Value Object로 추출합니다. 단순 CRUD 필드까지 전부 추상화할 필요는 없습니다.

검토할 모델 파일이나 `models.py` 내용을 보내주면, 실제 라인 기준으로 fat model 여부와 개선안을 위험도 순서로 정리하겠습니다.

---
> **관련 스킬 참조:**
> - Django model 책임 분리 / Clean Architecture 리뷰 → **architecture-implementation-patterns**, **architecture-ddd**, **implementation-cleancode** 스킬