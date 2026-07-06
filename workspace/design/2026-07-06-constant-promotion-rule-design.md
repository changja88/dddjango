# 상수화 규약 설계 — 어떤 문자열을 상수/Enum으로 승격하는가

- 작성: 2026-07-06 · 상태: **사용자 검토 대기** (승인 후 구현 착수)
- 범위: dddjango가 생성하는 코드의 문자열(및 부칙으로 숫자) 리터럴 승격 판정 규약. 스킬 문서 반영 + reviewer 점검 항목. **결정적 백스톱은 비채택**(§5).
- 리뷰 1: DDD 적대 리뷰(design-review-ddd, 2026-07-06) 노트 6건(blocker 2·important 3·nit 1) 전수 수용 반영 — 계층 소유·판정 소유 우선순위·공유 커널 기준·값 객체 라우팅·전이 스코프·published language 라벨.
- 리뷰 2: 정합성·실용성 적대 리뷰 2건(2026-07-06) 노트 29건 중재 반영 — **백스톱 비채택 결정 번복(§5: 결정적 부분집합 18번째 게이트 채택)**, 마이그레이션 직렬화 현실(`.value` 평탄화), `is`→`==` 비교, implementation-django 기존 예제 정리 편입, 승격 트리거 축소(분기·판정 앵커), 명백한 데이터 경계, SKILL.md 라우팅, reviewer grandfather·배타 조항. 공격 생존: 갭 진단·삽입 앵커·2곳째 수위·미러 절차·값 객체 라우팅.

---

## §1 배경·문제

생성 코드에서 choices/enum이 선언돼 있어도 소비처가 원시 문자열로 비교하는 패턴이 관찰됨:

```python
if (
    claim.idempotency_status == "duplicate_replay"
    and not claim.created
    and claim.delivery_status in {"delivered", "failed"}
):
```

- 리터럴 오타(`"duplicate_repaly"`)는 예외 없이 **조용히 항상 False** — 테스트가 그 분기를 안 밟으면 영원히 잠복. 심볼 참조는 오타 시 AttributeError로 즉사하고 mypy가 정적으로 잡는다. 위험은 "문자열"이 아니라 **오타가 조용히 지나가는 비교 위치**에 있다.
- 현 규약의 사각지대: `implementation-django` §2.5(TextChoices **선언** 권장)·`implementation-python` §10.1(Enum/StrEnum 권장)은 있으나 **소비 규율이 없다**. `discipline-cleancode`에 매직 값 판정 절 없음. reviewer 점검 항목·백스톱 17종 모두 비대상.
- 단, 발단 사례의 **복합 상태 판정 자체**(애그리거트 밖 조합 판정)는 기존 판정 소유 규율(reviewer 빈혈 불릿·`architecture-ddd` §3.2)이 이미 소유한다 — 이 규약의 순증 커버리지는 그 1차 시정 이후에도 남는 **잔여 위치**(리포지토리 필터·`default`·adapter 정규화의 리터럴)와 승격·소비·계층·테스트 규율의 명문화다.

## §2 조사 근거 (요약)

코퍼스(workspace/reference) + 외부 권위 자료 조사 결과. 핵심 발견 4가지:

