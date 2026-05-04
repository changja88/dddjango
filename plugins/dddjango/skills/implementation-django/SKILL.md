---
name: implementation-django
description: >
  Use when the user asks to write Django code, create models, review
  views, optimize queries, set up project structure, write Django tests,
  add a service layer, create migrations, configure settings, or refactor
  Django code. Covers Django 5.x/LTS 5.2, project structure, model design,
  QuerySet optimization, CBV/FBV, signals, caching, security, testing, and
  service layer patterns. Use for any Django code task, even small changes
  like adding a model field. For API endpoints use implementation-django-ninja;
  for templates/static/TemplateView use implementation-django-web; for Python
  conventions use implementation-python; for clean code use
  implementation-cleancode; for architecture patterns use
  architecture-implementation-patterns; for REST API design use
  architecture-api.
---

# Django 프레임워크 컨벤션과 패턴

이 스킬은 Django 고유의 컨벤션, 패턴, 관용구를 다룬다.
Django 5.x(LTS 5.2)를 기준선으로 한다. API 엔드포인트(Django Ninja)는
implementation-django-ninja에 위임한다. 웹 페이지(템플릿, 정적 파일,
디자인 시스템, TemplateView)는 implementation-django-web에 위임한다.
언어 비종속적 원칙(네이밍, SOLID, 디자인 패턴)은 implementation-cleancode에
위임한다. Python 전용 관용구(타입 힌트, dataclasses, async)는
implementation-python에 위임한다. 일반 RDB 설계 원칙(정규화, 인덱스
아키텍처, 격리 수준)은 architecture-db에 위임한다. 아키텍처 패턴
(헥사고날, CQRS, 이벤트 소싱)은 architecture-implementation-patterns에
위임한다. REST API 설계 원칙(엔드포인트, 상태 코드, 버저닝)은
architecture-api에 위임한다.

**DRF(Django REST Framework)는 사용하지 않는다. API 구현에는 Django Ninja를
사용한다.** DRF 코드(Serializer, ViewSet, APIView, permission_classes)를
발견하면 Django Ninja 패턴으로 전환을 권고한다.

**기준 요구사항 — 모든 모드에 적용:**
- Django의 설계 철학을 따른다: Loose Coupling, Less Code, DRY,
  Explicit is Better Than Implicit, Consistency.
- Django 5.x 기능(db_default, GeneratedField, CompositePrimaryKey)을
  적절히 사용한다. 현대적 대안이 있을 때 deprecated 패턴을 사용하지 않는다.
- Django의 공식 코딩 스타일을 따른다: black 포매터, 88자 줄,
  6그룹 정렬 규칙의 isort import.

아래 섹션에서 다루는 주제에 대해 작업할 때, 상세한 컨벤션과 코드 예제를
위해 연결된 참조 파일을 읽는다.

**참조 파일 로딩 규칙:**
- Writing 모드: 아래 주제와 관련된 코드를 생성하기 전에 해당 참조 파일을 먼저 읽는다.
- Review 모드: 리뷰 결과를 확정하기 전에 인용한 모든 컨벤션의 참조 파일을 읽는다.
- Refactoring 모드: 변경 사항을 제시하기 전에 적용한 각 패턴의 참조 파일을 읽는다.

## 응답 구조

모든 응답은 다음 구조를 따른다:

1. **[주요 내용]** -- 모드에 따른 코드, 리뷰, 리팩터링 결과
2. **[관련 스킬 참조]** -- 사용자의 다음 단계를 안내하는 연결점

이 스킬은 11개의 상호 연결된 스킬 체계의 일부이다.
사용자는 현재 작업 후 어떤 스킬을 호출해야 하는지 모르는 경우가
많으므로, 관련 스킬 참조가 워크플로우의 자연스러운 연결을 만든다.

ALWAYS use this exact template for the closing section:
```
---
> **관련 스킬 참조:**
> - [topic] → **[skill-name]** 스킬
```

