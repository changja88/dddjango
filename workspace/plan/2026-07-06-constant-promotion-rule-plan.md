# 상수화 규약 구현 계획 (적대 리뷰 반영판 v2)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax.
> v1 대비: 정합성·실용성 적대 리뷰 29건 중재 반영 — 백스톱 채택(Task 9)·`.value` 평탄화·`==` 비교·기존 예제 정리(Task 3 확장)·SKILL.md 라우팅·reviewer grandfather/배타.

**Goal:** 스펙(`workspace/design/2026-07-06-constant-promotion-rule-design.md`, 리뷰 2 반영본)을 dddjango 플러그인에 반영: 스킬 문서 7종 + SKILL.md 라우팅 + reviewer 항목 + **18번째 결정적 백스톱** + codex 미러 동기.

**Architecture:** 정본 `dddjango/` 수정 → final.md는 `corpus_mirror_sync --write` 자동 전파, SKILL.md·agents·scripts는 수동 미러. 집행은 db_table 동형 2층: 백스톱(FP≈0 직접형) + reviewer(의미 사각).

## Global Constraints

- 기존 문체·출처 태그(`[PP]`·`[Ref]`)·`§` 상호참조 준수. 비교 연산자는 규약상 `==`(`is` 금지 — StrEnum str-흐름).
- 소유 지도: 판정 원리·허용 목록·소비 규율 = cleancode §2.14(전문), 나머지 문서는 요지 1줄+참조. 계층·판정 소유 = architecture-ddd. Django 표기 = implementation-django. 테스트 역방향 = implementation-test §15.4.
- ORM `default=`는 `.value` 평탄화(EnumSerializer 산 참조 방지). CheckConstraint는 파일 관례 `check=`.
- 게이트 17→18: commands·README·corpus_mirror_sync 주석 카운트 갱신(AGENTS.md는 카운트 서술 있으면).
- 커밋은 전체 검증 후 단일 feat 커밋(사용자 확인 후).

---

### Task 1: discipline-cleancode §2.14 신설 + SKILL.md 라우팅

**Files:** `dddjango/skills/discipline-cleancode/references/final.md`(§2.13 끝 ~291행, `## 3.` 306행 직전), `dddjango/skills/discipline-cleancode/SKILL.md`(핵심 원칙 불릿 + §2 행)

- [ ] Step 1: final.md에 삽입 (목차는 챕터 단위라 갱신 없음)