1. **"문자열 전면 상수화"는 생태계 표준이 아니다.** ruff PLR2004는 str/bytes 기본 면제(숫자만 플래그, [settings.rs](https://github.com/astral-sh/ruff/blob/main/crates/ruff_linter/src/rules/pylint/settings.rs)), pylint magic-value-comparison은 opt-in 확장, [ESLint no-magic-numbers](https://eslint.org/docs/latest/rules/no-magic-numbers)는 문자열 비대상, [TSLint no-magic-strings 제안은 오탐 문제로 기각](https://github.com/palantir/tslint/issues/2928). [Sonar S1192](https://github.com/SonarSource/sonar-python/blob/master/python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S1192.html)는 의미가 아니라 중복 3회로만 판정하고 5자 미만·식별자형 문자열 면제. → 규약은 전면 검사가 아니라 **위치·용도 기반 선별**이어야 하며, 이는 §5 백스톱 비채택의 근거.
2. **단, 상태·종류 코드(type code)는 전 진영 일치로 타입 승격 대상.** [Django 공식 문서](https://docs.djangoproject.com/en/5.2/ref/models/fields/#enumeration-types)의 비교 예제는 전부 심볼(`self.year_in_school in {self.YearInSchool.JUNIOR, ...}`), Fowler 원전은 type code에 "상수를 건너뛰고 곧장 타입으로", [stringly-typed](https://blog.codinghorror.com/new-programming-jargon/)의 정의는 "타입 수단이 있는데 **불필요하게** 문자열". 코퍼스 동방향: 단단한 파이썬 "상태에 의미·동작이 붙으면 Enum"(implementation-python final.md §10.1), DDD 빈약 모델의 문자열 상태 비교 반례(architecture-ddd), 다중 boolean 대신 단일 TextChoices(implementation-django).
3. **테스트는 방향이 정반대.** [Google ToT "Don't Put Logic in Tests"](https://testing.googleblog.com/2014/07/testing-on-toilet-dont-put-logic-in.html)·["Tests Too DRY? Make Them DAMP!"](https://testing.googleblog.com/2019/12/testing-on-toilet-tests-too-dry-make.html)·[Khorikov "Leaking domain knowledge to tests"](https://enterprisecraftsmanship.com/posts/leaking-domain-knowledge-tests/): 기댓값에 프로덕션 상수를 역수입하면 상수 값이 잘못돼도 통과하는 동어반복 — "hard-coding the results is a good practice". 코퍼스의 Kent Beck 명백한 데이터(discipline-tdd final.md §7.4)와는 **역할 분담**이다: 명백한 데이터는 계산 결과값(관계를 산식으로 드러내라 — 맨 리터럴을 나쁨으로 판정)을, 이 규율은 철자가 곧 계약인 값(enum 코드·상태 문자열)을 소유한다 — §3.3에 경계 명시. 코퍼스에 자기참조 오라클 규율의 직접 서술은 없음(공백 확인).
4. **배치 규약 절반은 기존재.** `discipline-houserules` final.md: 앱 횡단 enum은 `common/enum/<domain>_enum.py`, 승격은 YAGNI(2개 이상 BC 실공유 시). PP "지식의 중복" — 우연히 같은 값·다른 지식은 합치지 않는다(discipline-cleancode external.md). [PEP 586](https://peps.python.org/pep-0586/): 값 의존 API 계약은 Literal, 도메인 개념은 Enum의 분업.

## §3 규칙 (확정)

### §3.0 전문 — 판정 원리

> **값들의 닫힌 집합의 원소로서 비교·분기·저장·전송에 쓰이면 집합 타입으로(1곳째부터), 철자가 여러 곳이 공유하는 계약이면 명명 상수로(2곳째부터), 나머지는 리터럴 그대로.**

아래 §3.1~§3.5는 이 원리의 유도 사례 목록이다. 목록에 없는 새 사례는 원리로 판정한다. 보조 판정 질문: "이 값의 오타는 어떻게 실패하는가(조용한 False vs 즉사)?" / "철자를 바꾸면 다른 파일도 함께 바뀌는가?"

원리의 경계 두 가지:

- **값 객체 라우팅**: 값에 검증·연산·불변식이 붙으면(집합의 폐쇄성과 무관하게) Enum이 아니라 **값 객체 승격 대상**이다(architecture-ddd §3.1 — 코퍼스 실존 예: `_country: CountryCode`·`PhoneNumber`. 닫힌 집합이라도 검증·연산이 붙으면 정답은 VO). enum vs VO 판정은 도메인 설계 소관이고, 이 규약은 그 경계 밖의 표기 규칙만 소유한다.
- **전이 스코프**: 이 규약은 상태값의 **표기**만 소유한다. 전이 가능 판정·전이 실행은 애그리거트 커맨드 메서드 소유(architecture-ddd §애그리거트)이며, 본 규약 준수가 그 규율을 대체하거나 면책하지 않는다.

### §3.1 상수화한다

**의미 기준 — 1곳째부터, 집합 타입으로 승격.** 앵커는 **우리 코드의 분기·판정·필터**다: 닫힌 집합의 원소이면서 우리 코드가 그 값으로 분기·판정하거나 그 값을 계약(wire·DB 제약)에 노출할 때 승격한다.

- 도메인 상태값: 생명주기·상태 전이·terminal 여부가 있는 값
- API wire contract: 요청/응답에 노출되는 enum성 문자열
- DB constraint/choices와 연결되는 값
- BC published service 입출력 계약에 들어가는 값
- provider/channel/kind/type/category 같은 분류 축 — **단 우리 코드가 그 값으로 분기·판정할 때만**(이름이 type/kind라는 이유로 승격하지 않는다)

이때 낱개 모듈 상수(`DUPLICATE_REPLAY = "duplicate_replay"`)가 아니라 **집합 단위 타입**으로 만든다. "이 상태가 전부인가"를 한 곳에서 답할 수 있어야 한다.

**승격하지 않는 경우(과승격 방지)**: ① **pass-through 저장·전송** — 분기 없이 상류 값을 저장·중계만 하는 필드는 승격 강제 대상이 아니다(데이터소스 BC — 판정 없는 상류 데이터 소스 — 는 명시 면제; enum 스캐폴딩으로 빈 domain 골격에 실내용을 만들지 않는다). ② **상류가 소유한 열린 집합** — 우리가 값 목록을 통제하지 못하면 전체를 enum화하지 않는다. 분기에 쓰는 값만 enum 멤버로 두고 **미지 값 처리 방침(UNKNOWN 폴백 또는 명시적 거부)을 함께 정한다** — 무방침 `ValueError` 정규화는 신규 값 도착 시 수집 경로를 죽인다.

**계층 소유 — 단일 출처와 파생 방향**: 도메인 판정에 쓰이는 값 집합의 단일 출처는 **domain_layer의 `StrEnum`(또는 순수 `Enum`)**이고, ORM `choices`/`CheckConstraint`와 presentation Schema는 거기서 **파생**한다. import 방향은 infra/presentation→domain만 허용, 역방향 금지(houserules §2 — domain은 아무것도 의존하지 않음). `models.TextChoices` 자체 선언은 **도메인 판정에 쓰이지 않는 순수 인프라 필드에 한정**한다 — 도메인 상태를 TextChoices로 선언하면 domain이 판정 시 ORM 타입을 역참조하게 되므로 위반이다.

- **`.value` 평탄화**: ORM 필드 인자(`default=`·`choices=`)와 마이그레이션 경계에서는 `OrderStatus.PENDING.value`처럼 `.value`로 평탄화한다 — 순수 StrEnum 멤버를 `default`에 직접 두면 Django `EnumSerializer`가 마이그레이션에 **살아있는 enum 참조**(`OrderStatus["PENDING"]` + domain import)를 직렬화해 §3.3의 동결 규율을 깬다(값 동결 직렬화기 `ChoicesSerializer`는 `models.Choices` 전용). 단일 출처에서의 `.value` 파생은 심볼 소비로 인정한다.
- **적용 조건과 전환 트리거**: 계층 소유는 4계층 표준 트리 적용 케이스에 적용한다 — 기존 TextChoices 관례가 확립된 프로젝트는 houserules §1.1(기존 규약 존중)로 그 관례를 따른다. 순수 인프라 필드였던 값에 도메인 판정이 처음 생기는 슬라이스에서 domain StrEnum 파생으로 전환한다(값 불변이면 `choices` 변경은 DB 무영향).

**중복 기준 — 서로 다른 파일 2곳째부터, 명명 상수로:**

- 닫힌 집합은 아니지만 여러 파일에서 분기 조건·키로 쓰이는 값(캐시 키 접두사, 내부 채널명 등). 1곳이면 리터럴로 두고 두 번째 파일에 등장하는 순간 승격.
- 단, **우연히 값이 같을 뿐 다른 지식이면 합치지 않는다**(나이 상한 150과 층수 상한 150은 별개 — PP 지식의 중복).

### §3.2 소비 규율 (짝 규칙 — 이번 규약의 핵심 신설)

**이 규율은 판정 소유 규율(architecture-ddd §판정 소유·tell-don't-ask)의 하위 규칙이다.** 도메인 어휘로 진술되는 복합 상태 판정의 1차 시정은 애그리거트 술어·enum 프로퍼티로의 승격이고, 심볼 비교는 그 술어 내부·리포지토리 필터·adapter 정규화 같은 **잔여 비교 위치**에 적용된다. 그 위에서: **Enum/choices가 선언된 값의 비교·분기·필터·대입·기본값은 반드시 그 심볼로 참조한다.** 선언하고 리터럴로 소비하면 위반이다.

```python
# 위반 (원 문제 코드) — 애그리거트 밖 리터럴 조합 판정
claim.idempotency_status == "duplicate_replay" and claim.delivery_status in {"delivered", "failed"}

# 1차 시정 — 판정 소유: 애그리거트 술어로 승격. 술어 내부가 심볼 비교의 정위치
claim.is_replayed_terminal()
#   내부: self.idempotency_status == IdempotencyStatus.DUPLICATE_REPLAY and self.delivery_status.is_terminal

# 잔여 비교 위치 — 심볼 참조
.filter(status=OrderStatus.PENDING)   # 리포지토리 필터
DeliveryStatus(raw_value)             # adapter 정규화(§3.5)
```

**비교 연산자는 `==`다 — `is`를 쓰지 않는다.** StrEnum 값은 ORM 필드·wire·DTO에서 plain `str`로 흐르므로, 수화(hydration)가 한 곳이라도 빠지면 `is` 비교는 오타 없이도 조용한 항상-False가 된다(규약이 잡으려는 실패 모드의 재생산). `==`는 str 서브클래스라 양방향으로 안전하고 Django 공식 관용구와 일치한다. `is`는 str 값 유통이 없는 순수 `Enum` 내부 비교에 한정한다.

**심볼 치환은 판정 소유 위반을 면책하지 않는다** — 리터럴을 심볼로 바꾸는 것만으로는 이 절의 충족이 아니다(reviewer 점검 §4-8).

**테스트 코드에서의 경계**: 테스트의 arrange/act(픽스처 생성·`.filter()` 준비)는 심볼 사용을 권장하고, **외부 계약을 관찰하는 assert 기댓값만** 리터럴로 고정한다(§3.3-1) — 같은 테스트 안에서 두 규율은 위치로 갈리므로 충돌하지 않는다.

### §3.3 상수화하지 않는다 (리터럴 허용)

- **테스트에서 외부 관찰 계약(HTTP 응답·DB 저장값·발행 이벤트)을 검증하는 expected string — 오히려 리터럴을 강제한다.** 프로덕션 상수 역수입은 자기참조 오라클(§2-3). 도메인 내부 단위 테스트가 심볼로 단언하는 것은 허용 — 철자 회귀는 계약 테스트가 잡는다. DB 저장값은 BC 사유 DB라도 기존 행과의 호환 자체가 계약이다. **경계**: 리터럴 동결 대상은 철자가 곧 계약인 값(enum 코드·상태 문자열·필드명)이고, 계산 결과값의 기댓값 표현은 discipline-tdd '명백한 데이터'가 소유한다(SUT를 호출하지 않는 독립 산식으로 관계를 드러내는 것 허용).
- 에러 메시지 본문·로그 메시지·이메일 제목 (사람 대상 서술 — 열거가 아니라 문장)
- HTTP content type, DB vendor명, Postgres error code 등 **외부 프로토콜이 소유한 문자열**. 단 이 값이 **분기 조건이 되는 순간 adapter 안에서 내부 enum으로 정규화**하고, 원시 리터럴이 adapter 밖으로 새지 않게 한다(§3.5).
- 식별자형·구조 문자열 — dict 키·kwargs·separator·Django setting key·환경변수명
- **마이그레이션 파일의 historical value** — 살아있는 Enum 참조 금지, 리터럴 동결이 규율(Enum 변경이 과거 이력의 의미를 바꾸면 안 됨; db_table 규약의 "이주 보존" 경계와 동형). 메커니즘: `default=`에 StrEnum 멤버를 직접 두면 `EnumSerializer`가 산 참조를 직렬화하므로 §3.1 `.value` 평탄화가 선행 조건이다. 수기 데이터 마이그레이션에서도 Enum import 대신 리터럴을 쓴다.
- Enum/TextChoices/상수 **정의부 자체**의 우변 (`DELIVERED = "delivered"` — 리터럴의 유일한 서식지)
- `Literal[...]`로 타입이 잠긴 외부 API 인자 (`open(path, "r")` 등 — 타입 체커가 오타를 잡음)
- 한 파일 로컬 문자열 — 닫힌 집합의 원소가 아니면 분기 의미와 무관하게 1곳은 리터럴(§3.1 중복 기준과 동일 판정). 단 같은 파일 안 반복이 같은 지식이면 DRY 판정(cleancode §13.1)이 우선한다 — 파일 임계는 승격 *강제* 시점일 뿐 지식-중복 규율을 완화하지 않는다.

### §3.4 BC 경계 규칙

- 상수/Enum은 기본적으로 **해당 BC 내부 소유**.
- 다른 BC가 내부 Enum을 직접 import하지 않는다.
- BC 간 호출은 published service 계약 타입 또는 wire value로 연결한다 — BC마다 같은 wire 값을 각자 정의하는 것은 지식의 중복이 아니라 **published language 수용**이다(유비쿼터스 언어는 BC 경계 안에서만 보편 — 같은 철자라도 컨텍스트마다 다른 개념). 상대 모델의 의미가 어긋나면 그때 ACL로 번역한다.
- `common/enum/` 승격은 **공유 커널 결정**이다: 두 BC의 값이 같은 철자를 넘어 같은 **지식**임이 확인될 때만(architecture-ddd 공유 커널 — 공유 범위 최소화 필수). "중복 비용 > 조율 비용"의 결정 가능한 대리 기준: **두 BC가 같은 변경 사유로 함께 수정된다는 근거가 명세에 있을 때만** 승격한다. houserules의 "2개 이상 BC 실공유 시 승격" 문구와 §3 표의 "앱 횡단 enum 집중화" 행을 이 기준으로 보강한다(§4-6).
- 승격된 공유 커널 enum의 배치는 `common/enum/<domain>_enum.py`(houserules 기존 슬롯 — `common/<project>/`는 enum 외 공유 VO·타입). **공유 커널은 도메인의 일부로 취급되어 domain_layer가 의존할 수 있는 유일한 외부다**("domain은 아무것도 의존하지 않는다"의 명시 예외 — 프레임워크 비종속이 조건).

### §3.5 표현 방식

- **API 문서(OpenAPI)에 드러나야 하는 값**: Schema 필드에 `Literal` 또는 `StrEnum` 우선 — 계약이 스키마에 enum으로 노출되게. 도메인 enum에서 파생하되(§3.1 계층 소유), 계약 안정성을 도메인 리팩터링과 분리해야 하면 경계-로컬 `Literal`로 고정한다.
- **Django 모델**: 도메인 판정에 쓰이는 필드의 `choices`/`CheckConstraint`는 domain_layer Enum에서 파생시켜 단일 출처 유지(§3.1 — `default=`는 `.value` 평탄화, `CheckConstraint`는 파일 관례 `check=` 표기). 순수 인프라 필드만 `TextChoices` 자체 선언. 사람용 라벨(i18n)이 필요한 필드는 파생 시 라벨 매핑을 명시적으로 병기한다(`name.title()` 기계 변환은 라벨 채널 상실).
- **파생 분류 집합**(terminal set 등): 집합 지식은 enum이 소유한다 — 1순위는 enum 프로퍼티(`DeliveryStatus.is_terminal`, 코퍼스 `OrderStatus.is_shippable`과 동형), 여러 원소를 묶는 상수가 필요하면 enum과 같은 모듈의 `frozenset`(원소는 심볼). 소비처 모듈마다 임의 frozenset을 재정의하지 않는다.
- **외부 provider raw value**: adapter에서 내부 enum으로 즉시 정규화하거나 adapter 안에 격리(§3.3의 외부 프로토콜 조항의 짝).
- **부칙 — 숫자**: 비교·계산에 등장하는 의미 있는 숫자는 1회부터 명명 상수(ruff/pylint magic-value-comparison과 대상 동일·이 규약이 더 강한 수위 — 해당 린트들은 opt-in). `0`·`±1`·루프 인덱스·수식의 본질적 구성 숫자(근의 공식의 2, 4 등)는 면제.

## §4 반영 위치 (구현 개요)

정본 `dddjango/` 수정 후 `codex-dddjango/` 미러 동기(final.md는 corpus_mirror_sync `--write` 자동, SKILL.md·agents는 수동). **db_table 규약(커밋 a803861)과 동형의 2층 집행** — 결정적 백스톱(형태·FP≈0) + reviewer 의미 점검(백스톱 사각 전담) + 문서 규약.

| # | 대상 | 변경 |
|---|---|---|
| 1 | `discipline-cleancode` references/final.md §2.14 신설 + SKILL.md | 판정 원리(§3.0)·승격 기준(§3.1)·허용 목록(§3.3)·**소비 규율 소유(§3.2)**·숫자 부칙. SKILL.md 핵심 원칙·§2 행에 라우팅 추가 |
| 2 | `implementation-python` references/final.md §10.1 | 소비 규율 요지 1줄+§2.14 참조·`==` 비교·frozenset 파생 집합·Literal/Enum 분업(기존 Literal 불릿과 정합화) |
| 3 | `implementation-django` references/final.md §2.5·§10.4 + **기존 예제 정리(§4.3·§5.1·§11·§16)** + SKILL.md | 계층 소유·`.value` 평탄화·소비 규율·historical value 경계. 기존 "권장" TextChoices 예제를 순수 인프라/파생 패턴으로 재규정, `filter(status="published")` 심볼화, §16 서비스 레이어 ORM 역참조 예제 교정. SKILL.md §2.5 행 라우팅 |
| 4 | `implementation-django-ninja` references/final.md §3.1 | wire contract 표현(Schema에 Literal/StrEnum 노출·경계-로컬 고정) 1항 보강 |
| 5 | `architecture-ddd` references/final.md | 계층 소유·파생 방향 + 판정 소유 우선순위(§3.2 말미) + BC 경계(§2.5 말미: published language 수용·공유 커널 기준·domain 의존 예외) |
| 6 | `discipline-houserules` references/final.md(트리 불릿 + §3 표 `common/enum/` 행) + SKILL.md | 공유 커널 승격 기준(같은 지식 + 같은 변경 사유 근거)·배치(`common/enum/` = 공유 커널 enum 슬롯)·domain→공유 커널 의존 예외 명문화 |
| 7 | `implementation-test` references/final.md §15.4 신설 + SKILL.md | 외부 계약 기댓값 리터럴(자기참조 오라클 금지·명백한 데이터와의 경계·arrange/assert 위치 경계). SKILL.md 라우팅 추가 |
| 8 | `dddjango/agents/discipline-reviewer.md` + codex 미러 SKILL.md | 의미 점검 항목 신설(백스톱 사각 전담): 닫힌 집합 미승격, 간접형 리터럴 소비, 계층 역참조, 테스트 역수입. **touched-only/grandfather 명시**, ①~④ 각각 기존 불릿과의 배타 조항, 삽입 위치는 빈혈 불릿 뒤 |
| 9 | **`dddjango/scripts/check-choices-literal-consumption.py` 신설(18번째 게이트)** + 등록(commands·README·AGENTS·codex SKILL·corpus_mirror_sync 주석·DEVLOG) + codex scripts 미러 | 결정적 부분집합 백스톱(§5) |
| 10 | `codex-dddjango/` 미러 동기 | final.md 11종 자동(`--write`)·SKILL.md/agents/scripts 수동 후 diff 검증 |

검증: `corpus_mirror_sync --check`(11/11) + `claude plugin validate dddjango --strict` + **백스톱 발화 매트릭스**(합성 픽스처: 위반 2형=exit 2·정상 심볼 소비=exit 0·면제 경로(migrations/테스트/인라인 choices)=exit 0) + 변경 diff 리뷰. reviewer 신설 항목의 라이브 발화 관측은 후속(DEVLOG 열린 항목 등재 — DR-59 라이브 관측 후속과 동형).

## §5 집행 설계와 비채택 결정

- **결정적 부분집합 백스톱 채택(18번째 게이트) — 초안의 "백스톱 비채택"을 적대 리뷰로 번복.** 번복 근거: ① 이 저장소의 DO-NOT-RETRY 박제(DEVLOG #8·#10) — "긍정 레시피+reviewer만" 구성은 라이브에서 실패가 재발했고 reviewer 불릿은 실위반을 권고로 강등한 관측(DR-21)이 있다 ② 초안이 인용한 db_table 선례는 실제로 2층 집행(presence 백스톱 + reviewer)이라 "백스톱 없음" 서술은 오기였다 ③ 기존 17종에 이미 AST 모델 해석(check-db-table)·의미 패턴(check-synthetic-infra-exc) 백스톱이 있어 "presence-only 철학 밖" 논거는 허수아비였다. **채택 범위(FP≈0 슬라이스만)**: (a) 같은 클래스에서 `choices=`가 심볼 출처(Name/Attribute/컴프리헨션)로 선언된 필드의 `default=<str 리터럴>` (b) 같은 앱에서 choices 선언이 확인되는 모델의 직접 호출형 `<Model>.objects.filter/exclude(<field>="리터럴")`(`<field>__in=[리터럴…]` 포함). touched-only·`migrations/`·테스트 경로 면제·인라인 리터럴 choices(심볼 출처 없음)는 비대상·fail-open(런타임 게이트 관례).
- **범용 magic-string 백스톱은 여전히 비채택.** 닫힌 집합 여부·허용 목록 경계·간접 queryset·변수 우회·미승격·계층 역참조·테스트 역수입은 의미 판정(TSLint no-magic-strings 기각 선례·ruff str 기본 면제·§2-1)이라 reviewer가 백스톱 사각을 전담한다 — db_table("존재는 백스톱·값 형태는 reviewer")과 같은 분업 구조.
- **Sonar식 3회 임계 비채택, 2곳(파일)째 채택.** 이 플러그인의 기존 "2곳째 강등/승격" 패턴(houserules common/ 승격 등)과 일관, LLM 코더에게 단순한 규칙이 준수율이 높음.
- **테스트 전면 리터럴 강제 비채택.** 외부 관찰 계약 검증으로 한정(§3.3-1) — 도메인 내부 단위 테스트의 심볼 단언은 허용. arrange/assert 위치 경계는 §3.2.

## §6 스코프 확인

단일 구현 단위로 적절: 스킬 문서 7종 + SKILL.md 라우팅 4종 + reviewer + 백스톱 스크립트 1종 신설 + 게이트 등록(README·commands·AGENTS·codex) + 미러 동기. **게이트 수 17→18** — README·commands·codex SKILL·corpus_mirror_sync 주석의 카운트 갱신 필요(a803861의 16→17 등록과 동형 절차).