## 운영 모드

사용자의 요청에 따라 모드를 선택한다:
- **Writing**: 사용자가 Django 코드 생성, 구현, 작성을 요청
- **Review**: 사용자가 기존 Django 코드의 리뷰, 검토, 평가를 요청
- **Refactoring**: 사용자가 Django 코드의 리팩토링, 개선, 현대화를 요청

의도가 모호한 경우 Writing 모드를 기본으로 한다.

요청이 여러 모드에 걸치는 경우(예: "리뷰하고 리팩토링해줘"), Review를 먼저 적용한 후 같은 코드에 Refactoring을 적용한다.

### Writing 모드

모든 Django 컨벤션을 묵시적으로 적용한다. 컨벤션을 설명하는 인라인 주석 없이
관용적인 Django 코드를 작성한다. 코드가 스스로 말하게 한다.

적용할 핵심 컨벤션:

**프로젝트 구조.** 잘 정리된 프로젝트는 대규모 코드베이스를 유지보수 불가능하게 만드는 "하나의 앱에 모든 것" 안티패턴을 방지한다. `config/`에 설정, `apps/`에 도메인 앱을 배치하는 Two Scoops 레이아웃을 사용한다. 설정을 base/local/production/test로 분리한다. `django-environ`을 통해 비밀을 환경 변수에 보관한다. 앱 이름은 간결한 복수형(`users`, `orders`)으로 한다. 앱의 목적을 한 문장으로 설명할 수 없으면 분할이 필요하다.

**모델 설계.** 모델은 모든 Django 프로젝트의 기반이다 — 올바르게 설계하면 연쇄적인 설계 문제를 방지할 수 있다. Fat Model, Thin View 원칙을 따른다. 공식 필드 순서를 사용한다: db 필드 → managers → Meta → `__str__` → `save()/delete()` → `get_absolute_url()` → 커스텀 메서드. 불리언 플래그 남발 대신 `TextChoices`/`IntegerChoices`를 사용한다. 공유 필드에는 Abstract Base Classes를 사용한다. 다중 테이블 상속을 피한다(ABC + 명시적 FK 선호). Python과 DB 수준 모두에서 검증을 위해 `clean()` + `CheckConstraint`를 사용한다.

**QuerySet 패턴.** N+1 쿼리는 가장 흔한 Django 성능 문제이다 — `select_related`와 `prefetch_related`를 배우면 완전히 방지할 수 있다. 체이닝 가능한 필터링을 위해 커스텀 QuerySet 메서드를 정의한다. FK/O2O에 `select_related()`, M2M/역방향 FK에 `prefetch_related()`, 조건부 프리페치에 `Prefetch()`를 사용한다. 배치 작업에 `bulk_create`/`bulk_update`/`update()`를 사용한다. 출력에 필요 없는 계산 필드에 `annotate()`와 `alias()`를 사용한다.

**뷰.** 올바른 뷰 패턴을 선택하면 불필요한 보일러플레이트와 이해할 수 없는 추상화를 모두 피할 수 있다. 표준 CRUD에는 Generic CBV로 시작한다. 명시적 제어 흐름이 필요하면 FBV를 사용한다. 교차 관심사에는 Mixin 합성을 사용한다(체인 3개 이하 유지). 첫 번째 매개변수는 항상 `request`로 명명한다. 인증에 `LoginRequiredMixin`/`@login_required`를 사용한다.

**폼과 검증.** Django의 폼 검증 파이프라인은 특정 순서로 실행된다 — 이를 이해하면 미묘한 버그를 방지할 수 있다. 명시적 `fields`와 함께 ModelForm을 사용한다(`__all__`이나 `exclude` 사용 금지). 필드별 검증에 `clean_<fieldname>()`, 교차 필드 검증에 `clean()`을 구현한다. 모델과 폼 간에 검증기를 재사용한다.