```markdown
### 2.14 매직 값과 상수 승격 판정 [PP] [Ref]

리터럴을 상수·Enum으로 승격할지는 "문자열이냐"가 아니라 **오타의 실패 모드**와 **철자의 계약성**으로 판정한다. 리터럴 오타는 조용한 항상-False로 잠복하고, 심볼 오타는 `AttributeError`로 즉사한다.

**승격 판정 원리**:

1. 값들의 **닫힌 집합의 원소**이면서 **우리 코드가 그 값으로 분기·판정·필터**하거나 계약(wire·DB 제약)에 노출하면 **집합 단위 타입**으로 — 1곳째부터. 도메인 상태·종류(type code)가 여기다. 낱개 상수 나열(`DUPLICATE_REPLAY = "duplicate_replay"`)이 아니라 집합 하나의 타입으로 — "이 상태가 전부인가"를 한 곳에서 답한다. **과승격 방지**: 분기 없이 저장·중계만 하는 pass-through 값은 강제 대상이 아니고, 상류가 소유한 열린 집합은 분기에 쓰는 값만 멤버로 두되 미지 값 처리 방침(UNKNOWN 폴백 또는 명시 거부)을 함께 정한다. 이름이 type/kind라는 이유만으로 승격하지 않는다.
2. 닫힌 집합이 아니라도 **같은 지식의 철자를 서로 다른 파일 2곳 이상이 공유**하면 명명 상수로. 우연히 값이 같을 뿐 다른 지식이면 합치지 않는다(나이 상한 150과 층수 상한 150은 별개). 같은 파일 안 반복이 같은 지식이면 §13.1 지식-중복 판정이 우선한다 — 파일 임계는 승격 *강제* 시점일 뿐 DRY를 완화하지 않는다.
3. 나머지는 리터럴 그대로 둔다.

**리터럴 허용 목록** (승격하지 않는다):

- 사람 대상 서술 — 로그·예외 메시지·이메일 제목(열거가 아니라 문장, 비교 대상 아님)
- Enum·상수 **정의부 자체**의 우변(리터럴의 유일한 서식지)
- `Literal[...]`로 타입이 잠긴 인자 자리(`open(path, "r")` — 타입 체커가 오타를 잡는다)
- 외부 프로토콜이 소유한 문자열(content type·vendor 코드·프로토콜 에러 코드) — 단 분기 조건이 되는 순간 경계(adapter)에서 내부 타입으로 정규화하고 원시 리터럴이 경계 밖으로 새지 않게 한다
- 식별자형·구조 문자열(dict 키·kwargs·separator·설정 키·환경변수명)
- 테스트에서 외부 관찰 계약을 검증하는 **assert 기댓값** — 오히려 리터럴을 강제한다(프로덕션 상수 역수입은 자기참조 오라클; `implementation-test` §15.4). 테스트의 arrange/act(픽스처·필터 준비)는 심볼 권장 — 두 규율은 위치로 갈린다.

**짝 규칙(소비 규율)**: 집합 타입이 선언된 값의 비교·분기·필터·대입·기본값은 반드시 그 심볼로 참조한다 — 선언하고 리터럴로 소비하면 위반이다. 비교는 `==`로 한다(`is` 금지 — StrEnum 값은 경계에서 plain str로 흐르므로 `is`는 수화 누락 시 오타 없이도 조용한 False를 만든다). 단 심볼 치환은 판정 소유 규율을 면책하지 않는다: 도메인 어휘로 진술되는 복합 상태 판정의 1차 시정은 애그리거트 술어·enum 프로퍼티다(`architecture-ddd` §3.2). 값에 검증·연산·불변식이 붙으면(집합의 폐쇄성과 무관하게) Enum이 아니라 값 객체 승격 대상이다(판정은 `architecture-ddd` §3.1 소관).

**숫자 부칙**: 비교·계산에 등장하는 의미 있는 숫자는 1회부터 명명 상수(ruff/pylint magic-value-comparison과 대상 동일·더 강한 수위). `0`·`±1`·루프 인덱스·수식의 본질적 구성 숫자(근의 공식의 2·4)는 면제.
```

- [ ] Step 2: SKILL.md — 핵심 운영 원칙 불릿에 1줄(`매직 값·상수 승격 판정과 심볼 소비 규율은 §2.14 — 닫힌 집합 1곳째 집합 타입·허용 목록·테스트 역방향`), 주제 표 §2 행 끝에 `·매직 값·상수 승격(§2.14)` 추가(기존 표 형식에 맞춤)
- [ ] Step 3: 검증 `grep -n '2.14' final.md SKILL.md`

### Task 2: implementation-python §10.1 보강

**Files:** `dddjango/skills/implementation-python/references/final.md`(≈1208행 기존 마지막 불릿 뒤)

- [ ] Step 1: 불릿 추가

```markdown
- 승격 판정(무엇을 Enum으로 만들지)·리터럴 허용 목록·소비 규율의 소유자는 `discipline-cleancode` §2.14다 — 요지: 닫힌 집합은 1곳째부터 집합 단위 타입으로(낱개 모듈 상수 나열 금지), 선언된 값의 비교·분기·대입은 심볼로만(`state == State.ACTIVE` — `==`를 쓴다, `is`는 StrEnum이 경계에서 plain str로 흐를 때 조용한 False).
- **파생 분류 집합**(terminal set 등)의 지식은 enum이 소유한다 — 1순위는 프로퍼티(`@property def is_terminal(self) -> bool: ...`), 여러 원소를 묶는 상수가 필요하면 enum과 같은 모듈의 `frozenset`(원소는 심볼). 소비처 모듈마다 임의 frozenset을 재정의하지 않는다.
- `Literal` vs `Enum` 분업(PEP 586): 위 불릿의 "지역적 분기 표현이면 `Literal` 가능"은 유지하되, 도메인 개념의 값 집합(상태·종류)은 Enum, 외부 API의 값 의존 계약(`open`의 mode처럼 인자 값에 따라 시그니처가 갈리는 자리)은 `Literal`로 가른다. `Literal`로 잠긴 인자 자리의 리터럴은 타입 체커가 검증하므로 허용이다.
```

- [ ] Step 2: 검증 `grep -n '§2.14' .../implementation-python/references/final.md`

### Task 3: implementation-django — §2.5 재규정 + 기존 예제 정리 + §10.4 + SKILL.md

