**주요 내용**

현재 `/private/tmp/dddjango-codex-eval` 작업 디렉터리에는 Django 모델 파일이 없습니다. `models.py`, `*models*.py`, `manage.py`, `pyproject.toml`을 검색했지만 파일이 없어서 이 모델이 실제로 fat model인지 라인 기준 리뷰는 할 수 없습니다. `config.toml`도 현재 디렉터리에는 없고, 관련 Codex 설정은 `../dddjango-codex-home/.codex/config.toml`에서만 확인됐습니다.

모델 코드를 붙여주시거나 파일 경로를 주시면 아래 기준으로 바로 리뷰하겠습니다.

**리뷰 기준**

Django 관점에서는 “Fat Model, Thin View”가 무조건 나쁜 패턴은 아닙니다. 모델에 상태 전이, 불변식 검증, 도메인 용어 기반 메서드가 있는 것은 오히려 좋습니다. 예를 들어 `order.confirm()`, `appointment.cancel()`, `bid.place()`처럼 데이터를 가진 객체가 자기 규칙을 지키는 구조는 정상적인 rich domain model입니다.

클린 아키텍처 관점에서 fat model로 볼 가능성이 큰 신호는 다음입니다.

| 항목 | 문제 |
|---|---|
| 모델이 이메일, 외부 API, 파일 I/O, 결제 SDK, 알림 발송을 직접 호출 | 도메인이 인프라에 의존합니다. 부수효과는 application service에서 `transaction.on_commit()` 또는 outbox로 분리하는 편이 낫습니다. |
| 모델 메서드가 여러 애그리거트를 조회/수정/save | 애그리거트 경계가 커지고 트랜잭션 책임이 모델 안으로 새어 들어옵니다. |
| `save()` override에 유스케이스 흐름이 들어 있음 | 영속성 훅이 숨은 application service가 되어 테스트와 변경이 어려워집니다. |
| 모델이 `request`, `user`, permission, API 응답 dict를 알고 있음 | presentation/application 관심사가 domain/persistence model에 침투한 것입니다. |
| 상태가 여러 BooleanField로 흩어짐 | 불가능한 상태 조합이 생깁니다. `models.TextChoices` 기반 단일 `status`로 바꾸는 편이 낫습니다. |
| `ValueError`, `Exception`이 도메인 실패를 표현 | `AppointmentAlreadyCancelledError`, `BidTooLowError` 같은 도메인 예외가 더 명확합니다. |
| DB 제약 없이 Python 검증만 있음 | race condition에 취약합니다. `clean()`과 `CheckConstraint`/`UniqueConstraint`를 함께 둬야 합니다. |
| 모델이 500줄 이상이고 변경 이유가 많음 | Django 서비스/selector, 도메인 서비스, 값 객체 분리를 검토할 시점입니다. |

판정은 이렇게 나눠 보는 게 실용적입니다.

- **좋은 rich model**: 자기 상태와 가까운 규칙을 캡슐화한다. 예: `cancel()`, `mark_paid()`, `reschedule()`이 상태 전이를 검증한다.
- **나쁜 fat model**: 유스케이스 조율, 트랜잭션, 외부 I/O, 권한, API 포맷팅, 다른 애그리거트 저장까지 맡는다.
- **클린 아키텍처 엄격 적용 시**: Django `models.Model` 자체는 프레임워크/DB 세부사항이므로 순수 도메인 엔티티와 분리하고, Django ORM 모델은 adapter/data model로 두는 설계를 검토합니다.
- **Django 실용 적용 시**: 단순 CRUD 또는 지원 도메인은 Active Record 스타일을 유지하되, 복잡한 비즈니스 규칙과 외부 의존성만 application service, domain service, repository port로 빼는 정도가 적절합니다.

모델 코드와 함께 관련 view/service/manager/queryset도 있으면 fat model 여부를 더 정확히 볼 수 있습니다. fat model 문제는 모델 파일만 봐서는 반대로 “view가 너무 fat해서 모델이 얇은지”를 놓치기 쉽습니다.

---
> **관련 스킬 참조:**
> - Django 모델/서비스 분리 리뷰 → **implementation-django** 스킬
> - 클린 아키텍처 의존성 방향 리뷰 → **architecture-implementation-patterns** 스킬
> - 애그리거트/값 객체/도메인 이벤트 리뷰 → **architecture-ddd** 스킬
> - 책임 분리와 God Class 판단 → **implementation-cleancode** 스킬