**API 레이어.** API 엔드포인트는 DRF가 아닌 Django Ninja로 구현한다.
Django Ninja 패턴(Schema, Router, 인증, 페이지네이션)은
implementation-django-ninja에 위임한다. 기존 코드에서 DRF 코드를
발견하면 Django Ninja로의 마이그레이션을 권장한다.

**시그널.** 시그널은 디버깅을 어렵게 만드는 보이지 않는 결합을 생성한다 — 직접 결합이 불가능할 때만 사용해야 한다. 서드파티 모델 훅이나 순환 의존성 해소에만 시그널을 사용한다. 같은 앱의 로직에는 `save()` 오버라이드나 서비스 함수를 선호한다.

**마이그레이션.** 마이그레이션은 배포 산출물이다 — 작고, 리뷰되고, 테스트된 마이그레이션이 프로덕션 인시던트를 방지한다. 마이그레이션을 작게 유지한다. `sqlmigrate`로 생성된 SQL을 확인한다. 데이터 마이그레이션에서 `apps.get_model()`을 사용한다. 무중단 배포를 위해: nullable 컬럼 추가 → 백필 → 제약조건 추가.

**성능.** 최적화 전에 프로파일링한다 — 조기 최적화는 측정 가능한 이점 없이 복잡성을 추가한다. `save(update_fields=...)`로 변경된 필드만 업데이트한다. 원자적 카운터 업데이트와 동시 필드 수정(재고, 조회수, 잔액)에 `F()` 표현식을 사용하여 레이스 컨디션을 방지한다. queryset 불리언 평가 대신 `exists()`, `len()` 대신 `count()`를 사용한다. 테스트에서 `assertNumQueries`를 사용한다. 추측이 아닌 프로파일링 기반으로 데이터베이스 인덱스를 추가한다.

**캐싱.** 명확한 무효화 전략 없는 캐싱은 재현하기 어려운 오래된 데이터 버그를 생성한다. 적절한 수준을 사용한다: 전체 응답에는 per-view, 부분에는 template fragment, 세밀한 제어에는 low-level. 캐시 키에 버전 정보를 포함한다. 모델 저장 시 관련 캐시를 삭제한다.

**보안.** Django의 내장 보안 기능은 강력하지만 실수로 비활성화될 수 있다. 강력한 정당성 없이 CSRF 보호를 우회하지 않는다. raw SQL에서 파라미터화된 쿼리를 사용한다. 모든 프로덕션 보안 헤더를 설정한다. 배포 전에 `manage.py check --deploy`를 실행한다.

**테스팅.** 올바른 TestCase 클래스는 테스트 속도와 신뢰성 모두에 영향을 미친다. 대부분의 테스트에 `TestCase`, DB가 필요 없는 테스트에 `SimpleTestCase`를 사용한다. 테스트 데이터에 Factory Boy를 사용한다. N+1 회귀를 잡기 위해 `assertNumQueries`를 사용한다. 픽스처와 깔끔한 어설션을 위해 `pytest-django`를 사용한다.

**서비스 레이어.** 모델이 500줄을 초과하면 비즈니스 로직을 서비스로 추출하여 각 레이어의 집중도를 유지한다. 모델 파일이 500줄을 초과하거나, 로직이 여러 모델에 걸치거나, 외부 서비스 호출이 모델 로직과 혼합될 때 서비스 함수를 도입한다. `<entity>_<action>` 네이밍을 따른다. 읽기 전용 쿼리 로직에 셀렉터를 사용한다. 트랜잭션이 성공적으로 커밋된 후에만 실행되어야 하는 부수 효과(이메일, 알림, 외부 API 호출)에 `transaction.on_commit()`을 사용한다.

> Reference: see `references/` for detailed conventions with examples.

### Review 모드

잘 구조화된 Django 코드를 리뷰할 때는 개선 사항을 나열하기 전에 코드의
잘된 점을 인정한다. 품질이 낮은 코드를 리뷰할 때는 가장 영향력 있는
문제부터 집중한다.

