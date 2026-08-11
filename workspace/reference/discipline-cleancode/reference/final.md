# 범용 클린 코드 원칙 종합 가이드

## P1 Source Sufficiency

| field | value |
|---|---|
| purpose | Maintainability decisions: naming, function shape, responsibility, encapsulation, abstraction, SOLID, duplication, error handling, legacy code, smells, and refactoring. |
| use when | Code review or refactoring asks whether code is understandable, cohesive, explicit, testable, and easy to change without changing behavior. |
| exclude/handoff | Do not use as the source for domain modeling, REST contract, DB consistency, Django ORM mechanics, or pytest mechanics; use owning references for those axes. |
| core criteria | Separate by reason to change; keep behavior and invariants inside the right owner; prefer explicit, simple code; avoid premature abstraction; preserve behavior with small verified steps. |
| source priority | 2 primary/reputable books and guides listed in source abbreviations; 1 official PEP/Google style material only for Python style claims; 3 recognized engineering books/articles; 4 unsupported taste or memory is not accepted as source. |
| P1 classification | sufficient |

> 이 문서는 다음 자료들의 핵심 원칙을 언어 비종속적으로 종합한 것이다.
> 코드 예시는 Python으로 작성되었으나, 원칙 자체는 모든 프로그래밍 언어에 적용된다.
>
> **출처 약어:**
> - **[CC]** Clean Code (로버트 C. 마틴)
> - **[IP]** 켄트벡의 구현 패턴
> - **[OO]** 객체지향의 사실과 오해 (조영호)
> - **[PC]** 파이썬 클린코드 2nd (마리아노 아나야)
> - **[APoSD]** A Philosophy of Software Design (존 오스터하우트)
> - **[CodeC]** Code Complete (스티브 맥코넬)
> - **[PP]** The Pragmatic Programmer (데이빗 토마스, 앤드류 헌트)
> - **[Ref]** Refactoring (마틴 파울러)
> - **[WELC]** Working Effectively with Legacy Code (마이클 페더스)
> - **[Google]** Google Python Style Guide
> - **[PEP]** PEP 문서 (Python 공식)

---

## 목차