**Files:** `dddjango/skills/implementation-django/references/final.md`(§2.5 ≈179-206·§4.3 ≈449-470·§5.1 ≈511-532·§11 부분 인덱스 ≈1055·최적화 ≈1087·§16 ≈1455)·`SKILL.md`

- [ ] Step 1: §2.5 — "좋은 예: … (권장)" 주석을 "순수 인프라 필드(도메인 판정 없음): TextChoices 자체 선언"으로 재라벨하고, 코드 블록 뒤에 계층 소유 단락+파생 예시 추가:

```markdown
**계층 소유 — 도메인 판정에 쓰이는 값 집합의 단일 출처는 domain_layer의 `StrEnum`이다.** 위 TextChoices 자체 선언은 도메인 판정에 쓰이지 않는 **순수 인프라 필드에 한정**한다(도메인 상태를 TextChoices로 선언하면 domain이 판정 시 ORM 타입을 역참조 — `architecture-ddd` §3.2). 도메인 상태 필드는 domain Enum에서 파생시킨다. 도메인 판정이 처음 생기는 슬라이스에서 파생형으로 전환한다(값 불변이면 `choices` 변경은 DB 무영향). 기존 TextChoices 관례가 확립된 프로젝트는 `discipline-houserules` §1.1로 그 관례를 따른다.

```python
# domain_layer/order/value_object/order_status.py — 단일 출처
class OrderStatus(StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"

# infra_layer/django_order/models/order_model.py — 파생 (라벨(i18n) 필요 시 명시 매핑 병기)
class OrderModel(models.Model):
    status = models.CharField(
        max_length=20,
        choices=[(s.value, s.name.title()) for s in OrderStatus],
        default=OrderStatus.PENDING.value,  # .value 평탄화 — 멤버 직접 참조는 마이그레이션에 산 enum 참조를 직렬화
    )
```

**`.value` 평탄화**: `default=`·마이그레이션 경계에서 순수 StrEnum 멤버를 직접 두면 `EnumSerializer`가 살아있는 참조(`OrderStatus["PENDING"]` + domain import)를 박는다 — 값 동결(`ChoicesSerializer`)은 `models.Choices` 전용이므로 domain Enum 파생 시 `.value`로 평탄화한다(단일 출처 파생이므로 심볼 소비로 인정). `CheckConstraint`(`check=`)·부분 인덱스 `Q()` 조건도 같은 파생으로 쓴다.

**소비 규율**: `choices`/Enum이 선언된 필드 값의 비교·분기·`.filter()`·대입·`default`는 반드시 심볼로 참조한다 — `.filter(status="pending")` 금지 → `.filter(status=OrderStatus.PENDING)`. 비교는 `==`(`is` 금지 — 필드 값은 plain str). 복합 상태 판정의 1차 시정은 애그리거트 술어·enum 프로퍼티(`architecture-ddd` §3.2). 승격 판정·허용 목록은 `discipline-cleancode` §2.14.
```

- [ ] Step 2: §4.3(boolean 폭발→TextChoices) — 예제 코드는 유지하고 끝에 1줄: `단 이 Status가 도메인 판정(전이·terminal)에 쓰이면 §2.5 계층 소유대로 domain Enum 파생으로 선언한다.`
- [ ] Step 3: §5.1 Post/Manager 예제 — 모듈 레벨 `PostStatus`(TextChoices 또는 상수) 도입 또는 최소 침습으로 `filter(status="published")`류 리터럴을 심볼 참조로 교체(§11 부분 인덱스 `Q(status=…)`·최적화 예시 동일). 예제 구조 훼손이 크면 해당 코드 블록에 심볼 선언 1개 추가로 통일.
- [ ] Step 4: §16 `if order.status != Order.Status.PENDING:` — domain enum 참조(`OrderStatus.PENDING`)로 교정 + 근처에 계층 소유 1줄 참조.
- [ ] Step 5: §10.4 끝 불릿:

```markdown
- **historical value 리터럴 동결**: 마이그레이션 파일 안의 choices·상태·default 값은 살아있는 도메인 Enum을 참조하지 않는다 — Enum 변경이 과거 이력의 의미를 소급 변경하면 안 된다(기존명 보존과 동형). 모델 `default=`를 `.value`로 평탄화하면(§2.5) makemigrations가 리터럴로 동결한다; 멤버를 직접 두면 `EnumSerializer`가 산 참조를 직렬화하므로 금지. 수기 데이터 마이그레이션에서도 Enum import 대신 리터럴을 쓴다.
```

- [ ] Step 6: SKILL.md §2.5 관련 행/불릿에 `계층 소유(도메인 상태=domain StrEnum 파생·TextChoices는 인프라 필드 한정)·소비 규율(.filter 심볼)` 라우팅 추가
- [ ] Step 7: 검증 `grep -n '계층 소유\|.value 평탄화\|historical value' final.md`; `grep -n 'status="published"' final.md` → 잔존 0(§10.4·마이그레이션 예시 제외)

### Task 4: implementation-django-ninja §3.1 불릿

**Files:** `dddjango/skills/implementation-django-ninja/references/final.md`(§3.1 불릿 끝 ≈284행)

- [ ] Step 1: 불릿 추가

```markdown
- enum성 필드(상태·종류)는 `Literal[...]` 또는 `StrEnum`으로 선언해 OpenAPI 계약에 enum으로 노출한다. 도메인 enum에서 파생하되, 계약 안정성을 도메인 리팩터링과 분리해야 하면 경계-로컬 `Literal`로 고정한다(published language — `architecture-ddd` §2.5). 응답 조립·비교에 원시 리터럴을 흩지 않는다(`discipline-cleancode` §2.14 소비 규율).
```

- [ ] Step 2: 검증 `grep -n '경계-로컬' final.md`

### Task 5: architecture-ddd — 판정 소유 뒤 + §2.5 뒤 단락

**Files:** `dddjango/skills/architecture-ddd/references/final.md`(632행 단락 뒤·§2.5 ACL 마무리 ≈360행 뒤)

- [ ] Step 1: 632행 뒤 삽입

```markdown
**상태·종류 값 집합의 표기와 계층 소유 — 단일 출처는 도메인 enum이다.** 생명주기·상태 전이·terminal 여부를 갖는 도메인 상태값과 종류 코드(type code)는 낱개 문자열 상수가 아니라 domain_layer의 `StrEnum`(또는 순수 `Enum`) 하나로 선언하고, ORM `choices`/`CheckConstraint`·presentation Schema는 거기서 파생한다 — import 방향은 infra/presentation→domain만 허용한다(`models.TextChoices` 자체 선언은 도메인 판정에 쓰이지 않는 순수 인프라 필드 한정; ORM `default=` 등 직렬화 경계는 `.value` 평탄화 — `implementation-django` §2.5). 소비는 심볼로만, 비교는 `==`로 한다 — 원시 리터럴 비교는 오타가 조용한 False로 잠복하고, `is`는 str로 흐르는 값에서 수화 누락 시 같은 실패를 오타 없이 만든다. 단 심볼 비교 자체가 목적지가 아니다: 도메인 어휘로 진술되는 복합 상태 판정의 1차 시정은 애그리거트 술어·enum 프로퍼티(§3.3의 `OrderStatus.is_shippable`)이고, 심볼 비교는 그 술어 내부·리포지토리 필터·ACL 정규화 같은 잔여 위치에 남는다(승격 판정·허용 목록은 `discipline-cleancode` §2.14). 값에 검증·연산·불변식이 붙으면(집합의 폐쇄성과 무관하게) enum이 아니라 값 객체 승격 대상이다(§3.1의 `CountryCode`·`PhoneNumber`가 그 예).
```

- [ ] Step 2: §2.5 ACL 마무리 뒤 삽입

```markdown
**BC 간 enum·상수 공유 경계.** 상수·Enum은 기본적으로 그것을 소유한 바운디드 컨텍스트 내부 자산이다 — 다른 BC가 내부 Enum을 직접 import하지 않는다(유비쿼터스 언어는 BC 경계 안에서만 보편 §2.3; 같은 철자라도 컨텍스트마다 다른 개념). BC 간 연결은 published service 계약 타입 또는 wire value로 하고, 같은 wire 값을 BC마다 각자 선언하는 것은 지식의 중복이 아니라 **published language 수용**이다 — 상대 모델의 의미가 어긋나면 그때 ACL로 번역한다. 공용 승격은 **공유 커널 결정**이다: 같은 철자를 넘어 같은 지식임이 확인되고, 결정 가능한 대리 기준으로 **두 BC가 같은 변경 사유로 함께 수정된다는 근거가 명세에 있을 때만** — 공유 범위 최소화 필수(위 표). 승격된 enum은 `common/enum/`에 두며, 공유 커널은 도메인의 일부로 취급되어 domain_layer가 의존할 수 있는 유일한 외부다(배치·의존 예외는 `discipline-houserules`).
```

- [ ] Step 3: 검증 `grep -n '단일 출처는 도메인 enum\|공유 커널 결정' final.md`

### Task 6: implementation-test §15.4 신설 + SKILL.md

**Files:** `dddjango/skills/implementation-test/references/final.md`(`## 16.` 2074행 직전)·`SKILL.md`

- [ ] Step 1: 절 삽입 (목차 갱신 없음 — 챕터 단위)

```markdown
### 15.4 외부 계약 기댓값은 리터럴로 — 프로덕션 상수 역수입 금지 [Google Testing Blog] [Khorikov]

외부 관찰 계약(HTTP 응답 본문·DB 저장값·발행 이벤트 payload)을 검증하는 테스트의 **assert 기댓값**은 완성형 리터럴로 하드코딩한다. 프로덕션 Enum·상수를 import해 기댓값으로 재사용하면 상수 값이 잘못 바뀌어도 테스트가 함께 통과하는 자기참조 오라클(동어반복)이 된다 — wire·DB에 노출된 `.value`는 published/영속 계약이라 그 변경은 내부 리팩터링이 아니라 계약 파괴이고, 리터럴 기댓값의 시끄러운 실패가 의도된 보호다. BC 사유 DB라도 기존 행과의 호환 자체가 계약이다.

```python
# 나쁜 예 — 자기참조 오라클: DeliveryStatus.DELIVERED 값이 "deliverd"로 오타 나도 통과
assert response.json()["status"] == DeliveryStatus.DELIVERED.value

# 좋은 예 — 계약을 리터럴로 고정: 값 회귀 시 시끄럽게 실패
assert response.json()["status"] == "delivered"
```

경계 셋: ① **도메인 내부 단위 테스트**의 심볼 단언(`assert order.status == OrderStatus.DELIVERED`)은 허용 — 거기서의 계약은 전이 행위이지 철자가 아니고, 철자 회귀는 위 계약 테스트가 잡는다. ② 리터럴 동결 대상은 **철자가 곧 계약인 값**(enum 코드·상태 문자열·필드명)이다 — 계산 결과값의 기댓값 표현은 `discipline-tdd` '명백한 데이터'가 소유한다(SUT를 호출하지 않는 독립 산식으로 관계를 드러내는 것 허용). ③ 테스트의 **arrange/act**(픽스처 생성·`.filter()` 준비)는 심볼 사용을 권장한다 — 리터럴 강제는 외부 계약을 관찰하는 assert에만 적용되므로 프로덕션 소비 규율(`discipline-cleancode` §2.14)과 같은 테스트 안에서 충돌하지 않는다.
```

- [ ] Step 2: SKILL.md — §15 또는 핵심 불릿에 `외부 계약 기댓값 리터럴(자기참조 오라클 금지, §15.4)` 라우팅 추가 (§16 '프로덕션 로직 재사용' 행에 `·상수 역수입은 §15.4` 병기로 이원화 해소)
- [ ] Step 3: 검증 `grep -n '15.4' final.md SKILL.md`

### Task 7: discipline-houserules 승격 기준·배치·의존 예외

**Files:** `dddjango/skills/discipline-houserules/references/final.md`(59행 뒤 + §3 표 163행 + 168행 부근)·`SKILL.md`(§1 불릿)

- [ ] Step 1: final.md 59행 문장 뒤 불릿:

```markdown
- **`common/enum/` 승격은 공유 커널 결정이다** — 같은 철자를 넘어 같은 *지식*이고, 두 BC가 같은 변경 사유로 함께 수정된다는 근거가 명세에 있을 때만(`architecture-ddd` §2.5 공유 커널 — 공유 범위 최소화 필수). BC 내부 enum은 그 BC `domain_layer` 소유이고 다른 BC가 직접 import하지 않는다 — 같은 wire 값의 BC별 각자 선언은 중복이 아니라 published language 수용이다. **승격된 공유 커널(`common/enum/`·`common/<project>/`)은 도메인의 일부로 취급되어 domain_layer가 의존할 수 있는 유일한 외부다**(§2 "domain은 아무것도 의존하지 않는다"의 명시 예외 — 프레임워크 비종속이 조건).
```

- [ ] Step 2: §3 표 163행 개정 → `| `common/enum/` | 공유 커널로 승격된 enum(승격 기준: 같은 지식+같은 변경 사유 — §1) | `<domain>_enum.py` |`; 168행 "2개 이상 BC가 실제로 공유할 때만" 문장에 `(enum은 추가로 공유 커널 기준 — 같은 지식일 때만; 같은 wire 값 각자 선언은 정상)` 보강
- [ ] Step 3: SKILL.md §1 불릿(38행 뒤):

```markdown
   - **상수·Enum 배치** — BC 내부 enum은 그 BC `domain_layer/` 소유(단일 출처; ORM `choices`·Schema는 파생·역참조 금지·`default=`는 `.value` 평탄화), 타 BC 직접 import 금지, `common/enum/` 승격은 공유 커널 결정(같은 지식+같은 변경 사유 근거)일 때만. 상세 `references/final.md`·`architecture-ddd` §2.5·§3.2.
```

- [ ] Step 4: 검증 `grep -n '공유 커널' final.md SKILL.md`

### Task 8: discipline-reviewer 항목 신설 + codex 수동 미러

**Files:** `dddjango/agents/discipline-reviewer.md`(**빈혈 불릿(40행) 뒤** 삽입 — "위" 지시어 정합), `codex-dddjango/skills/dddjango-discipline-reviewer/SKILL.md`(동일 위치·동일 문안), `codex-dddjango/skills/discipline-houserules/SKILL.md`(Task 7-Step 3 동일)

- [ ] Step 1: 불릿 삽입(양 파일 동일)

```markdown
- **상수 승격·심볼 소비 규율(백스톱 사각 전담)**: **이번 작업이 touched한 코드만 본다 — untouched 기존 리터럴은 면제(grandfather)**. ① 닫힌 집합의 원소(도메인 상태·종류·wire enum성 문자열)를 우리 코드가 분기·판정하는데 집합 타입(domain `StrEnum`/`choices` 파생) 없이 원시 리터럴로 산재하면 **important**(1곳째부터 승격 — `discipline-cleancode` §2.14; 단 그 산재가 같은-지식 중복 정리 사안이면 위 클린코드 불릿의 DRY로만 분류, 이중 계상 금지). ② Enum/choices가 *선언돼 있는데* 소비처가 리터럴로 비교·`.filter()`·대입하면 **important** — 결정적 백스톱 `check-choices-literal-consumption`이 직접형(`default=` 리터럴·`<Model>.objects.filter(<field>="…")`)을 잡으므로 네가 보는 건 그 사각이다: 변수 우회·간접 queryset(`qs.filter(...)`)·비교식·`__in` 변종. **심볼 치환은 판정 소유 위반을 면책하지 않는다** — 그 사건이 복합 판정의 소유 문제(위 '죽은 도메인 메서드·판정 인프라 누수' 불릿)면 그쪽 하나로만 분류한다. ③ 도메인 판정 값 집합이 `models.TextChoices`로 선언돼 domain이 ORM 타입을 역참조하면 **important**(계층 소유 — 단일 출처는 domain enum·ORM은 `.value` 평탄화 파생; `implementation-django` §2.5. 구조 이주 사안이면 위 파일트리 불릿과 이중 계상 금지 — 값 집합 소유만 여기). ④ 테스트가 **외부 관찰 계약**(HTTP 응답·DB 저장값·이벤트)의 assert 기댓값에 프로덕션 Enum·상수를 역수입하면 **important**(자기참조 오라클 — `implementation-test` §15.4; 테스트 품질 불릿과는 별개 렌즈 — 오라클 자기참조만 여기). **거짓지적 방지(잡지 않는다)**: 도메인 내부 단위 테스트의 심볼 단언·테스트 arrange/act의 심볼 사용, 로그·예외 메시지 등 사람 대상 서술, Enum·상수 정의부 우변, `.value` 평탄화 파생(`default=OrderStatus.PENDING.value`), `Literal[...]`로 잠긴 인자 자리, 외부 프로토콜 소유 문자열(분기 조건인데 adapter 정규화 부재면 nit로만), 설정 키·환경변수명, 마이그레이션 historical value(살아있는 Enum 참조가 오히려 위반 — `implementation-django` §10.4), pass-through 저장·데이터소스 BC의 미승격, 한 파일 로컬 문자열, 우연히 같은 값·다른 지식의 미통합(합치면 오히려 위반). 근거 `discipline-cleancode` §2.14·`implementation-django` §2.5·§10.4·`architecture-ddd` §2.5·§3.2·`implementation-test` §15.4.
```

- [ ] Step 2: codex houserules SKILL.md에 Task 7-Step 3 불릿 동일 반영
- [ ] Step 3: 검증 — 신설 불릿 양쪽 diff 0

### Task 9: 백스톱 check-choices-literal-consumption.py 신설 + 게이트 등록

**Files:** Create `dddjango/scripts/check-choices-literal-consumption.py` + `codex-dddjango/skills/dddjango/scripts/` 미러. Modify: `dddjango/commands/dddjango.md`(17종→18종·목록)·`README.md`·`codex-dddjango/skills/dddjango/SKILL.md`·`workspace/tools/corpus_mirror_sync.py`(주석 "17개"→"18개")·AGENTS.md(카운트 서술 시)

- [ ] Step 1: 스크립트 작성 — `check-db-table.py`의 구조(touched-only git diff·AST·fail-open·exit 규약)를 모델로. 검출 2슬라이스:
  - (a) 클래스 본문의 필드 호출 노드에 `choices=` kwarg가 **심볼 출처**(Name/Attribute/ListComp/GeneratorExp — 리터럴 List/Dict 제외)로 있고 같은 호출에 `default=<str 상수>`가 있으면 위반.
  - (b) touched 파일들의 모델 클래스에서 심볼-choices 필드명 레지스트리를 만들고, `<ModelName>.objects.filter(...)/exclude(...)` 직접 호출형의 kwarg `<field>=<str 상수>` 또는 `<field>__in=[<str 상수>…]`가 레지스트리와 매칭되면 위반.
  - 면제: 경로에 `migrations/`·`test`(디렉터리/파일명 관례)·인라인 리터럴 choices·비-str 상수. 파싱 실패 fail-open. exit 0/2(위반)/기존 게이트 관례 준수.
- [ ] Step 2: 발화 매트릭스 — scratchpad 합성 픽스처 6종: 위반(a)=exit2·위반(b) filter=exit2·위반(b) `__in`=exit2·정상 심볼 소비=0·migrations 경로=0·인라인 choices+리터럴 default=0
- [ ] Step 3: 등록 — commands/dddjango.md 게이트 목록에 ⑱ 추가·"17종"→"18종", README·codex SKILL 동일, corpus_mirror_sync 주석 카운트, codex scripts 디렉터리에 byte-identical 복사
- [ ] Step 4: 검증 — `diff dddjango/scripts/check-choices-literal-consumption.py codex-dddjango/.../check-choices-literal-consumption.py` 0; `grep -rn '17종\|17개' dddjango/ codex-dddjango/ workspace/tools/` 잔존 확인

### Task 10: 미러 동기·검증·기록·커밋

- [ ] Step 1: `python3 workspace/tools/corpus_mirror_sync.py --write` → `--check` exit 0(11/11)
- [ ] Step 2: `claude plugin validate dddjango --strict` pass (codex도 규격 검증 수단 있으면 수행)
- [ ] Step 3: DEVLOG §2에 DR-60(스펙 경로·리뷰 3건 요약·백스톱 번복 근거·발화 매트릭스 결과·열린 항목: reviewer 신설 항목 라이브 발화 관측) + §0 최근 작업 1줄
- [ ] Step 4: `git diff --stat` 전수 확인 → 사용자 확인 후 단일 feat 커밋

## Self-Review 결과

- 스펙 §4 표 10행 ↔ Task 1~10 전 항목 대응(표 1↔T1 … 표 9↔T9, 표 10↔T10). 숫자 부칙 소유=cleancode(T1)로 표·계획 일치.
- 소비 규율 전문은 T1(소유자)에만, T2·T3·T5는 요지+참조 — Global Constraint 자기 위반 해소.
- `is` 표기 전무(전부 `==`), `default=`는 전부 `.value`, CheckConstraint는 `check=` 관례 언급.
- reviewer 불릿: 삽입 위치=빈혈 불릿 뒤("위" 지시어 정합), 배타 4종(①↔DRY·②↔판정소유·③↔파일트리·④↔테스트품질), grandfather 명시, 백스톱 분업 명시.