각 발견 사항을 다음 형식으로 작성한다:

```
[Convention] -- 이것이 관용적 Django가 아닌 이유 설명
```

리뷰를 확정하기 전에 이 체크리스트의 모든 항목을 확인한다:

- [ ] 프로젝트 구조: 설정 분리, 앱 격리, 순환 의존성 없음
- [ ] 모델 필드 순서: fields → managers → Meta → __str__ → save → 커스텀 메서드
- [ ] 불리언 플래그 남발: TextChoices/IntegerChoices여야 함
- [ ] 루프 내 FK/M2M 접근 시 select_related/prefetch_related 누락
- [ ] 뷰 또는 템플릿에서 N+1 쿼리
- [ ] 특정 필드만 변경 시 update_fields 없는 save()
- [ ] 같은 앱 로직에 시그널 사용 (직접 호출 또는 서비스여야 함)
- [ ] ModelForm에서 fields = "__all__" 또는 exclude
- [ ] DRF Serializer/ViewSet 사용 (Django Ninja로 전환 필요)
- [ ] Abstract Base Class로 충분한 곳에서 다중 테이블 상속
- [ ] 문자열 보간을 사용한 raw SQL (SQL 인젝션 위험)
- [ ] CSRF 보호 누락 또는 정당성 없는 @csrf_exempt
- [ ] 4개 이상의 Mixin 또는 깊이 커스터마이즈된 제네릭 뷰를 가진 CBV
- [ ] 모델/서비스에 있어야 할 비즈니스 로직이 포함된 Fat 뷰
- [ ] 성능 크리티컬 테스트 경로에서 assertNumQueries 누락
- [ ] 적용 가능한 곳에서 Django 5.x 기능 미사용 (db_default, GeneratedField)

### Refactoring 모드

리팩토링 시 변경 전/후를 보여주고 각 변경의 이유를 명시한다.
각 변경을 특정 Django 컨벤션에 연결하여 근거를 추적 가능하게 한다.
각 변경을 다음 형식으로 작성한다:

```
[Before]
<원본 코드>

[After]
<개선된 코드>

[Reason] Convention -- 이 변경이 Django 모범 사례를 따르는 이유 설명
```

변경 사항을 제시하기 전에 아래의 모든 적용 가능한 개선을 적용한다:

- [ ] 구조화되지 않은 설정 -> base/local/production/test로 분리
- [ ] 불리언 플래그 필드 -> TextChoices/IntegerChoices로 대체
- [ ] 다중 테이블 상속 -> Abstract Base Class + FK로 변환
- [ ] prefetch/select_related 누락 -> 접근 패턴 기반으로 추가
- [ ] 루프 내 개별 save() -> bulk_update/update()로 대체
- [ ] 같은 앱 시그널 -> save() 오버라이드 또는 서비스 함수로 변환
- [ ] fields = "__all__" -> 명시적 필드 목록으로 대체
- [ ] 문자열 보간 raw SQL -> 파라미터화된 쿼리로 변환
- [ ] 비즈니스 로직이 있는 Fat 뷰 -> 모델 메서드 또는 서비스로 추출
- [ ] DRF Serializer/ViewSet -> Django Ninja Schema/Router로 변환
- [ ] 뷰 내 bare queryset -> 커스텀 Manager/QuerySet으로 추출
- [ ] 모델 검증 누락 -> clean() + CheckConstraint 추가
- [ ] 레거시 Django 패턴 -> Django 5.x 기능으로 업그레이드

개별 변경 후에는 **전체 리팩토링된 코드**를 제공하여 사용자가
모든 것이 어떻게 맞아떨어지는지 볼 수 있게 한다.

---

## 응답 작성 직전 체크리스트 (필수)

### 공통
- [ ] DRF 사용 금지 — 모든 API는 Django Ninja
- [ ] BooleanField 남발 금지 (status TextChoices로 표현)
- [ ] 같은 앱 내 post_save 시그널 회피 (서비스 레이어로 명시 호출)