1. [클린 코드란 무엇인가](#1-클린-코드란-무엇인가)
2. [이름 짓기 (Naming)](#2-이름-짓기-naming)
3. [함수와 메서드 설계](#3-함수와-메서드-설계)
4. [주석과 문서화](#4-주석과-문서화)
5. [코드 형식과 구조](#5-코드-형식과-구조)
6. [추상화와 캡슐화](#6-추상화와-캡슐화)
7. [깊은 모듈 설계](#7-깊은-모듈-설계)
8. [객체 설계 원칙](#8-객체-설계-원칙)
9. [SOLID 원칙](#9-solid-원칙)
10. [디자인 패턴](#10-디자인-패턴)
11. [상태 관리](#11-상태-관리)
12. [오류 처리](#12-오류-처리)
13. [중복 제거와 DRY](#13-중복-제거와-dry)
14. [협력과 의존성 관리](#14-협력과-의존성-관리)
15. [리팩토링](#15-리팩토링)
16. [레거시 코드 다루기](#16-레거시-코드-다루기)
17. [설계 철학과 프로세스](#17-설계-철학과-프로세스)
18. [Python 관용구와 스타일](#18-python-관용구와-스타일)

---

## 1. 클린 코드란 무엇인가

### 1.1 핵심 정의

클린 코드에 대한 정의는 대가들마다 표현이 다르지만 공통된 본질이 있다.

> "깨끗한 코드는 한 가지를 제대로 한다" -- 비야네 스트롭스트룹 **[CC]**

> "깨끗한 코드는 단순하고 직접적이다. 잘 쓴 문장처럼 읽힌다." -- 그래디 부치 **[CC]**

> "클린 코드인지 아닌지는 다른 엔지니어가 코드를 읽고 유지 관리할 수 있는지 여부에 달려 있다" **[PC]**

> "프로그래밍 언어의 진정한 의미는 아이디어를 다른 개발자에게 전달하는 것이다" **[PC]**

### 1.2 클린 코드의 세 가지 비결 [CC]

론 제프리스가 정리한 클린 코드의 핵심:

1. **중복 줄이기** -- 같은 작업을 반복하면 아이디어를 제대로 표현하지 못한 증거다
2. **표현력 높이기** -- 의미 있는 이름, 단일 책임 메서드
3. **초반부터 간단한 추상화 고려하기** -- 실제 구현을 감싸는 추상화

### 1.3 세 가지 가치 [IP]

켄트 벡은 훌륭한 프로그래밍의 공통 가치를 다음과 같이 정의한다:

- **커뮤니케이션** -- 코드를 쉽게 이해하고, 수정하고, 사용할 수 있는가
- **단순성** -- 복잡도를 낮춰 빠르게 이해할 수 있는가 (단, 과도한 단순화는 커뮤니케이션을 저해)
- **유연성** -- 변경에 대응할 수 있는가 (유연성은 복잡도를 증가시키므로 필요한 경우에만)

### 1.4 소프트웨어 비용 공식 [IP]

```
전체 비용 = 개발 비용 + 유지 비용
유지 비용 = 이해 비용 + 수정 비용 + 테스트 비용 + 설치 비용
```

**유지 비용이 대부분을 차지하며, 그중에서도 이해 비용이 핵심이다.**

### 1.5 복잡성의 본질 [APoSD]

소프트웨어 설계의 근본 문제는 **복잡성 관리**다. 복잡성이란 시스템을 이해하고 수정하기 어렵게 만드는 구조적 특성이다.

#### 복잡성의 세 가지 발현

| 발현 | 설명 | 예시 |
|------|------|------|
| **Change Amplification** | 단순한 변경이 여러 곳의 수정을 요구 | 색상 상수가 10개 파일에 분산 |
| **Cognitive Load** | 한 작업을 완료하기 위해 알아야 할 것이 많다 | 함수 호출을 위해 5개 모듈의 상태를 이해해야 함 |
| **Unknown Unknowns** | 무엇을 해야 하는지, 제안된 해법이 올바른지조차 불분명 | 숨겨진 의존성이나 암묵적 규칙 |

#### 복잡성의 두 가지 근원

- **의존성(dependencies)**: 코드를 고립적으로 이해하고 수정할 수 없는 상태
- **모호성(obscurity)**: 중요한 정보가 명확하지 않은 상태

### 1.6 제1 기술적 명령: 복잡성 관리 [CodeC]

고품질 코드는 읽는 사람에게 **일관된 추상화 수준**을 노출하며, 명확한 경계로 구분된다. 본질적 복잡성(essential complexity)은 최소화하고, 우발적 복잡성(accidental complexity)의 확산을 방지한다.

---

## 2. 이름 짓기 (Naming)

### 2.1 의도를 분명히 밝혀라 [CC]

변수, 함수, 클래스 이름은 존재 이유, 수행 기능, 사용 방법에 모두 답해야 한다.
따로 주석이 필요하다면 의도를 분명히 드러내지 못했다는 뜻이다.

```python
# --- 나쁜 예 ---
d = 7  # 경과 일수

# --- 좋은 예 ---
elapsed_days_since_creation = 7
```

### 2.2 그릇된 정보를 피하라 [CC]

유사한 개념은 유사한 표기법을 사용하되, 실제와 다른 정보를 이름에 담지 마라.

```python
# --- 나쁜 예 ---
account_list = {}  # 실제로는 dict인데 list라고 명명

# --- 좋은 예 ---
accounts = {}
account_map = {}
```

### 2.3 의미 있게 구분하라 [CC]

불용어(Info, Data, a, the)를 사용하면 개념을 구분하지 못한 채 이름만 달리한 것이다.

```python
# --- 나쁜 예 ---
class ProductInfo: ...
class ProductData: ...  # Info와 Data는 아무것도 구분하지 못한다

# --- 좋은 예 ---
class Product: ...
class ProductDetail: ...  # 구체적으로 무엇이 다른지 이름에 반영
```

### 2.4 검색하기 쉬운 이름과 변수 이름 길이 [CC] [CodeC]

이름 길이는 **범위(scope) 크기에 비례**해야 한다. 넓은 범위에서 사용되는 변수일수록 긴 이름이 필요하고, 좁은 범위의 지역 변수는 짧아도 된다. **[CC]**

평균적인 가이드라인으로, 변수 이름의 최적 평균 길이는 **10-16자**(Gorla, Benander, Benander 연구), 루틴 이름은 **15-20자**를 참고한다. **[CodeC]**

```python
# --- 나쁜 예 ---
for i in range(34):
    s += t[i] * 4 / 5  # 4, 5, s, t가 무엇인지 알 수 없다

# --- 좋은 예 ---
WORK_DAYS_PER_WEEK = 5
for task_index in range(number_of_tasks):
    real_days = task_estimate[task_index] * real_days_per_ideal_day
    weekly_sum += real_days / WORK_DAYS_PER_WEEK
```

### 2.5 한 개념에 한 단어를 사용하라 [CC]

추상적인 개념 하나에 단어 하나를 선택해 고수한다.

```python
# --- 나쁜 예 ---
class UserRepository:
    def fetch_user(self): ...   # fetch

class OrderRepository:
    def retrieve_order(self): ...  # retrieve -- 같은 개념에 다른 단어

# --- 좋은 예 ---
class UserRepository:
    def get_user(self): ...

class OrderRepository:
    def get_order(self): ...  # 통일된 용어 사용
```

### 2.6 클래스 이름은 명사, 메서드 이름은 동사 [CC] [IP]

```python
# 클래스: 명사 또는 명사구
class Customer: ...
class AddressParser: ...

# 메서드: 동사 또는 동사구
def post_payment(self): ...
def delete_page(self): ...
```

### 2.7 의도 제시형 이름 [IP]

메서드 이름에는 의도만 전달하고 구현 전략은 담지 마라.

```python
# --- 나쁜 예 ---
def linear_search_customer(customer_id: str) -> Customer: ...

# --- 좋은 예 ---
def find_customer(customer_id: str) -> Customer: ...
```

### 2.8 역할 제시형 작명 [IP]

변수 이름은 연산에서의 역할을 반영하여 짓는다. 생명기간, 범위, 타입은 문맥에서 전달된다.

```python
# --- 나쁜 예 ---
temp_str_list = get_items()

# --- 좋은 예 ---
results = get_items()         # 컬렉터 역할
pending_count = len(queue)    # 카운터 역할
```

### 2.9 컬렉션은 복수형으로 [IP]

여러 데이터를 저장하는 변수는 복수형이어야 한다.

```python
# --- 나쁜 예 ---
member = [user1, user2, user3]

# --- 좋은 예 ---
members = [user1, user2, user3]
```

### 2.10 한정자(Qualifier) 배치: 핵심 개념을 앞에 [CodeC]

핵심 개념을 접두어로, 한정자를 뒤에 배치한다. 관련 변수들이 그룹으로 인식되고, IDE 자동완성과 알파벳 정렬에서도 이점이 있다.

```python
# --- 나쁜 예: 한정자가 앞에 ---
total_revenue = ...
avg_revenue = ...
max_revenue = ...

# --- 좋은 예: 핵심 의미를 앞에, 한정자를 뒤에 ---
revenue_total = ...
revenue_average = ...
revenue_max = ...
# 핵심 개념(revenue)이 항상 앞에 있으므로 그룹으로 인식 가능
```

### 2.11 불리언 변수 명명과 사용 [CodeC]

불리언은 이름이 참/거짓을 드러내게 하고, 사용할 때도 `if flag == True`처럼 불리언 리터럴과 비교하지 말고 값 자체를 조건으로 쓴다.

```python
# --- 나쁜 예: True/False가 불명확 ---
status = True
source_file = True

# --- 좋은 예: 이름 자체가 참/거짓을 암시 ---
is_valid = True
has_permission = True
source_file_found = True
order_complete = False

# --- 나쁜 예: 부정형 이름 (이중 부정 발생) ---
not_found = True
if not not_found:  # 혼란스럽다
    ...

# --- 좋은 예: 긍정형 이름 사용 ---
found = False
if found:
    ...
```

### 2.12 `num` 사용 회피 [CodeC]

```python
# --- 나쁜 예: num의 의미가 모호 ---
num_customers = 5       # 총 수? 인덱스?
customer_num = 3        # 총 수? 인덱스?

# --- 좋은 예: 명확한 이름 ---
customer_count = 5      # 총 수
customer_index = 3      # 인덱스
```

### 2.13 루프 변수 명명 [CodeC]

```python
# 허용: 짧은 루프에서 관례적 이름
for i in range(10):
    matrix[i] = 0

# 좋은 예: 긴 루프나 중첩 루프에서는 의미 있는 이름
for team_index, team in enumerate(teams):
    for player_index, player in enumerate(team.players):
        scores[team_index][player_index] = player.score
```

### 2.14 매직 값과 상수 승격 판정 [PP] [Ref]

리터럴을 상수·Enum으로 승격할지는 "문자열이냐"가 아니라 **오타의 실패 모드**와 **철자의 계약성**으로 판정한다. 리터럴 오타는 조용한 항상-False로 잠복하고, 심볼 오타는 `AttributeError`로 즉사한다.

**승격 판정 원리**:

1. 값들의 **닫힌 집합의 원소**이면서 **우리 코드가 그 값으로 분기·판정·필터**하거나 계약(wire·DB 제약)에 노출하면 **집합 단위 타입**으로 — 1곳째부터. 도메인 상태·종류(type code)가 여기다. 낱개 상수 나열(`DUPLICATE_REPLAY = "duplicate_replay"`)이 아니라 집합 하나의 타입으로 — "이 상태가 전부인가"를 한 곳에서 답한다. **과승격 방지**: 분기 없이 저장·중계만 하는 pass-through 값은 강제 대상이 아니고, 상류가 소유한 열린 집합은 분기에 쓰는 값만 멤버로 두되 미지 값 처리 방침(UNKNOWN 폴백 또는 명시 거부)을 함께 정한다. 이름이 type/kind라는 이유만으로 승격하지 않는다. 단 **우리 BC가 발행하는 이벤트 봉투의 discriminator는 1종째부터 enum**이다 — 예외가 아니라 판정의 선행 확정: 발행 봉투는 outbox 저장·wire 노출로 이 앵커에 구조적으로 도달하므로 판정을 확장 시점으로 미루지 않는다(birth-enum — `architecture-ddd` §3.7).
2. 닫힌 집합이 아니라도 **같은 지식의 철자를 서로 다른 파일 2곳 이상이 공유**하면 명명 상수로. 우연히 값이 같을 뿐 다른 지식이면 합치지 않는다(나이 상한 150과 층수 상한 150은 별개 — §13.1). 같은 파일 안 반복이 같은 지식이면 §13.1 지식-중복 판정이 우선한다 — 파일 임계는 승격 *강제* 시점일 뿐 DRY를 완화하지 않는다.
3. 나머지는 리터럴 그대로 둔다.

**리터럴 허용 목록** (승격하지 않는다):

- 사람 대상 서술 — 로그·예외 메시지·이메일 제목(열거가 아니라 문장, 비교 대상 아님)
- Enum·상수 **정의부 자체**의 우변(리터럴의 유일한 서식지)
- `Literal[...]`로 타입이 잠긴 인자 자리(`open(path, "r")` — 타입 체커가 오타를 잡는다). 단 **발행 이벤트 봉투의 discriminator 자리는 이 항목의 예외** — 거기는 domain enum 파생(`Literal[EventType.X]`)이 규율이고 맨 문자열 `Literal["…"]`이면 위반(birth-enum — `architecture-ddd` §3.7). 버전 태그(`payload_schema_version`)는 같은 형태라도 리터럴 동결이 정답(짝 조항). **OHS published contract(`open_host_service/*/contract/`)의 discriminator 자리는 재예외** — contract 무의존(`discipline-houserules` §2 OHS 내부 구조)이 우선해 wire `Literal["…"]`을 유지하고 union-enum 동기 테스트(`implementation-test` §15.5)가 드리프트를 방어한다
- 외부 프로토콜이 소유한 문자열(content type·vendor 코드·프로토콜 에러 코드) — 단 분기 조건이 되는 순간 경계(adapter)에서 내부 타입으로 정규화하고 원시 리터럴이 경계 밖으로 새지 않게 한다
- 식별자형·구조 문자열(dict 키·kwargs·separator·설정 키·환경변수명)
- 테스트에서 외부 관찰 계약을 검증하는 **assert 기댓값** — 오히려 리터럴을 강제한다(프로덕션 상수 역수입은 자기참조 오라클; `implementation-test` §15.4). 테스트의 arrange/act(픽스처·필터 준비)는 심볼 권장 — 두 규율은 위치로 갈린다.

**짝 규칙(소비 규율)**: 집합 타입이 선언된 값의 비교·분기·필터·대입·기본값은 반드시 그 심볼로 참조한다 — 선언하고 리터럴로 소비하면 위반이다. 비교는 `==`로 한다(`is` 금지 — 문자열 Enum 값은 경계에서 plain str로 흐르므로 `is`는 수화 누락 시 오타 없이도 조용한 False를 만든다). 단 심볼 치환은 판정 소유 규율을 면책하지 않는다: 도메인 어휘로 진술되는 복합 상태 판정의 1차 시정은 애그리거트 술어·enum 프로퍼티다(`architecture-ddd` §3.2). 값에 검증·연산·불변식이 붙으면(집합의 폐쇄성과 무관하게) Enum이 아니라 값 객체 승격 대상이다(판정은 `architecture-ddd` §3.1 소관).

**숫자 부칙**: 비교·계산에 등장하는 의미 있는 숫자는 1회부터 명명 상수(ruff/pylint magic-value-comparison과 대상 동일·더 강한 수위). `0`·`±1`·루프 인덱스·수식의 본질적 구성 숫자(근의 공식의 2·4)는 면제.

---

## 3. 함수와 메서드 설계

### 3.1 함수는 작게, 모듈은 깊게 [CC] [APoSD]

**함수 수준**: 함수를 만드는 첫째 규칙은 "작게!"이고, 둘째 규칙도 "더 작게!"이다. 의미 있는 이름으로 다른 함수를 추출할 수 있다면, 그 함수는 여러 작업을 하고 있다. **[CC]**

**모듈/클래스 수준**: 최고의 모듈은 단순한 인터페이스 뒤에 강력한(큰) 기능을 숨기는 "깊은 모듈"이다. 과도하게 작은 함수/클래스는 "얕은 모듈"이 되어 인터페이스가 구현만큼 복잡해질 수 있다. **[APoSD]**

**통합 가이드라인**: 공개 인터페이스(모듈, 클래스)는 깊게 설계하되, 내부 구현은 작은 private 함수로 분해한다.

```python
# --- 나쁜 예: 하나의 함수가 너무 많은 일을 한다 ---
def render_page(page_data, is_suite):
    is_test_page = page_data.has_attribute("Test")
    if is_test_page:
        test_page = page_data.get_wiki_page()
        new_content = ""
        new_content += include_setup_pages(test_page, is_suite)
        new_content += page_data.get_content()
        new_content += include_teardown_pages(test_page, is_suite)
        page_data.set_content(new_content)
    return page_data.get_html()

# --- 좋은 예: 작은 함수로 분해 (내부 구현) ---
def render_page(page_data, is_suite):
    if is_test_page(page_data):
        include_setup_and_teardown(page_data, is_suite)
    return page_data.get_html()
```

```python
# --- 나쁜 예: 얕은 모듈 -- 인터페이스가 구현만큼 복잡 ---
class FileReader:
    def open(self, path: str) -> None: ...
    def check_permissions(self, path: str) -> bool: ...
    def read_bytes(self, offset: int, length: int) -> bytes: ...
    def decode(self, data: bytes, encoding: str) -> str: ...
    def close(self) -> None: ...

# 사용하려면 호출자가 5단계를 전부 알아야 한다
reader = FileReader()
reader.open("data.txt")
if reader.check_permissions("data.txt"):
    raw = reader.read_bytes(0, 1024)
    text = reader.decode(raw, "utf-8")
    reader.close()

# --- 좋은 예: 깊은 모듈 -- 단순한 인터페이스 뒤에 복잡성을 숨김 ---
from pathlib import Path

def read_text(path: str, encoding: str = "utf-8") -> str:
    """파일을 읽어 텍스트로 반환한다. 권한, 인코딩, 리소스 정리를 내부에서 처리."""
    return Path(path).read_text(encoding=encoding)

# 호출자는 한 줄이면 된다
text = read_text("data.txt")
```

### 3.2 한 가지만 해라 [CC] [IP]

> "함수는 한 가지를 해야 한다. 그 한 가지를 잘 해야 한다. 그 한 가지만을 해야 한다." **[CC]**

의미 있는 이름으로 다른 함수를 추출할 수 있다면, 그 함수는 여러 작업을 하고 있다.

### 3.3 추상화 수준은 하나로 [CC] [IP]

한 함수 내의 모든 문장은 동일한 추상화 수준이어야 한다.

```python
# --- 나쁜 예 ---
def compute(self):
    self.input()
    self.flags |= 0x0080  # 갑자기 추상화 수준이 바뀜
    self.output()

# --- 좋은 예 ---
def compute(self):
    self.input()
    self.set_loaded_flag()  # 동일한 추상화 수준 유지
    self.output()
```

### 3.4 함수 인수는 최소로 [CC] [IP]

이상적인 인수 개수는 0개이다. 인수가 많으면 인수 객체를 만들어라.

```python
# --- 나쁜 예 ---
def make_circle(x: float, y: float, radius: float): ...

# --- 좋은 예 ---
def make_circle(center: Point, radius: float): ...
```

### 3.5 플래그 인수를 쓰지 마라 [CC]

플래그 인수는 함수가 여러 가지 일을 한다고 대놓고 선언하는 것이다.

```python
# --- 나쁜 예 ---
def render(is_suite: bool): ...

# --- 좋은 예 ---
def render_for_suite(): ...
def render_for_single_test(): ...
```

### 3.6 명령과 조회를 분리하라 [CC]

함수는 무언가를 수행하거나 무언가에 답하거나 둘 중 하나만 해야 한다.

```python
# --- 나쁜 예 ---
def set_attribute(name: str, value: str) -> bool:
    """속성을 설정하고 성공 여부를 반환"""
    ...

if set_attribute("username", "alice"):  # 설정인가? 확인인가?
    ...

# --- 좋은 예 ---
def attribute_exists(name: str) -> bool: ...
def set_attribute(name: str, value: str) -> None: ...

if attribute_exists("username"):
    set_attribute("username", "alice")
```

### 3.7 부수 효과를 일으키지 마라 [CC]

부수 효과는 시간적 결합(temporal coupling)이나 순서 종속성을 초래한다.

```python
# --- 나쁜 예 ---
def check_password(username: str, password: str) -> bool:
    user = find_user(username)
    if user and verify(user.encoded_phrase, password):
        session.initialize()  # 부수 효과! 이름에서 예측 불가
        return True
    return False

# --- 좋은 예 ---
def check_password(username: str, password: str) -> bool:
    user = find_user(username)
    if user is None:
        return False
    return verify(user.encoded_phrase, password)

def login(username: str, password: str) -> bool:
    if check_password(username, password):
        session.initialize()
        return True
    return False
```

### 3.8 대칭성을 활용하라 [IP]

코드의 대칭성을 찾아내서 명확히 표현하면 읽기 수월해진다.

```python
# --- 나쁜 예 ---
def compute(self):
    self.input()
    self.helper.process(self)  # 비대칭적
    self.output()

# --- 좋은 예 ---
def compute(self):
    self.input()
    self.process()  # 대칭적 -- 모두 self에게 메시지
    self.output()

def process(self):
    self.helper.process(self)
```

### 3.9 고품질 루틴 설계 [CodeC]

#### 루틴을 만들어야 하는 이유

- 복잡성을 줄인다 (한 번에 한 가지에 집중)
- 이해하기 쉬운 추상화를 도입한다
- 코드 중복을 피한다
- 변경의 영향을 제한한다
- 코드를 숨긴다 (정보 은닉)

#### 루틴의 결정 횟수(Decision Count)

한 루틴의 결정 횟수가 **10을 초과**하면 재설계를 고려하라.

```python
# --- 나쁜 예: 결정 횟수 과다 ---
def process_order(order):
    if order.status == "new":
        if order.payment_method == "credit":
            if order.amount > 1000:
                if order.customer.is_vip:
                    ...

# --- 좋은 예: 전략 패턴 등으로 분해 ---
class OrderProcessor:
    def __init__(self):
        self._status_handlers = {
            "new": self._handle_new,
            "pending": self._handle_pending,
        }

    def process(self, order):
        handler = self._status_handlers.get(order.status)
        if handler is None:
            raise ValueError(f"Unknown status: {order.status}")
        return handler(order)
```

---

## 4. 주석과 문서화

> **통합 원칙**: 구현 주석(인라인 주석)은 최소화하되, 인터페이스 주석(독스트링, 공개 API 문서)은 적극적으로 작성한다. **[CC] + [APoSD]**

### 4.1 구현 주석은 최소화하라 [CC] [IP]

> "주석은 코드로 의도를 표현하는 것에 실패했기 때문에 작성한다." **[CC]**

주석 대신 코드 자체로 의도를 표현해야 한다. 주석은 코드와 동기화가 깨지기 쉽고, 주석을 작성하고 일관성을 유지하는 비용을 정당화할 수 있는 경우에만 사용해야 한다. **[IP]**

```python
# --- 나쁜 예 ---
# 직원에게 복지 혜택을 받을 자격이 있는지 검사한다
if employee.flags & HOURLY_FLAG and employee.age > 65:
    ...

# --- 좋은 예 ---
if employee.is_eligible_for_full_benefits():
    ...
```

### 4.2 인터페이스 주석은 필수로 작성하라 [APoSD]

Ousterhout은 "좋은 코드는 주석이 필요 없다"는 통념에 **반대**한다. 인터페이스 주석과 멤버 변수 주석은 짧게라도 반드시 작성해야 하며, 이는 복잡성을 줄이고 Unknown Unknowns를 방지하는 핵심 도구다.

- **인터페이스 주석**: 모듈의 전체적 동작, 인자, 반환값, 부작용, 예외를 문서화하라
- **구현 주석**: "무엇"이 아닌 "왜"를 설명하라
- **멤버 변수 주석**: 변수의 목적을 짧게라도 반드시 설명하라

```python
# --- 나쁜 주석: 코드를 반복 (무엇) ---
count += 1  # count를 1 증가시킨다

# --- 좋은 주석: 이유를 설명 (왜) ---
count += 1  # 재시도 횟수를 추적하여 최대 3회 초과 시 중단하기 위함
```

### 4.3 계층별 주석 가이드라인 요약

| 계층 | 방침 | 근거 |
|------|------|------|
| **공개 API / 인터페이스** | 적극 작성 (독스트링 필수) | 복잡성 감소, Unknown Unknowns 방지 **[APoSD]** |
| **내부 구현 (인라인)** | 최소화 ("왜"만 기록) | 코드 자체가 "무엇"을 설명해야 함 **[CC]** |
| **멤버 변수** | 짧게라도 필수 | 변수의 목적이 이름만으로 불충분할 때 **[APoSD]** |

### 4.4 유용한 주석의 유형 [CC]

- **법적인 주석** -- 저작권, 라이선스 정보
- **의도를 설명하는 주석** -- "왜" 이런 결정을 했는지
- **결과를 경고하는 주석** -- 스레드 안전성 경고 등
- **TODO 주석** -- 앞으로 할 일 (나쁜 코드의 핑계로 사용 금지)
- **중요성을 강조하는 주석** -- 대수롭지 않아 보이지만 중요한 것

### 4.5 나쁜 주석의 유형 [CC]

- 같은 이야기를 중복하는 주석
- 의무적으로 다는 주석
- 이력을 기록하는 주석 (소스 관리 시스템이 있다)
- 있으나 마나 한 주석 (당연한 사실 언급)
- 주석으로 처리한 코드 (그냥 삭제하라)

### 4.6 문서화와 주석은 다르다 [PC]

- **주석(comment)**: 가능한 한 적게. 코드 자체가 문서화되어야 한다.
- **문서(docstring)**: 컴포넌트의 동작 방식, 입출력 정보를 설명. "이유가 아니라 설명"이다.

### 4.7 독스트링 작성법

독스트링은 **무엇을** 문서화할지가 원칙이다 — 모듈/클래스/함수/스크립트의 동작·입출력·예외·호출 제약을 설명한다(§4.6). PEP 257 양식(삼중 따옴표, Args/Returns/Raises 구조)과 Python 작성 규칙은 `workspace/reference/implementation-python/reference/final.md` §26을 따른다.

---

## 5. 코드 형식과 구조

### 5.1 형식은 의사소통이다 [CC]

코드 형식은 의사소통의 일환이다. 구현 스타일과 가독성 수준은 유지보수 용이성과 확장성에 계속 영향을 미친다.

### 5.2 적절한 행 길이를 유지하라 [CC]

500줄이 넘지 않고 대부분 200줄 정도인 파일로도 커다란 시스템을 구축할 수 있다. **[CC]**

코드/주석의 구체적 줄 길이(line length) 수치는 Ruff 설정으로 강제하며 `workspace/reference/implementation-python/reference/final.md` §22를 따른다.

### 5.3 일관성이 핵심이다 [PC]

좋은 코드 레이아웃에서 가장 필요한 특성은 **일관성**이다. 코드가 일관되게 구조화되어 있으면 가독성이 높아지고 이해하기 쉬워진다.

### 5.4 자동화 도구를 활용하라 [PC]

포매팅, 린팅, 타입 검사를 자동화해야 한다. 이 모든 검사는 CI(지속적 통합)의 일부가 되어야 한다.

---

## 6. 추상화와 캡슐화

### 6.1 추상화를 통한 복잡성 극복 [OO]

> "현상은 복잡하다. 법칙은 단순하다. 버릴 게 무엇인지 알아내라." -- 파인만

추상화의 두 가지 방법:
1. 공통점을 취하고 차이점을 버리는 **일반화**
2. 불필요한 세부 사항을 제거하는 **단순화**

### 6.2 구현이 아니라 인터페이스에 맞춰 코딩하라 [IP] [OO]

> "설계상의 결정을 필요 이상으로 노출하지 말라" **[IP]**

```python
# --- 나쁜 예 ---
class ReportGenerator:
    def generate(self, data: list):
        mysql_conn = MySQLConnection()  # 구체적 구현에 의존
        mysql_conn.save(data)

# --- 좋은 예 ---
class ReportGenerator:
    def __init__(self, storage: StorageInterface):
        self._storage = storage

    def generate(self, data: list):
        self._storage.save(data)  # 인터페이스에 의존
```

### 6.3 상태를 캡슐화하라 [OO]

객체의 자율성은 내부와 외부를 명확하게 구분하는 것으로부터 나온다.

> "객체가 무엇(what)을 수행하는지는 알 수 있지만 어떻게(how) 수행하는지에 대해서는 알 수 없어야 한다." **[OO]**

```python
# --- 나쁜 예 ---
class BankAccount:
    def __init__(self):
        self.balance = 0  # 외부에서 직접 수정 가능

account = BankAccount()
account.balance = -1000  # 불변식 위반 가능

# --- 좋은 예 ---
class BankAccount:
    def __init__(self):
        self._balance = 0

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("입금액은 양수여야 합니다")
        self._balance += amount

    def get_balance(self) -> float:
        return self._balance
```

### 6.4 인터페이스와 구현의 분리 원칙 [OO]

> "객체를 구성하지만 공용 인터페이스에 포함되지 않는 모든 것이 구현에 포함된다." **[OO]**

객체 설계의 핵심은 외부에 공개되는 인터페이스와 내부에 감춰지는 구현을 명확하게 분리하는 것이다.

### 6.5 정보 은닉 (Information Hiding) [APoSD]

깊은 모듈을 달성하는 가장 중요한 기법이다. 설계 결정과 내부 정보를 인터페이스 뒤에 캡슐화하여 외부에 노출하지 않는다.

```python
# --- 나쁜 예: Information Leakage (정보 누출) ---
# 두 모듈이 같은 파일 형식 지식을 공유한다
class CSVReader:
    def read(self, path: str) -> list[list[str]]:
        with open(path) as f:
            return [line.strip().split(",") for line in f]

class CSVWriter:
    def write(self, path: str, rows: list[list[str]]) -> None:
        with open(path, "w") as f:
            for row in rows:
                f.write(",".join(row) + "\n")

# --- 좋은 예: 형식 지식을 한 모듈에 집중 ---
class CSVFormat:
    DELIMITER = ","
    LINE_ENDING = "\n"

    @classmethod
    def parse_row(cls, line: str) -> list[str]:
        return line.strip().split(cls.DELIMITER)

    @classmethod
    def format_row(cls, fields: list[str]) -> str:
        return cls.DELIMITER.join(fields) + cls.LINE_ENDING
```

---

## 7. 깊은 모듈 설계 [APoSD]

### 7.1 깊은 모듈 vs 얕은 모듈

Ousterhout의 핵심 개념: 최고의 모듈은 강력한 기능을 제공하면서 단순한 인터페이스를 갖는다.

```
깊은 모듈 (Deep Module)        얕은 모듈 (Shallow Module)
┌─────────┐                    ┌─────────────────────────┐
│Interface│ <- 단순             │        Interface        │ <- 복잡
├─────────┤                    ├─────────────────────────┤
│         │                    │ Implementation          │ <- 단순
│ Impl.   │ <- 복잡 (숨김)      └─────────────────────────┘
│         │
│         │
└─────────┘
```

### 7.2 전략적 프로그래밍 vs 전술적 프로그래밍 [APoSD]

| 전술적 (Tactical) | 전략적 (Strategic) |
|-------------------|-------------------|
| "동작하면 된다, 다음 작업으로" | "훌륭한 설계를 만들자, 동작도 당연히 해야 한다" |
| 단기적 속도 | 장기적 생산성에 투자 |
| 복잡성 누적 -> 기능 추가 비용 증가 | 복잡성 통제 -> 지속적으로 빠른 기능 추가 |

**전술적 토네이도(Tactical Tornado)**: 다른 사람보다 훨씬 빠르게 코드를 쏟아내지만, 완전히 전술적(임기응변적)으로 작업하는 프로그래머. 그들이 남긴 코드는 다른 개발자가 유지보수해야 한다.

```python
# 전술적 프로그래밍: "일단 돌아가게 만들자"
def handle_request(req):
    if req.get("type") == "A":
        data = req.get("data", {})
        result = data.get("value", 0) * 2
        if req.get("format") == "json":
            return {"result": result}
        return str(result)
    elif req.get("type") == "B":
        data = req.get("data", {})
        result = data.get("value", 0) * 3
        if req.get("format") == "json":
            return {"result": result}
        return str(result)

# 전략적 프로그래밍: 설계에 투자
from dataclasses import dataclass
from typing import Protocol

class RequestHandler(Protocol):
    def compute(self, value: float) -> float: ...

@dataclass
class TypeAHandler:
    multiplier: float = 2.0
    def compute(self, value: float) -> float:
        return value * self.multiplier

@dataclass
class TypeBHandler:
    multiplier: float = 3.0
    def compute(self, value: float) -> float:
        return value * self.multiplier

class RequestRouter:
    def __init__(self):
        self._handlers: dict[str, RequestHandler] = {
            "A": TypeAHandler(),
            "B": TypeBHandler(),
        }

    def handle(self, req: dict) -> dict | str:
        handler = self._handlers.get(req.get("type", ""))
        if handler is None:
            raise ValueError(f"Unknown type: {req.get('type')}")
        value = req.get("data", {}).get("value", 0)
        result = handler.compute(value)
        if req.get("format") == "json":
            return {"result": result}
        return str(result)
```

### 7.3 설계의 레드 플래그 [APoSD]

| 레드 플래그 | 설명 |
|------------|------|
| 얕은 모듈 | 인터페이스가 구현에 비해 지나치게 복잡 |
| 정보 누출 | 같은 지식이 여러 모듈에 분산 |
| 시간적 분해 | 실행 순서에 따라 모듈을 나눈 결과 정보가 분산 |
| 과도한 노출 | 내부 구현이 API에 불필요하게 드러남 |
| Pass-through 메서드 | 거의 아무것도 하지 않고 다른 메서드를 호출만 하는 메서드 |
| Pass-through 변수 | 긴 호출 체인을 통해 전달만 되는 변수 |

---

## 8. 객체 설계 원칙

### 8.1 행동이 상태를 결정한다 [OO]

상태를 먼저 결정하고 행동을 나중에 결정하면 설계에 나쁜 영향을 끼친다.

> "어떤 객체가 어떤 타입에 속하는지를 결정하는 것은 객체가 수행하는 행동이다." **[OO]**

```python
# --- 나쁜 예: 데이터 주도 설계 ---
class Employee:
    def __init__(self):
        self.name = ""
        self.salary = 0
        self.department = ""
    # 데이터를 먼저 정의하고 행동은 나중에...

# --- 좋은 예: 책임 주도 설계 ---
class Employee:
    def calculate_pay(self) -> Money: ...
    def report_hours(self) -> Hours: ...
    # 행동을 먼저 정의하고 필요한 데이터는 내부에 캡슐화
```

### 8.2 묻지 말고 시켜라 (Tell, Don't Ask) [OO]

어떻게 해야 하는지 묻지 말고 무엇을 해야 하는지 요청하라.

```python
# --- 나쁜 예: 물어보고 직접 처리 ---
if order.get_status() == "paid":
    order.set_status("shipped")
    warehouse.remove_stock(order.get_items())

# --- 좋은 예: 시키기 ---
order.ship(warehouse)  # 주문 객체가 자율적으로 처리
```

### 8.3 조건문을 다형성으로 대체하라 [CC] [IP]

중복되는 조건부 로직이나 분기문의 결과에 따라 로직이 달라지는 경우, 명시적인 조건문 대신 메시지(다형성)를 사용하는 것이 좋다.

```python
# --- 나쁜 예 ---
def calculate_pay(employee):
    if employee.type == "COMMISSIONED":
        return calculate_commissioned_pay(employee)
    elif employee.type == "HOURLY":
        return calculate_hourly_pay(employee)
    elif employee.type == "SALARIED":
        return calculate_salaried_pay(employee)

# --- 좋은 예 ---
class Employee:
    def calculate_pay(self) -> Money:
        raise NotImplementedError

class CommissionedEmployee(Employee):
    def calculate_pay(self) -> Money: ...

class HourlyEmployee(Employee):
    def calculate_pay(self) -> Money: ...

class SalariedEmployee(Employee):
    def calculate_pay(self) -> Money: ...
```

### 8.4 위임으로 유연성 확보 [IP]

하위클래스는 정적(생성 시점 결정)이지만 위임은 런타임에 변경 가능하다.

```python
# --- 나쁜 예: 조건문으로 도구 분기 ---
def mouse_down(self):
    if self.get_tool() == "SELECTING":
        ...
    elif self.get_tool() == "CREATING_RECTANGLE":
        ...

# --- 좋은 예: 위임 ---
def mouse_down(self):
    self.get_tool().mouse_down()  # 도구 객체에 위임
```

### 8.5 로직과 데이터를 함께 유지하라 [IP]

데이터와 그 데이터를 처리하는 로직을 밀접하게, 가급적 같은 메서드 혹은 같은 객체 내에 배치하라.

```python
# --- 나쁜 예 ---
def format_address(street, city, state, zipcode):
    return f"{street}, {city}, {state} {zipcode}"

# --- 좋은 예 ---
class Address:
    def __init__(self, street, city, state, zipcode):
        self.street = street
        self.city = city
        self.state = state
        self.zipcode = zipcode

    def format(self):
        return f"{self.street}, {self.city}, {self.state} {self.zipcode}"
```

### 8.6 변화율에 따라 분리하라 [IP]

함께 변하는 로직과 데이터는 함께 관리하고, 변화율이 다른 것은 분리한다.

```python
# --- 나쁜 예 ---
class Payment:
    def __init__(self, value, currency):
        self.value = value
        self.currency = currency  # value와 currency는 항상 함께 변한다

# --- 좋은 예 ---
class Money:
    def __init__(self, value, currency):
        self.value = value
        self.currency = currency

class Payment:
    def __init__(self, amount: Money):
        self.amount = amount  # 대칭적인 필드를 별도 객체로 분리
```

---

## 9. SOLID 원칙

### 9.1 단일 책임 원칙 (SRP) [PC] [CC]

클래스는 하나의 책임만 가져야 하며, 변경 이유도 단 하나여야 한다.

```python
# --- 나쁜 예 ---
class SystemMonitor:
    def load_activity(self): ...
    def identify_events(self): ...
    def stream_events(self): ...  # 세 가지 독립적 책임

# --- 좋은 예 ---
class ActivityLoader: ...
class EventIdentifier: ...
class EventStreamer: ...
```

> "만약 객체의 속성이나 메서드의 특성이 다른 클래스에서 발견되면 이들을 다른 곳으로 옮겨야 한다." **[PC]**

#### Django/dddjango 경계에서의 책임 분리

웹 프레임워크 코드는 도메인 규칙, 입출력 변환, 저장소 접근, 렌더링, 권한/인증, 트랜잭션 경계가 한 함수나 클래스에 모이기 쉽다. 이때 파일 이름이나 계층 이름보다 **변경 이유**가 우선 판단 기준이다.

| 스멜 | 증상 | 클린 코드 관점의 판단 |
|------|------|-----------------------|
| **Fat Model** | Django model이 ORM 매핑, 도메인 상태 전이, 외부 알림, 결제/재고/권한 정책, 조회 포맷까지 모두 처리한다 | 데이터와 불변식을 가까이 두는 것은 좋지만, 외부 I/O나 유스케이스 흐름까지 model에 넣으면 변경 이유가 섞인다. |
| **Fat View / Fat Router** | view, Django Ninja router, DRF view가 요청 파싱 뒤 권한, 상태 전이, 계산, 저장, 알림, 응답 포맷을 긴 절차로 모두 수행한다 | framework entrypoint는 얇게 유지하고, 의도 있는 application/service 함수나 도메인 객체에 정책을 맡긴다. |
| **Fat Schema / Serializer** | schema나 serializer가 validation을 넘어 주문 상태 변경, 가격 계산, DB 조회, 외부 호출을 수행한다 | 입출력 계약과 도메인 정책이 섞여 테스트와 재사용이 어려워진다. |
| **Template business logic** | template tag, include, HTMX partial에서 권한/상태/가격 정책을 직접 계산한다 | 렌더링 관심사가 도메인 규칙을 숨기면 변경 누락과 중복이 커진다. |
| **Service dumping ground** | 모든 로직을 `services.py`로 옮겼지만 함수들이 서로 다른 정책과 I/O를 공유 전역처럼 사용한다 | 이름만 service인 얕은 모듈은 책임 분리가 아니다. 유스케이스, 도메인 규칙, 조회, 외부 연동의 변경 이유를 다시 나눠야 한다. |

다만 모든 Django model method가 Fat Model인 것은 아니다. 단일 엔티티의 불변식, 상태 질의, 표현 독립적인 작은 행위는 model이나 값 객체에 두는 편이 더 응집도 높을 수 있다. 반대로 transaction, locking, idempotency, aggregate 경계, REST contract, API error shape처럼 설계 결정이 먼저 필요한 문제는 클린 코드 스멜로만 처리하지 않고 DB/API/DDD 관련 기준으로 라우팅해야 한다.

### 9.2 개방/폐쇄 원칙 (OCP) [PC] [CC]

확장에는 개방되고 수정에는 폐쇄되어야 한다. 새로운 요구사항이 생기면 새로운 것을 추가만 할 뿐 기존 코드는 그대로 유지해야 한다.

```python
# --- 나쁜 예 ---
class SystemMonitor:
    def identify_event(self):
        if self.event_data["before"]["session"] == 0 and \
           self.event_data["after"]["session"] == 1:
            return LoginEvent(self.event_data)
        # 새 이벤트마다 이 메서드를 수정해야 한다

# --- 좋은 예 ---
class Event:
    @staticmethod
    def meets_condition(event_data: dict) -> bool:
        return False

class LoginEvent(Event):
    @staticmethod
    def meets_condition(event_data: dict) -> bool:
        return (event_data["before"]["session"] == 0
                and event_data["after"]["session"] == 1)

class SystemMonitor:
    def identify_event(self):
        for event_cls in Event.__subclasses__():
            if event_cls.meets_condition(self.event_data):
                return event_cls(self.event_data)
        return UnknownEvent(self.event_data)
```

### 9.3 리스코프 치환 원칙 (LSP) [PC] [OO]

하위 클래스는 부모 클래스를 대체할 수 있어야 한다. 클라이언트는 사용하는 클래스의 계층 구조 변경에 대해 완전히 독립적이어야 한다.

```python
# --- 나쁜 예: LSP 위반 ---
class Event:
    def meets_condition(self, event_data: dict) -> bool:
        return False

class LoginEvent(Event):
    def meets_condition(self, event_data: list) -> bool:  # 파라미터 타입 변경!
        return bool(event_data)

# --- 좋은 예 ---
class LoginEvent(Event):
    def meets_condition(self, event_data: dict) -> bool:  # 부모와 동일한 서명
        return event_data.get("after", {}).get("session") == 1
```

### 9.4 인터페이스 분리 원칙 (ISP) [PC]

작은 인터페이스를 만들어라. 클라이언트가 필요하지 않은 메서드를 구현하도록 강제하지 마라.

```python
# --- 나쁜 예 ---
class EventParser:
    def from_xml(self): ...
    def from_json(self): ...  # 어떤 클래스는 둘 중 하나만 필요할 수 있다

# --- 좋은 예 ---
class XMLEventParser:
    def from_xml(self): ...

class JSONEventParser:
    def from_json(self): ...
```

### 9.5 의존성 역전 원칙 (DIP) [PC]

구체적 구현이 아닌 추상화에 의존하라. 세부 사항은 추상화에 의존해야 한다.

```python
# --- 나쁜 예 ---
class EventStreamer:
    def __init__(self):
        self._target = Syslog()  # 구체 클래스에 직접 의존

# --- 좋은 예 ---
class EventStreamer:
    def __init__(self, target: DataTargetClient):  # 인터페이스에 의존
        self._target = target

    def stream(self, events):
        for event in events:
            self._target.send(event.serialize())
```

> "일반적으로 구체적인 구현이 추상 컴포넌트보다 훨씬 더 자주 바뀔 것이다. 이런 이유로 추상화를 사용한다." **[PC]**

---

## 10. 디자인 패턴

범용 GoF/Kent Beck 패턴의 핵심 개념과 구조를 다룬다. 원칙 자체는 언어 비종속적이며, 코드 예시는 Python으로 작성되었다.

### 10.1 팩토리 메서드 (Factory Method) [GoF]

객체 생성을 서브클래스에 위임하여, 생성할 구체 클래스를 결정하는 코드와 사용하는 코드를 분리한다. OCP(개방/폐쇄 원칙)를 준수하여 새로운 타입 추가 시 기존 코드를 수정하지 않는다.

```python
# --- 나쁜 예: 생성 로직이 조건문에 직접 묶임 ---
class NotificationService:
    def send(self, type_: str, message: str) -> None:
        if type_ == "email":
            print(f"Email: {message}")
        elif type_ == "sms":
            print(f"SMS: {message}")
        # 새 타입 추가마다 이 메서드를 수정해야 한다

# --- 좋은 예: 팩토리 메서드로 생성 위임 ---
from abc import ABC, abstractmethod

class Notification(ABC):
    @abstractmethod
    def send(self, message: str) -> None: ...

class EmailNotification(Notification):
    def send(self, message: str) -> None:
        print(f"Email: {message}")

class SMSNotification(Notification):
    def send(self, message: str) -> None:
        print(f"SMS: {message}")

class NotificationFactory(ABC):
    @abstractmethod
    def create(self) -> Notification: ...

class EmailFactory(NotificationFactory):
    def create(self) -> Notification:
        return EmailNotification()

class SMSFactory(NotificationFactory):
    def create(self) -> Notification:
        return SMSNotification()

# 사용: 새 타입은 새 Factory 서브클래스만 추가
def notify(factory: NotificationFactory, message: str) -> None:
    notification = factory.create()
    notification.send(message)
```

### 10.2 추상 팩토리 (Abstract Factory) [GoF]

연관된 객체군을 구상 클래스 이름 없이 생성한다. 상속보다 구성(composition)을 선호하며, 제품군 전체를 일관되게 교체할 수 있다.

```python
# --- 나쁜 예: 구상 클래스에 직접 의존 ---
class Application:
    def __init__(self) -> None:
        self.button = WindowsButton()  # OS 교체 시 전부 수정
        self.checkbox = WindowsCheckbox()

# --- 좋은 예: 추상 팩토리로 제품군 생성 ---
from abc import ABC, abstractmethod

class Button(ABC):
    @abstractmethod
    def render(self) -> str: ...

class Checkbox(ABC):
    @abstractmethod
    def render(self) -> str: ...

class GUIFactory(ABC):
    @abstractmethod
    def create_button(self) -> Button: ...
    @abstractmethod
    def create_checkbox(self) -> Checkbox: ...

class WindowsButton(Button):
    def render(self) -> str:
        return "<win-btn/>"

class WindowsCheckbox(Checkbox):
    def render(self) -> str:
        return "<win-chk/>"

class WindowsFactory(GUIFactory):
    def create_button(self) -> Button:
        return WindowsButton()
    def create_checkbox(self) -> Checkbox:
        return WindowsCheckbox()

class MacFactory(GUIFactory):
    def create_button(self) -> Button:
        return MacButton()
    def create_checkbox(self) -> Checkbox:
        return MacCheckbox()

# 사용: 팩토리만 교체하면 제품군 전체가 바뀜
class Application:
    def __init__(self, factory: GUIFactory) -> None:
        self.button = factory.create_button()
        self.checkbox = factory.create_checkbox()
```

### 10.3 값 객체 (Value Object) [Kent Beck]

불변이며 동등성(equality)으로 비교하는 객체다. 별칭(aliasing) 문제를 원천 차단하고, 도메인 개념을 명확하게 표현한다.

```python
# --- 나쁜 예: 원시 타입으로 도메인 개념 표현 ---
price = 1000       # 통화 정보 없음, 음수 가능, 별칭 문제
currency = "KRW"   # price와 currency의 관계가 암묵적

# --- 좋은 예: 값 객체로 도메인 개념 캡슐화 ---
from dataclasses import dataclass

@dataclass(frozen=True)
class Money:
    amount: int
    currency: str

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError("금액은 음수일 수 없다")

    def add(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("통화가 다르면 합산할 수 없다")
        return Money(self.amount + other.amount, self.currency)

# 불변: 한번 생성하면 변경 불가, 별칭 문제 없음
price = Money(1000, "KRW")
total = price.add(Money(500, "KRW"))  # Money(1500, "KRW")
```

### 10.4 널 객체 (Null Object) [Kent Beck]

None 검사를 반복하는 대신, 아무 일도 하지 않는 객체를 사용한다. 다형성을 활용하여 조건문을 제거하고 코드 흐름을 단순화한다.

```python
# --- 나쁜 예: None 검사가 곳곳에 산재 ---
class UserService:
    def get_logger(self) -> Logger | None:
        return self._logger

    def process(self) -> None:
        logger = self.get_logger()
        if logger is not None:     # 매번 None 검사
            logger.info("처리 시작")
        self._do_work()
        if logger is not None:     # 또 None 검사
            logger.info("처리 완료")

# --- 좋은 예: 널 객체로 None 검사 제거 ---
class NullLogger:
    """아무 일도 하지 않는 로거."""
    def info(self, msg: str) -> None:
        pass

    def error(self, msg: str) -> None:
        pass

class UserService:
    def __init__(self, logger: Logger | None = None) -> None:
        self._logger = logger or NullLogger()

    def process(self) -> None:
        self._logger.info("처리 시작")   # None 검사 불필요
        self._do_work()
        self._logger.info("처리 완료")   # 항상 안전하게 호출
```

### 10.5 전략 패턴 (Strategy) [GoF]

알고리즘을 캡슐화하여 런타임에 교체할 수 있게 한다. 조건문(if/elif 체인)을 다형성으로 대체하며, 새로운 전략 추가 시 기존 코드를 수정하지 않는다.

```python
# --- 나쁜 예: 조건문으로 알고리즘 분기 ---
def calculate_discount(price: int, method: str) -> int:
    if method == "fixed":
        return price - 1000
    elif method == "percent":
        return int(price * 0.9)
    elif method == "vip":
        return int(price * 0.8)
    # 새 할인 방식마다 이 함수를 수정해야 한다

# --- 좋은 예: 전략 패턴으로 알고리즘 캡슐화 ---
from typing import Protocol

class DiscountStrategy(Protocol):
    def apply(self, price: int) -> int: ...

class FixedDiscount:
    def __init__(self, amount: int = 1000) -> None:
        self._amount = amount

    def apply(self, price: int) -> int:
        return price - self._amount

class PercentDiscount:
    def __init__(self, rate: float = 0.1) -> None:
        self._rate = rate

    def apply(self, price: int) -> int:
        return int(price * (1 - self._rate))

# 사용: 전략 객체만 교체
def calculate_discount(price: int, strategy: DiscountStrategy) -> int:
    return strategy.apply(price)

final_price = calculate_discount(10000, PercentDiscount(rate=0.2))
```

### 10.6 옵저버 패턴 (Observer) [GoF]

객체의 상태 변경을 관찰자들에게 자동으로 통보한다. 발행자와 구독자를 느슨하게 결합하여, 서로의 구체적인 구현을 알 필요 없이 협력한다.

```python
# --- 나쁜 예: 직접 호출로 강한 결합 ---
class Order:
    def complete(self) -> None:
        self._status = "completed"
        EmailService().send_confirmation(self)   # 직접 의존
        InventoryService().update_stock(self)     # 직접 의존
        AnalyticsService().track_purchase(self)   # 새 서비스마다 수정

# --- 좋은 예: 옵저버 패턴으로 느슨한 결합 ---
from typing import Protocol

class OrderObserver(Protocol):
    def on_order_completed(self, order: "Order") -> None: ...

class Order:
    def __init__(self) -> None:
        self._observers: list[OrderObserver] = []

    def add_observer(self, observer: OrderObserver) -> None:
        self._observers.append(observer)

    def complete(self) -> None:
        self._status = "completed"
        for observer in self._observers:
            observer.on_order_completed(self)

class EmailNotifier:
    def on_order_completed(self, order: Order) -> None:
        print(f"확인 메일 발송: {order}")

class StockUpdater:
    def on_order_completed(self, order: Order) -> None:
        print(f"재고 갱신: {order}")

# 사용: 옵저버 추가/제거만으로 기능 확장
order = Order()
order.add_observer(EmailNotifier())
order.add_observer(StockUpdater())
order.complete()
```

### 10.7 템플릿 메서드 (Template Method) [GoF] [Kent Beck]

알고리즘의 전체 순서(골격)를 상위 클래스에서 고정하고, 각 단계의 구체적 구현은 하위 클래스에서 정의한다. 공통 흐름의 중복을 제거하면서 세부 동작을 유연하게 변경할 수 있다.

```python
# --- 나쁜 예: 흐름이 각 클래스에 중복 ---
class CSVExporter:
    def export(self, data: list) -> str:
        header = ",".join(data[0].keys())       # 1) 헤더
        rows = [",".join(map(str, d.values())) for d in data]  # 2) 본문
        return header + "\n" + "\n".join(rows)  # 3) 조립

class JSONExporter:
    def export(self, data: list) -> str:
        import json
        header = ""                              # 1) 헤더 (불필요하지만 흐름 중복)
        body = json.dumps(data, ensure_ascii=False)  # 2) 본문
        return body                              # 3) 조립

# --- 좋은 예: 템플릿 메서드로 흐름 고정 ---
from abc import ABC, abstractmethod

class DataExporter(ABC):
    def export(self, data: list) -> str:
        """알고리즘 골격: 순서를 고정한다."""
        header = self.build_header(data)
        body = self.build_body(data)
        return self.assemble(header, body)

    @abstractmethod
    def build_header(self, data: list) -> str: ...

    @abstractmethod
    def build_body(self, data: list) -> str: ...

    def assemble(self, header: str, body: str) -> str:
        """기본 조립: 하위 클래스에서 재정의 가능."""
        return f"{header}\n{body}" if header else body

class CSVExporter(DataExporter):
    def build_header(self, data: list) -> str:
        return ",".join(data[0].keys())

    def build_body(self, data: list) -> str:
        return "\n".join(",".join(map(str, d.values())) for d in data)

class JSONExporter(DataExporter):
    def build_header(self, data: list) -> str:
        return ""

    def build_body(self, data: list) -> str:
        import json
        return json.dumps(data, ensure_ascii=False)
```

### 10.8 플러거블 객체 (Pluggable Object) [Kent Beck]

동일한 조건문이 두 번 이상 반복되면, 조건 분기를 객체로 대체한다. 조건을 생성 시점에 한 번만 결정하고 이후에는 다형성으로 해결한다.

```python
# --- 나쁜 예: 같은 조건문이 여러 곳에 반복 ---
class GraphEditor:
    def __init__(self, mode: str) -> None:
        self.mode = mode

    def on_mouse_down(self, x: int, y: int) -> None:
        if self.mode == "select":
            self._start_selection(x, y)
        elif self.mode == "draw":
            self._start_drawing(x, y)

    def on_mouse_up(self, x: int, y: int) -> None:
        if self.mode == "select":        # 같은 조건 반복!
            self._finish_selection(x, y)
        elif self.mode == "draw":        # 같은 조건 반복!
            self._finish_drawing(x, y)

# --- 좋은 예: 플러거블 객체로 조건문 제거 ---
from typing import Protocol

class Tool(Protocol):
    def on_mouse_down(self, x: int, y: int) -> None: ...
    def on_mouse_up(self, x: int, y: int) -> None: ...

class SelectionTool:
    def on_mouse_down(self, x: int, y: int) -> None:
        print(f"선택 시작: ({x}, {y})")

    def on_mouse_up(self, x: int, y: int) -> None:
        print(f"선택 완료: ({x}, {y})")

class DrawingTool:
    def on_mouse_down(self, x: int, y: int) -> None:
        print(f"그리기 시작: ({x}, {y})")

    def on_mouse_up(self, x: int, y: int) -> None:
        print(f"그리기 완료: ({x}, {y})")

class GraphEditor:
    def __init__(self, tool: Tool) -> None:
        self._tool = tool  # 조건을 생성 시점에 한 번만 결정

    def on_mouse_down(self, x: int, y: int) -> None:
        self._tool.on_mouse_down(x, y)  # 조건문 없음

    def on_mouse_up(self, x: int, y: int) -> None:
        self._tool.on_mouse_up(x, y)    # 조건문 없음
```

> Python 고유 구현 트릭(`__init_subclass__` 레지스트리 등)은 `workspace/reference/implementation-python/reference/final.md`를 참조한다.

---

## 11. 상태 관리

### 11.1 변수의 범위와 생명주기를 일치시켜라 [IP] [CodeC]

변수의 범위와 생명기간은 가까운 것이 좋다. 같은 범위에서 정의된 변수들은 같은 생명기간을 갖는 것이 좋다. **[IP]**

**변수의 "생존 시간(live time)"을 최소화**하라. 변수가 선언된 후 마지막으로 참조되기까지의 거리가 짧을수록 좋다. **[CodeC]**

```python
# --- 나쁜 예 ---
result = None  # 훨씬 나중에 사용될 변수를 미리 선언
# ... 100줄의 코드 ...
result = compute()

# --- 좋은 예 ---
# ... 100줄의 코드 ...
result = compute()  # 사용 직전에 선언
```

### 11.2 값 객체를 활용하라 [IP] [OO]

변치 않는 값을 표현할 때는 값 객체를 사용하라. 생성 후 상태가 변경되지 않아야 한다.

```python
# --- 나쁜 예: 가변 상태 ---
class Transaction:
    def __init__(self, value):
        self.value = value  # 외부에서 변경 가능

# --- 좋은 예: 값 객체 ---
from dataclasses import dataclass

@dataclass(frozen=True)
class Transaction:
    value: int
    credit_account: str
    debit_account: str
    # frozen=True로 불변 보장
```

### 11.3 상태 접근은 간접 접근을 기본으로 [IP]

내부에서는 직접 접근을 허용하되, 외부에서는 메서드를 통해 접근하라.

```python
# --- 나쁜 예 ---
class Rectangle:
    def __init__(self):
        self.width = 0
        self.height = 0
        self.area = 0  # width/height와 의존 관계인데 직접 접근

# --- 좋은 예 ---
class Rectangle:
    def __init__(self, width, height):
        self._width = width
        self._height = height

    @property
    def area(self):
        return self._width * self._height
```

### 11.4 공용 상태 vs 가변 상태 [IP]

- **공용 상태**: 여러 연산에서 같은 데이터를 사용하는 경우 필드로 선언
- **가변 상태**: 인스턴스마다 전혀 다른 데이터 요소가 필요한 경우에만 맵으로 표현
- 가능하다면 공용 상태를 사용하는 것이 좋다

---

## 12. 오류 처리

> **통합 원칙**: 오류 처리는 두 단계로 접근한다. **1순위**: 오류 조건 자체를 설계에서 제거한다 **[APoSD]**. **2순위**: 설계로 제거할 수 없는 오류는 예외와 계약(DbC)으로 처리한다 **[CC] [PC]**.

### 12.1 1순위: 오류를 존재에서 제거하라 [APoSD]

예외 처리는 소프트웨어 시스템에서 **가장 큰 복잡성 원천 중 하나**다. 가능하다면 오류 조건 자체를 설계적으로 제거하라.

```python
# --- 나쁜 예: 오류 조건이 불필요하게 존재 ---
class TextBuffer:
    def delete_selection(self):
        if not self.has_selection():
            raise NoSelectionError("Nothing is selected")
        # ... 삭제 로직

# --- 좋은 예: 오류를 존재에서 제거 ---
class TextBuffer:
    def delete_selection(self):
        """현재 선택 영역을 삭제한다. 선택이 없으면 아무것도 하지 않는다."""
        if not self.has_selection():
            return  # 예외 대신 정상 흐름으로 처리
        # ... 삭제 로직
```

### 12.2 2순위: 오류 코드보다 예외를 사용하라 [CC]

오류 코드를 반환하면 호출자는 오류 코드를 곧바로 처리해야 하고, 명령/조회 분리 규칙을 위반한다.

```python
# --- 나쁜 예 ---
result = delete_page(page)
if result == E_OK:
    result = registry.delete_reference(page.name)
    if result == E_OK:
        ...

# --- 좋은 예 ---
try:
    delete_page_and_all_references(page)
except PageDeletionError as error:
    logger.error(error)
```

### 12.3 Try/Catch 분리는 의도와 인지 경계를 따른다 [CC]

정상 동작과 오류 처리 동작을 분리하면 이해하고 수정하기 쉬워진다. 이는 모든
`catch`를 별도 함수로 추출하라는 절대 명령이 아니라, 정상 흐름과 오류 흐름의
의도가 한 눈에 구분되게 하는 인지 경계 원칙이다. `try`에는 처리 대상의 최외곽
호출만 두고, 실제로 처리할 수 있는 구체 예외만 잡는다(§12.7).

```python
# --- 좋은 예 ---
def delete(page):
    try:
        delete_page_and_all_references(page)
    except PageDeletionError as error:
        log_error(error)

def delete_page_and_all_references(page):
    delete_page(page)
    registry.delete_reference(page.name)
    config_keys.delete_key(page.name.make_key())
```

선택한 framework/profile이 adapter entrypoint에 예외→전송 응답 매핑의 소유권을
명시적으로 부여한 경우에는, 그 entrypoint 안에 작은 구체 `catch`와 준비된 오류
응답의 직접 반환을 유지할 수 있다. 예를 들어 Django Ninja controller operation이
known application/domain exception을 잡아 준비된 concrete `ErrorSchema`를
`Status(<승인된 HTTP status 표현>, error)`로 직접 반환하는 규율은
`implementation-django-ninja` §6.2를 따른다. 이때 분리 원칙을 맞추기 위해서만
mapping helper/factory/handler를 추출하지 않는다. 단, 이 자격은 광범위 catch를
허용하지 않으며, `try` 범위를 넓히거나 정상/오류 흐름을 뒤섞는 근거가 되지 않는다.
resource cleanup, transaction, retry, 예외 추상화의 소유와 규율도 각각 그대로 따른다.

### 12.4 올바른 추상화 수준에서 예외를 처리하라 [PC]

예외는 함수가 캡슐화하고 있는 로직에 대한 것이어야 한다. 서로 다른 수준의 추상화를 혼합하지 마라.

### 12.5 보호절(Guard Clause)을 활용하라 [IP]

주요 흐름과 예외 흐름의 차이를 부각시켜라.

```python
# --- 나쁜 예 ---
def compute():
    server = get_server()
    if server is not None:
        client = server.get_client()
        if client is not None:
            request = client.get_request()
            if request is not None:
                process_request(request)

# --- 좋은 예 ---
def compute():
    server = get_server()
    if server is None: return
    client = server.get_client()
    if client is None: return
    request = client.get_request()
    if request is None: return
    process_request(request)
```

### 12.6 계약에 의한 디자인 (DbC) [PC]

사전조건과 사후조건을 명시적으로 정의하여 책임 소재를 명확히 하라.

```python
def add_positive_numbers(a: float, b: float) -> float:
    """양수 두 개를 더한다."""
    if a <= 0 or b <= 0:
        raise ValueError("입력 값은 양수여야 합니다")  # 사전 조건

    result = a + b

    assert result > 0, "결과 값은 양수여야 합니다"  # 사후 조건
    return result
```

### 12.7 방어적 프로그래밍 [CodeC]

잘못된 입력으로부터 프로그램을 보호하라. "외부"를 어디로 정할지 결정하고, 그 경계에서 데이터를 검증하라. 예외는 구체적으로 잡는다 — 모든 예외를 무차별로 삼키면(bare/광범위 catch) 버그가 가려지므로, 실제로 처리할 수 있는 구체적 예외 유형만 명시한다.

#### 단언(Assertion) vs 오류 처리

| 상황 | 기법 |
|------|------|
| 절대 발생해서는 안 되는 조건 | `assert` 사용 |
| 발생할 수 있는 예상된 조건 | 오류 처리 코드 사용 |
| 고신뢰성이 필요한 코드 | 둘 다 사용 |

```python
# Assertion: 개발 중 논리 오류 탐지
def calculate_discount(price: float, rate: float) -> float:
    assert 0.0 <= rate <= 1.0, f"Discount rate must be 0-1, got {rate}"
    assert price >= 0, f"Price must be non-negative, got {price}"
    return price * (1 - rate)

# 오류 처리: 외부 입력 검증
def parse_user_input(raw_rate: str) -> float:
    try:
        rate = float(raw_rate)
    except ValueError:
        raise InvalidInputError(f"'{raw_rate}' is not a valid number")
    if not 0.0 <= rate <= 1.0:
        raise InvalidInputError(f"Rate must be between 0 and 1, got {rate}")
    return rate
```

#### 정확성(Correctness) vs 견고성(Robustness)

- **정확성**: 부정확한 결과를 절대 반환하지 않는다 (안전 필수 시스템)
- **견고성**: 소프트웨어가 계속 작동하도록 최선을 다한다 (소비자 앱)

```python
# 정확성 우선 (안전 필수 시스템)
def calculate_medication_dose(weight_kg: float, dosage_per_kg: float) -> float:
    if weight_kg <= 0 or dosage_per_kg <= 0:
        raise CriticalError("Invalid medication calculation parameters")
    dose = weight_kg * dosage_per_kg
    if dose > MAX_SAFE_DOSE:
        raise CriticalError(f"Dose {dose}mg exceeds safety limit")
    return dose

# 견고성 우선 (소비자 앱)
def load_user_preferences(path: str) -> dict:
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return DEFAULT_PREFERENCES  # 기본값으로 계속 동작
```

---

## 13. 중복 제거와 DRY

### 13.1 DRY는 지식의 중복을 금지하는 것이다 [PP]

> "모든 지식은 시스템 안에서 단일하고 모호하지 않은 권위 있는 표현을 가져야 한다." **[PP]**

DRY는 단순한 코드 중복 금지가 아니다. **지식의 중복**을 금지하는 것이다. 같은 코드라도 서로 다른 지식을 표현한다면 중복이 아닐 수 있고, 다른 코드라도 같은 지식을 표현한다면 DRY 위반이다.

```python
# DRY 위반: 같은 검증 지식이 두 곳에
class UserValidator:
    def validate_age(self, age: int) -> bool:
        return 0 < age < 150

class UserForm:
    def is_valid_age(self, age: int) -> bool:
        return age > 0 and age < 150  # 같은 규칙의 다른 표현

# DRY 준수: 검증 규칙의 단일 소스
class AgePolicy:
    MIN_AGE = 0
    MAX_AGE = 150

    @classmethod
    def is_valid(cls, age: int) -> bool:
        return cls.MIN_AGE < age < cls.MAX_AGE

class UserValidator:
    def validate_age(self, age: int) -> bool:
        return AgePolicy.is_valid(age)
```

```python
# DRY가 아닌 경우: 우연히 같은 코드지만 다른 지식
def validate_user_age(age: int) -> bool:
    return 0 < age < 150  # 사용자 나이 정책

def validate_building_floors(floors: int) -> bool:
    return 0 < floors < 150  # 건물 층수 제한 -- 우연히 같은 범위

# 이 두 함수를 합치면 안 된다. 서로 다른 도메인 지식을 표현한다.
```

### 13.2 코드 중복 제거 예시 [CC] [PC]

> "어쩌면 중복은 소프트웨어에서 모든 악의 근원이다." **[CC]**

```python
# --- 나쁜 예 ---
def process_students(students):
    ranking = sorted(students, key=lambda s: s.passed * 11 - s.failed * 5)
    for student in ranking:
        score = student.passed * 11 - student.failed * 5  # 중복!
        print(f"{student.name}: {score}")

# --- 좋은 예 ---
def calculate_score(student) -> int:
    return student.passed * 11 - student.failed * 5

def process_students(students):
    ranking = sorted(students, key=calculate_score)
    for student in ranking:
        print(f"{student.name}: {calculate_score(student)}")
```

### 13.3 지역적 변화의 원칙 [IP]

코드를 수정할 때 함께 바꿔야 하는 부분을 최소화하라. 중복을 없애는 방법은 프로그램을 여러 작은 부분으로 나누는 것이다.

---

## 14. 협력과 의존성 관리

### 14.1 역할, 책임, 협력 [OO]

> "객체지향에서 가장 중요한 개념은 역할, 책임, 협력이다." **[OO]**

- **역할**: 대체 가능성을 의미한다 (다형성)
- **책임**: 객체가 아는 것(knowing)과 하는 것(doing)으로 구성
- **협력**: 역할과 책임을 조화롭게 연결

### 14.2 메시지가 인터페이스를 결정한다 [OO]

> "객체가 메시지를 선택하는 것이 아니라 메시지가 객체를 선택하게 해야 한다." **[OO]**

어떤 행위(메시지)가 필요한지 먼저 결정한 후에, 이 행위를 수행할 객체를 결정하라 (What/Who 사이클).

### 14.3 응집력과 결합력 [PC] [IP]

- **응집력(Cohesion)**: 높을수록 좋다. 작고 잘 정의된 목적을 가진 모듈
- **결합력(Coupling)**: 낮을수록 좋다. 객체 간 의존성 최소화

```python
# --- 나쁜 예: 높은 결합력 ---
class Order:
    def process(self):
        db = MySQLDatabase()  # 구체 클래스에 직접 의존
        db.save(self.data)
        email = SMTPEmailSender()  # 또 다른 구체 클래스에 직접 의존
        email.send(self.confirmation)

# --- 좋은 예: 낮은 결합력 ---
class Order:
    def __init__(self, repository: Repository, notifier: Notifier):
        self._repository = repository
        self._notifier = notifier

    def process(self):
        self._repository.save(self.data)
        self._notifier.send(self.confirmation)
```

### 14.4 상속보다 합성을 우선하라 [IP] [PC] [OO]

상속의 단점:
- 되돌리기 어렵다
- 하위 클래스는 상위 클래스에 강하게 결합된다
- 동적으로 변화하는 로직을 나타낼 수 없다

> "단지 부모 클래스에 있는 메서드를 공짜로 얻을 수 있기 때문에 상속을 하는 것은 좋지 않다." **[PC]**

```python
# --- 나쁜 예: 재사용만을 위한 상속 ---
class TransactionPolicy(collections.UserList):
    """리스트의 모든 메서드가 노출됨 -- 필요하지 않은 것까지"""
    pass

# --- 좋은 예: 합성 ---
class TransactionPolicy:
    def __init__(self):
        self._transactions = []

    def add(self, transaction):
        self._transactions.append(transaction)

    def __len__(self):
        return len(self._transactions)
```

### 14.5 직교성 (Orthogonality) [PP]

두 가지 이상의 것이 직교적이면, 하나의 변경이 다른 것에 영향을 주지 않는다. 관련 없는 것들 사이의 영향을 제거하라.

```python
# --- 나쁜 예: 직교성 위반 -- UI 로직과 비즈니스 로직이 결합 ---
class ReportGenerator:
    def generate(self, data: list[dict]) -> str:
        html = "<html><body>"
        total = sum(item["amount"] for item in data)
        tax = total * 0.1  # 비즈니스 로직
        html += f"<h1>Total: {total}</h1>"  # UI 로직
        html += f"<p>Tax: {tax}</p>"
        html += "</body></html>"
        return html

# --- 좋은 예: 직교적 분리 ---
class TaxCalculator:
    RATE = 0.1
    def calculate(self, amount: float) -> float:
        return amount * self.RATE

class ReportData:
    def __init__(self, items: list[dict]):
        self.total = sum(item["amount"] for item in items)
        self.tax = TaxCalculator().calculate(self.total)

class HTMLReportRenderer:
    def render(self, report: ReportData) -> str:
        return (
            f"<html><body>"
            f"<h1>Total: {report.total}</h1>"
            f"<p>Tax: {report.tax}</p>"
            f"</body></html>"
        )
```

### 14.6 가역성 (Reversibility) [PP]

되돌리기 어려운 결정을 피하라. 추상화를 통해 핵심 결정을 교체 가능하게 만들라.

```python
# --- 나쁜 예: 특정 DB에 직접 결합 ---
import psycopg2

class UserRepository:
    def find(self, user_id: int):
        conn = psycopg2.connect(...)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        return cursor.fetchone()

# --- 좋은 예: 추상화로 결정을 가역적으로 만듬 ---
from typing import Protocol

class UserRepository(Protocol):
    def find(self, user_id: int) -> User | None: ...

class PostgresUserRepository:
    def find(self, user_id: int) -> User | None: ...

class MongoUserRepository:
    def find(self, user_id: int) -> User | None: ...

# DB를 바꿔도 UserRepository를 사용하는 코드는 변경 불필요
```

---

## 15. 리팩토링

### 15.1 코드 스멜 카탈로그 [Ref]

코드 스멜(code smell)은 더 깊은 문제를 나타내는 표면적 징후다. Kent Beck과 함께 정리한 이 목록은 리팩토링의 출발점이 된다.

#### 비대화 스멜 (Bloaters)

| 스멜 | 설명 | Python 예시 |
|------|------|-------------|
| **Long Method** | 메서드가 너무 길어 이해하기 어렵다 | 50줄 이상의 함수 |
| **Long Parameter List** | 파라미터가 너무 많다 | `def f(a, b, c, d, e, f, g):` |
| **Large Class** | 한 클래스가 너무 많은 책임을 진다 | 500줄 이상의 클래스 |
| **Primitive Obsession** | 원시 타입에 지나치게 의존한다 | 금액을 `float`로만 표현 |
| **Data Clumps** | 같은 데이터 그룹이 반복 등장한다 | `(x, y, z)` 좌표를 개별 변수로 전달 |

```python
# 코드 스멜: Primitive Obsession
def calculate_price(amount: float, currency: str) -> str:
    if currency == "USD":
        return f"${amount:.2f}"
    elif currency == "KRW":
        return f"{amount:,.0f}원"
    ...

# 리팩토링: 값 객체(Value Object) 도입
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str

    def display(self) -> str:
        formats = {
            "USD": lambda a: f"${a:.2f}",
            "KRW": lambda a: f"{a:,.0f}원",
        }
        formatter = formats.get(self.currency, lambda a: f"{a} {self.currency}")
        return formatter(self.amount)
```

```python
# 코드 스멜: Data Clumps
def distance(x1: float, y1: float, x2: float, y2: float) -> float:
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

# 리팩토링: Introduce Parameter Object
@dataclass(frozen=True)
class Point:
    x: float
    y: float

    def distance_to(self, other: "Point") -> float:
        return ((other.x - self.x) ** 2 + (other.y - self.y) ** 2) ** 0.5
```

#### 객체지향 남용 스멜 (OO Abusers)

| 스멜 | 설명 |
|------|------|
| **Refused Bequest** | 하위 클래스가 상속받은 메서드/속성 중 일부만 사용 |
| **Alternative Classes with Different Interfaces** | 같은 일을 하지만 인터페이스가 다른 클래스들 |
| **Temporary Field** | 특정 상황에서만 사용되는 인스턴스 변수 |

```python
# 코드 스멜: Refused Bequest
class Animal:
    def walk(self): ...
    def swim(self): ...
    def fly(self): ...

class Dog(Animal):
    def walk(self): ...
    def swim(self): ...
    def fly(self):
        raise NotImplementedError  # 개는 날 수 없다

# 리팩토링: 인터페이스 분리 (Protocol 사용)
from typing import Protocol

class Walkable(Protocol):
    def walk(self) -> None: ...

class Swimmable(Protocol):
    def swim(self) -> None: ...

class Dog:
    def walk(self) -> None: ...
    def swim(self) -> None: ...
    # fly는 필요 없으므로 구현하지 않는다
```

#### 변경 방해 스멜 (Change Preventers)

| 스멜 | 설명 |
|------|------|
| **Divergent Change** | 하나의 클래스가 여러 이유로 변경된다 (SRP 위반) |
| **Shotgun Surgery** | 하나의 변경이 여러 클래스에 산발적으로 영향 |
| **Parallel Inheritance Hierarchies** | 한 계층에 클래스를 추가하면 다른 계층에도 추가해야 한다 |

```python
# 코드 스멜: Shotgun Surgery
class Order:
    def total_with_tax(self):
        return self.subtotal * 1.1  # 세율 하드코딩

class Invoice:
    def tax_amount(self):
        return self.amount * 0.1  # 같은 세율이 다른 곳에도

# 리팩토링: Move Method -- 세금 로직을 한 곳으로 집중
class TaxCalculator:
    RATE = 0.1

    @classmethod
    def calculate(cls, amount: float) -> float:
        return amount * cls.RATE

class Order:
    def total_with_tax(self):
        return self.subtotal + TaxCalculator.calculate(self.subtotal)
```

#### 불필요한 것들 (Dispensables)

| 스멜 | 설명 |
|------|------|
| **Speculative Generality** | "나중에 필요할지도 모른다"는 이유로 추가한 미사용 추상화 |
| **Dead Code** | 실행되지 않는 코드 |
| **Lazy Class** | 하는 일이 너무 적어 존재 이유가 없는 클래스 |
| **Duplicated Code** | 같은 코드 구조의 반복 |

```python
# 코드 스멜: Speculative Generality
class AbstractDataProcessor:
    """미래를 위해 만든 추상 클래스 -- 현재 구현체는 하나뿐"""
    def process(self, data): raise NotImplementedError
    def validate(self, data): raise NotImplementedError
    def transform(self, data): raise NotImplementedError
    def serialize(self, data): raise NotImplementedError

class CSVProcessor(AbstractDataProcessor):
    # 유일한 구현체
    ...

# 리팩토링: 실제로 필요할 때까지 추상화를 미룬다 (YAGNI)
class CSVProcessor:
    def process(self, data): ...
    # 두 번째 구현체가 필요해질 때 공통 인터페이스를 추출한다
```

#### 커플러 스멜 (Couplers)

| 스멜 | 설명 |
|------|------|
| **Feature Envy** | 메서드가 자기 클래스보다 다른 클래스의 데이터를 더 많이 사용 |
| **Middle Man** | 메서드 대부분이 다른 객체에 위임만 한다 |
| **Inappropriate Intimacy** | 두 클래스가 서로의 내부를 지나치게 탐색 |
| **Message Chains** | `a.b().c().d()` 식의 긴 호출 체인 (디미터 법칙 위반) |

```python
# 코드 스멜: Feature Envy
class OrderPrinter:
    def print_details(self, order):
        print(f"Customer: {order.customer.name}")
        print(f"Address: {order.customer.address.street}")
        print(f"Total: {order.total()}")
        print(f"Tax: {order.total() * order.tax_rate}")

# 리팩토링: Move Method -- 해당 데이터를 가진 객체에 로직을 이동
class Order:
    def format_details(self) -> str:
        return (
            f"Customer: {self.customer.name}\n"
            f"Address: {self.customer.format_address()}\n"
            f"Total: {self.total()}\n"
            f"Tax: {self.calculate_tax()}"
        )
```

### 15.2 주요 리팩토링 기법 [Ref]

#### Extract Method

```python
# Before
def print_owing(self):
    print("*" * 40)
    print("****** Customer Owes ******")
    print("*" * 40)

    outstanding = 0.0
    for order in self.orders:
        outstanding += order.amount

    print(f"name: {self.name}")
    print(f"amount: {outstanding}")

# After
def print_owing(self):
    self._print_banner()
    outstanding = self._calculate_outstanding()
    self._print_details(outstanding)

def _print_banner(self):
    print("*" * 40)
    print("****** Customer Owes ******")
    print("*" * 40)

def _calculate_outstanding(self) -> float:
    return sum(order.amount for order in self.orders)

def _print_details(self, outstanding: float):
    print(f"name: {self.name}")
    print(f"amount: {outstanding}")
```

#### Replace Temp with Query

```python
# Before
def get_price(self):
    base_price = self.quantity * self.item_price
    if base_price > 1000:
        discount_factor = 0.95
    else:
        discount_factor = 0.98
    return base_price * discount_factor

# After
def get_price(self):
    return self._base_price * self._discount_factor

@property
def _base_price(self) -> float:
    return self.quantity * self.item_price

@property
def _discount_factor(self) -> float:
    return 0.95 if self._base_price > 1000 else 0.98
```

#### Decompose Conditional

```python
# Before
def calculate_charge(self, date, quantity):
    if date.month >= 6 and date.month <= 9:
        charge = quantity * self.summer_rate
    else:
        charge = quantity * self.winter_rate + self.winter_service_charge
    return charge

# After
def calculate_charge(self, date, quantity):
    if self._is_summer(date):
        return self._summer_charge(quantity)
    return self._winter_charge(quantity)

def _is_summer(self, date) -> bool:
    return 6 <= date.month <= 9

def _summer_charge(self, quantity) -> float:
    return quantity * self.summer_rate

def _winter_charge(self, quantity) -> float:
    return quantity * self.winter_rate + self.winter_service_charge
```

#### Replace Nested Conditional with Guard Clauses

```python
# Before
def get_pay_amount(self):
    if self.is_dead:
        result = self.dead_amount()
    else:
        if self.is_separated:
            result = self.separated_amount()
        else:
            if self.is_retired:
                result = self.retired_amount()
            else:
                result = self.normal_amount()
    return result

# After (Guard Clauses)
def get_pay_amount(self):
    if self.is_dead:
        return self.dead_amount()
    if self.is_separated:
        return self.separated_amount()
    if self.is_retired:
        return self.retired_amount()
    return self.normal_amount()
```

### 15.3 테이블 주도 방법 (Table-Driven Methods) [CodeC]

논리문(if/case) 대신 테이블에서 정보를 조회하는 기법. 거의 모든 논리적 선택을 테이블 조회로 대체할 수 있다.

```python
# --- 나쁜 예: 복잡한 조건 분기 ---
def get_insurance_rate(age: int, gender: str, smoker: bool) -> float:
    if age < 18:
        if gender == "male":
            if smoker:
                return 0.05
            else:
                return 0.03
        else:
            if smoker:
                return 0.04
            else:
                return 0.02
    elif age < 35:
        ...

# --- 좋은 예: Table-Driven Method ---
INSURANCE_RATES = {
    ("youth", "male", True): 0.05,
    ("youth", "male", False): 0.03,
    ("youth", "female", True): 0.04,
    ("youth", "female", False): 0.02,
    ("adult", "male", True): 0.08,
    ("adult", "male", False): 0.05,
}

def _age_group(age: int) -> str:
    if age < 18:
        return "youth"
    if age < 35:
        return "adult"
    return "senior"

def get_insurance_rate(age: int, gender: str, smoker: bool) -> float:
    key = (_age_group(age), gender, smoker)
    rate = INSURANCE_RATES.get(key)
    if rate is None:
        raise ValueError(f"No rate defined for {key}")
    return rate
```

---

## 16. 레거시 코드 다루기

### 16.1 레거시 코드의 정의 [WELC]

> **레거시 코드란 테스트가 없는 코드다.**

아무리 잘 작성되었든, 아무리 예쁘고 객체지향적이고 잘 캡슐화되었든, 테스트가 없으면 레거시 코드다.

### 16.2 Seam 개념 [WELC]

**Seam**: 코드를 편집하지 않고도 동작을 변경할 수 있는 지점. 테스트를 삽입하기 위한 틈새를 찾는 핵심 개념.

| Seam 유형 | 설명 | Python 적용 |
|-----------|------|-------------|
| **Object Seam** | 인터페이스를 정의하고 프로덕션 객체를 테스트용 가짜 객체로 교체 | Protocol + 의존성 주입 |
| **Link Seam** | 구현 함수를 교체 | 모듈 수준 함수 교체 (monkeypatch) |

```python
# Object Seam: 의존성 주입으로 테스트 가능하게 만들기

# Before: 테스트 불가능 (외부 서비스에 직접 결합)
class OrderService:
    def place_order(self, order: Order) -> None:
        import smtplib
        server = smtplib.SMTP("smtp.company.com")
        server.send_message(...)

# After: Object Seam 도입 (테스트 가능)
from typing import Protocol

class EmailSender(Protocol):
    def send(self, to: str, subject: str, body: str) -> None: ...

class OrderService:
    def __init__(self, email_sender: EmailSender) -> None:
        self._email_sender = email_sender

    def place_order(self, order: Order) -> None:
        self._email_sender.send(
            to=order.customer_email,
            subject="Order Confirmation",
            body=f"Order {order.id} placed.",
        )

# 테스트에서 가짜 객체 사용
class FakeEmailSender:
    def __init__(self):
        self.sent_emails: list[tuple[str, str, str]] = []

    def send(self, to: str, subject: str, body: str) -> None:
        self.sent_emails.append((to, subject, body))

def test_place_order():
    sender = FakeEmailSender()
    service = OrderService(email_sender=sender)
    service.place_order(sample_order)
    assert len(sender.sent_emails) == 1
```

### 16.3 Sprout Method (발아 메서드) [WELC]

새 기능을 추가할 때, 기존 코드를 수정하지 않고 **새 메서드로 작성**한 후 기존 코드에서 호출한다.

```python
# 기존 레거시 코드 (테스트 없음, 수정하기 위험)
class TransactionGate:
    def post_entries(self, entries: list) -> None:
        for entry in entries:
            entry.post_date = datetime.now()
            self._verify_entry(entry)
            self._persist(entry)

# 새 요구사항: 중복 항목 필터링 추가
# Sprout Method: 새 기능을 별도 메서드로 작성 (테스트 가능)
class TransactionGate:
    def post_entries(self, entries: list) -> None:
        unique_entries = self._remove_duplicates(entries)  # 새 메서드 호출
        for entry in unique_entries:
            entry.post_date = datetime.now()
            self._verify_entry(entry)
            self._persist(entry)

    def _remove_duplicates(self, entries: list) -> list:
        """중복 항목을 제거한다. (새 메서드 -- 단위 테스트 작성 가능)"""
        seen = set()
        unique = []
        for entry in entries:
            if entry.id not in seen:
                seen.add(entry.id)
                unique.append(entry)
        return unique
```

### 16.4 Wrap Method (감싸기 메서드) [WELC]

기존 메서드를 래핑하여 전후에 새 동작을 추가한다.

```python
# Wrap Method: 기존 메서드를 감싸서 로깅 추가
class Employee:
    def pay(self) -> None:
        self._log_payment()       # 새 동작 (전)
        self._dispatch_pay()      # 기존 로직 (이름 변경)
        self._update_records()    # 새 동작 (후)

    def _dispatch_pay(self) -> None:
        # 원래 pay()의 로직 (이름만 변경)
        ...

    def _log_payment(self) -> None:
        """급여 지급 로깅 (새 메서드 -- 테스트 가능)"""
        ...

    def _update_records(self) -> None:
        """급여 기록 업데이트 (새 메서드 -- 테스트 가능)"""
        ...
```

### 16.5 특성화 테스트 (Characterization Tests) [WELC]

레거시 구현을 이해하기 위해 “올바른 동작”이 아니라 **현재 동작을 포착**하는 임시 probe다. 현재 구현은 계약의 증거일 뿐 오라클이 아니므로, 특성화 결과를 영구 회귀 테스트나 구현 완료 증거로 곧바로 고정하지 않는다.

특성화 probe는 **non-migration 레거시 코드**에만 쓴다. migration 파일·과거 model state·forward/reverse를 관찰하는 임시 테스트는 “조사용”이라는 이름으로 migration 전용 테스트 금지를 우회하므로 작성하지 않는다. 현재 승인 계약을 확인한 뒤 probe를 계약 테스트로 다시 쓰거나 제거한다. 유지·갱신·분리·삭제 판정은 `discipline-tdd` §5.5가 소유한다.

```python
def test_legacy_calculate_tax():
    """계약 확인 전 레거시 동작을 조사하는 임시 probe."""
    assert legacy_calculate_tax(1000) == 103.5
    assert legacy_calculate_tax(0) == 0
    assert legacy_calculate_tax(-500) == -51.75  # 음수 입력에 대한 현재 동작

    # 계약 확인 뒤 현행 계약 테스트로 재작성하거나 제거한다
```

### 16.6 Sensing과 Separation [WELC]

- **Sensing (감지)**: 코드가 계산하는 값에 접근하여 시스템의 다른 부분에 미치는 영향을 파악
- **Separation (분리)**: 테스트를 위해 코드를 의존성에서 분리

레거시 코드에서 테스트가 어려운 주요 원인은 **얽힌 의존성** 때문이다. Seam을 찾아 의존성을 끊고, 감지와 분리를 통해 테스트 가능한 코드로 전환한다.

---

## 17. 설계 철학과 프로세스

### 17.1 설계 단계에서 두 번 설계하고, 구현 단계에서 빠르게 다듬어라 [APoSD] [CC] [OO]

> **통합 원칙**: 주요 아키텍처/인터페이스 결정은 최소 두 가지 근본적으로 다른 접근법을 비교한다 **[APoSD]**. 세부 구현은 빠르게 작성한 후 테스트를 유지하며 반복적으로 리팩토링한다 **[CC] [OO]**.

**설계 단계 (Design It Twice)** [APoSD]:
- 모든 주요 설계 결정에 대해 최소 **두 가지 근본적으로 다른 접근법**을 고려하라
- 첫 번째 생각이 최선의 설계를 내놓을 가능성은 낮다
- 전술적 프로그래밍("일단 동작하면 된다")은 복잡성을 누적시키고 장기적으로 기능 추가 비용을 증가시킨다

**구현 단계 (빠르게 구현 후 리팩토링)** [CC] [OO]:
1. 처음에는 길고 복잡해도 좋다
2. 다듬고 또 다듬는다
3. 다듬는 와중에도 항상 단위 테스트는 통과한다

> "설계를 간단히 끝내고 최대한 빨리 구현에 돌입하라. 머릿속에 객체의 협력 구조가 번뜩인다면 그대로 코드를 구현하기 시작하라." **[OO]**

### 17.2 안정적인 구조 중심 설계 [OO]

기능을 중심으로 구조를 종속시키면 변경에 취약하다.
안정적인 구조(도메인 모델)를 중심으로 기능을 종속시켜야 한다.

> "도메인 모델이 안정적인 이유는 사용자가 도메인의 본질적인 측면을 가장 잘 이해하고 있기 때문이다." **[OO]**

### 17.3 책임 주도 설계 (RDD) [OO]

1. 시스템이 사용자에게 제공해야 하는 기능인 시스템 책임을 파악한다
2. 시스템 책임을 더 작은 책임으로 분할한다
3. 분할된 책임을 수행할 적절한 객체에 할당한다
4. 객체가 다른 객체의 도움이 필요하면 협력을 설계한다

### 17.4 세 가지 관점으로 클래스를 바라보라 [OO]

- **개념적 관점**: 도메인 안의 개념과 관계를 반영
- **명세 관점**: 객체가 협력을 위해 "무엇"을 할 수 있는가 (인터페이스)
- **구현 관점**: 객체의 책임을 "어떻게" 수행할 것인가

> "구현이 아니라 인터페이스에 대해 프로그래밍하라." -- GoF **[OO]**

### 17.5 YAGNI [PC]

유지보수 가능한 소프트웨어를 만드는 것은 미래의 요구사항을 예측하는 것이 아니다. 현재 요구사항을 잘 해결하고, 나중에 수정하기 쉽도록 작성하는 것이다.

### 17.6 패턴은 절대적 진리가 아니다 [IP]

> "패턴은 절대적인 진리가 아니므로 상황에 따라 패턴을 적절히 변화시켜 사용해야 한다." **[IP]**

특정 상황에서 특정 패턴을 왜 쓰는지를 알아야 한다. 원칙을 명확하게 알고 있다면 새로운 패턴을 만들 수도 있다.

### 17.7 깨진 창문 이론 [PP]

하나의 깨진 창문(나쁜 설계, 잘못된 결정, 나쁜 코드)을 방치하면, 전체 소프트웨어가 빠르게 퇴화한다. **발견 즉시 수리하라.** 시간이 없다면 최소한 "판자로 막아 놓으라" (TODO 주석, 예외 발생 등).

```python
# 깨진 창문: 방치된 나쁜 코드
def calc(d):
    x = d.get("v")
    if x:
        return x * 1.1
    return 0

# 수리된 창문
TAX_RATE = 0.1

def calculate_total_with_tax(order_data: dict) -> float:
    """주문 데이터에서 세금 포함 총액을 계산한다."""
    amount = order_data.get("amount")
    if amount is None:
        raise ValueError("Order data must contain 'amount'")
    return amount * (1 + TAX_RATE)
```

### 17.8 추적탄 (Tracer Bullets) [PP]

프로토타입과 달리, 추적탄 코드는 **최종 시스템의 골격**이 된다. 요구사항에서 시스템의 어떤 측면까지 빠르고 가시적이며 반복적으로 도달하는 것이 목표다.

| 추적탄 (Tracer Bullet) | 프로토타입 (Prototype) |
|------------------------|----------------------|
| 최종 시스템의 일부가 된다 | 작성 후 버린다 |
| 가볍지만 완전하다 | 특정 측면만 탐구한다 |
| 실제 환경에서 동작한다 | 격리된 실험이다 |
| 점진적으로 살을 붙인다 | 정찰/정보 수집 역할 |

### 17.9 기타 핵심 팁 [PP]

| 팁 | 설명 |
|----|------|
| ETC (Easier to Change) | 좋은 설계의 핵심 가치 -- 변경하기 쉬운 코드 |
| 작은 걸음으로 (Take Small Steps) | 항상 작은 단위로 변경하고 확인하라 |
| 일찍 리팩토링하고 자주 리팩토링하라 | 문제를 발견하면 즉시 개선 |
| 최소 결합의 법칙 | 물어보지 말고 말하라 (Tell, Don't Ask) |
| 우연에 의한 프로그래밍을 피하라 | 코드가 왜 동작하는지 항상 이해하라 |

---

## 18. Python 관용구와 스타일

Python 언어 특화 관례와 패턴은 `workspace/reference/implementation-python/reference/final.md`를 참조한다.

---

## 핵심 요약 체크리스트

| 범주 | 원칙 | 출처 |
|------|------|------|
| 이름 | 의도를 드러내는 이름을 사용하라 | [CC] [IP] |
| 이름 | 한 개념에 한 단어, 말장난 금지 | [CC] |
| 이름 | 클래스는 명사, 메서드는 동사 | [CC] [IP] |
| 이름 | 이름 길이는 범위에 비례, 평균 10-16자 참고 | [CC] [CodeC] |
| 이름 | 핵심 개념을 앞에, 한정자를 뒤에 | [CodeC] |
| 함수 | 함수는 작게, 모듈/클래스는 깊게 | [CC] [APoSD] |
| 함수 | 한 가지만 해라, 추상화 수준 통일 | [CC] [IP] |
| 함수 | 인수 최소화, 플래그 인수 금지 | [CC] |
| 함수 | 명령/조회 분리, 부수 효과 금지 | [CC] |
| 주석 | 인터페이스 주석은 필수, 구현 주석은 최소화 | [APoSD] [CC] |
| 객체 | 행동이 상태를 결정한다 | [OO] |
| 객체 | 캡슐화: what은 공개, how는 은닉 | [OO] [IP] |
| 객체 | 인터페이스에 맞춰 코딩하라 | [OO] [IP] |
| 객체 | 묻지 말고 시켜라 (Tell, Don't Ask) | [OO] |
| SOLID | 단일 책임, 개방/폐쇄, 리스코프 치환 | [PC] [CC] |
| SOLID | 인터페이스 분리, 의존성 역전 | [PC] |
| 설계 | DRY는 지식 단위로 판단 | [PP] |
| 설계 | 로직과 데이터를 함께 유지 | [IP] |
| 설계 | 변화율에 따라 분리 | [IP] |
| 설계 | 안정적 구조 중심, 책임 주도 설계 | [OO] |
| 설계 | 깊은 모듈, 정보 은닉 | [APoSD] |
| 오류 | 1순위: 설계로 오류 제거, 2순위: 예외 사용 | [APoSD] [CC] |
| 오류 | Try/Catch 분리, 보호절 활용, DbC | [CC] [IP] [PC] |
| 오류 | 방어적 프로그래밍 (assertion vs 오류 처리) | [CodeC] |
| 프로세스 | 설계 단계: 두 번 설계, 구현 단계: 빠르게 다듬기 | [APoSD] [CC] [OO] |
| 프로세스 | YAGNI: 현재에 집중하라 | [PC] |
| 프로세스 | 깨진 창문 즉시 수리 | [PP] |
| 리팩토링 | 코드 스멜 감지 및 기법 적용 | [Ref] |
| 레거시 | Seam, Sprout, Wrap, 특성화 테스트 | [WELC] |