### 작성 모드
- [ ] **selectors 함수 패턴 (api/selectors.py에 read 전용 함수) 사용**
- [ ] **이메일/외부 API 알림은 transaction.on_commit으로 실제 코드 작성 (멘션만이 아닌 실제 호출)**

### 리뷰 모드
- [ ] N+1 가능성 있는 쿼리에 assertNumQueries 회귀 방지 테스트 권고
- [ ] LoginRequiredMixin / PermissionRequiredMixin 누락된 뷰는 인증 필수 추가 지적
- [ ] [Convention: 한 줄 요약] -- 상세 형식 사용
- [ ] **`datetime` 필드명이 Python 빌트인 `datetime`과 충돌함을 지적 (다른 이름 권고)**
- [ ] **Meta 클래스의 `ordering`/`indexes`/`verbose_name` 누락 지적**
- [ ] **모델 `__str__` 메서드 누락 지적**

### 리팩토링 모드
- [ ] 컬럼 rename(scheduled_at, status 등)은 무중단 배포 3단계 명시:
      1단계 add 새 컬럼 + dual write,
      2단계 backfill 기존 데이터,
      3단계 drop 기존 컬럼 + 코드 정리
- [ ] 알림/이메일/외부 API 호출은 transaction.on_commit으로 트랜잭션 후 처리
- [ ] LoginRequiredMixin / 권한 데코레이터 추가 (인증 누락 뷰)
- [ ] 변경 사항을 조각으로 나열하지 말고 마지막에 전체 통합 코드 블록 제공
- [ ] [Before] / [After] / [Reason] 포맷 일관 적용
- [ ] **settings 보안 강화 시 `X_FRAME_OPTIONS = 'DENY'` 추가**
- [ ] **API 작성/리팩토링 시 [Reason]에 "DRF 미사용 — Django Ninja만 사용" 명시**
- [ ] **settings 보안 강화 시 manage.py check --deploy 명령어 안내**
- [ ] **transaction.on_commit으로 부수효과 분리 — 멘션만이 아닌 실제 코드 블록 포함**
- [ ] **API 엔드포인트에 LoginRequiredMixin 또는 auth=django_auth 실제 적용 (말로만이 아닌 코드 변경)**

### 잔여 디테일 정밀도 (회귀 방지 — 절대 누락 금지)

리뷰/리팩토링 모드에서 다음 3개 항목은 표면적인 일반 지적("Choices를 쓰세요", "권한 검사하세요", "rename은 단계적으로")으로 회귀하기 쉽다. 반드시 아래의 정확한 형태로 작성한다.

- [ ] **리뷰 모드에서 `STATUS_CHOICES = (("scheduled", "예정"), ...)` 형태의 튜플 리스트를 발견하면 → "이 튜플을 `class Status(models.TextChoices): SCHEDULED = "scheduled", "예정"` 형태의 TextChoices 클래스로 교체할 것"이라는 명시적 교체 명령으로 작성. "TextChoices를 권장합니다"는 회귀 표현으로 간주.**
- [ ] **리뷰 모드의 권한 검사 지적은 (1) 인증 누락(LoginRequiredMixin)과 (2) 권한 분리(환자는 본인 예약만, 의사는 본인 환자 예약만 — `get_queryset()`에서 `request.user`로 filter)를 **별도 항목 2개**로 분리해 작성. 한 항목으로 합치는 것은 회귀.**
- [ ] **리팩토링 모드에서 컬럼 rename(`date` → `scheduled_at`, `status` 컬럼명 변경 등)을 제시할 때는 **컬럼별로** 무중단 3단계 절차를 코드와 함께 명시: ① `add` 마이그레이션 (새 컬럼 nullable + dual write 코드) → ② `backfill` 마이그레이션 (RunPython 또는 SQL UPDATE) → ③ `drop` 마이그레이션 (구 컬럼 제거 + 코드 정리). status 한 컬럼에만 적용하고 date는 단순 rename으로 끝내는 것은 회귀.**
- [ ] **리뷰 모드에서 같은 의사-시간대 중복 방지에 대해서는 (1) DB 제약 `Meta.constraints = [UniqueConstraint(fields=["doctor", "scheduled_at"], name="...")]`(또는 CheckConstraint)과 (2) Python 수준 `clean()` 검증 — **이중 방어**를 모두 지적. 둘 중 하나만 지적하는 것은 회귀(DB 제약은 race condition 방어, clean()은 폼/admin UX 검증 — 둘 다 필요).**
- [ ] **리팩토링 모드에서 `Appointment.objects.get(pk=pk)` 패턴은 반드시 `get_object_or_404(Appointment, pk=pk)`로 교체하는 [Before]/[After]를 별도 항목으로 제시. selector/services 패턴으로 추출하더라도 selector 내부에서 `get_object_or_404` 사용을 명시. 단순 selector 추출만으로 끝내고 404 처리를 명시하지 않으면 회귀.**
- [ ] **리팩토링 모드에서 모델 Meta.constraints에는 같은 의사-시간대 중복 방지를 위한 `UniqueConstraint(fields=["doctor", "scheduled_at"], name="unique_doctor_schedule")`를 반드시 추가(취소 상태 제외 등 condition 포함 가능). CheckConstraint만 추가하고 UniqueConstraint를 빠뜨리는 것은 회귀.**

---

## 1. 설계 철학과 코딩 스타일

Django의 공식 설계 철학(Loose Coupling, Less Code, DRY,
Explicit > Implicit)과 코딩 스타일(black, isort 6그룹 import,
템플릿 컨벤션)이 기반을 형성한다. 모델 필드 순서 규칙을 따른다.
열거형 필드에 `TextChoices`/`IntegerChoices`를 사용한다.

> Reference: `references/design-style.md`

## 2. 프로젝트 구조와 설정

`config/`과 `apps/`를 가진 Two Scoops 레이아웃을 사용한다. 설정을
base/local/production/test로 분리한다. 비밀에 `django-environ`을 사용한다.
앱 이름은 간결한 복수형으로 한다. 설정에 느리게 접근한다(모듈 import 시점이 아닌).

> Reference: `references/project-structure.md`

## 3. 모델 설계 패턴

Fat Model, Thin View. 공유 필드에 Abstract Base Classes. 동작만 다른
경우 Proxy 모델. 검증에 `clean()` + `CheckConstraint`. 금액에
`DecimalField`, 상태에 `TextChoices`.

> Reference: `references/model-design.md`

## 4. QuerySet과 Manager 패턴

체이닝 가능한 필터링을 위한 커스텀 QuerySet 메서드. FK/O2O에
`select_related`, M2M/역방향에 `prefetch_related`. 조건부 쿼리에
`Prefetch()`. 부분 로딩에 `only()`/`defer()`. 계산 필드에
`annotate()`/`alias()`. 배치 쓰기에 벌크 작업.

> Reference: `references/queryset-manager.md`

## 5. 뷰 패턴: CBV와 FBV

표준 CRUD에 Generic CBV. 복잡한 커스텀 로직에 FBV. 교차 관심사에
Mixin 합성. 첫 번째 매개변수는 항상 `request`.
`get_object_or_404`와 올바른 HTTP 메서드 처리를 사용한다.

> Reference: `references/views.md`

## 6. 폼과 검증

명시적 `fields`와 함께 ModelForm. 필드별에 `clean_<fieldname>()`,
교차 필드 검증에 `clean()`. 재사용 가능한 검증기.
검증 순서를 이해한다: Field.clean → clean_fieldname → clean.

> Reference: `references/forms-validation.md`

## 7. API 레이어 (Django Ninja)

API 엔드포인트는 Django Ninja로 구현한다. 모든 Django Ninja 패턴
(Schema, Router, 인증, 페이지네이션, 필터링, 에러 처리)은
implementation-django-ninja 스킬을 참조한다.

**DRF(Django REST Framework)는 사용하지 않는다.** 기존 DRF 코드를
발견하면 Django Ninja로의 전환을 안내한다.

## 8. 시그널

서드파티 모델 훅이나 순환 의존성 해소에만 사용한다.
같은 앱 로직에는 사용을 피한다. 시그널은 동기적이며 예외는
트리거 함수로 전파된다.

> Reference: `references/signals.md`

## 9. 마이그레이션

작게 유지한다. `sqlmigrate`로 SQL을 확인한다. 데이터 마이그레이션에서
`apps.get_model()`을 사용한다. 무중단 배포를 위한 3단계 접근:
nullable 추가 → 백필 → 제약조건.

> Reference: `references/migrations.md`

## 10. 성능과 캐싱

부분 업데이트에 `save(update_fields=...)`. queryset 평가 대신
`exists()`/`count()`. 프로파일링 기반 데이터베이스 인덱스. Per-view,
fragment, low-level 캐싱. 버전 기반 캐시 키.

> Reference: `references/performance-caching.md`

## 11. 보안

CSRF, XSS, SQL 인젝션 보호는 내장되어 있지만 우회될 수 있다.
프로덕션 설정 체크리스트. 파라미터화된 raw SQL. 인증과 인가 패턴.

> Reference: `references/security.md`

## 12. 테스팅

대부분의 테스트에 `TestCase`, DB 불필요 시 `SimpleTestCase`. 데이터에
Factory Boy. 픽스처에 `pytest-django`. 성능에 `assertNumQueries`.
`assertTrue(x)` 대신 `assertIs(x, True)`.

> Reference: `references/testing.md`

## 13. 미들웨어

요청은 MIDDLEWARE 목록을 위에서 아래로 통과하고, 응답은 아래에서 위로.
`__init__` + `__call__` + 선택적 `process_exception`을 가진 커스텀
미들웨어. 미들웨어를 경량으로 유지한다.

> Reference: `references/middleware.md`

## 14. 서비스 레이어 아키텍처

모델이 500줄을 초과하거나 로직이 모델에 걸칠 때 도입한다.
`<entity>_<action>` 네이밍. 쓰기에 서비스, 읽기에 셀렉터.
Django ORM은 Active Record이다 — 완전한 Repository 패턴은 거의 필요 없다.

> Reference: `references/service-layer.md`

## 15. Django 5.x 기능

데이터베이스 계산 기본값에 `db_default`. 저장/가상 계산 컬럼에
`GeneratedField`. `CompositePrimaryKey`(5.2).
`LoginRequiredMiddleware`(5.1). 딕셔너리 기반 choices(5.0).

> Reference: `references/django5.md`

---

## 16. 고급 ORM 표현식

쿼리 내 조건부 로직에 Case/When. 분석 계산에 윈도우 함수(Rank,
Lag, Lead). 상관 쿼리에 Subquery/OuterRef. 효율적인 불리언
검사에 Exists(). 데이터베이스 함수(Coalesce, Cast, Concat,
Extract/Trunc). QuerySet의 집합 연산(union, intersection, difference).

> Reference: `references/advanced-orm.md`

---

## 17. PostgreSQL 전용 기능

JSONField 쿼리(포함, 키 존재, 경로 조회).
GIN 인덱스를 가진 ArrayField. 전문 검색(SearchVector,
SearchQuery, SearchRank, TrigramSimilarity). 겹침 방지를 위한
ExclusionConstraint를 가진 Range 필드. PostgreSQL 집계
(ArrayAgg, StringAgg, JSONBAgg). 특수 인덱스(GIN, GiST,
BRIN, Bloom).

> Reference: `references/postgres-specific.md`
