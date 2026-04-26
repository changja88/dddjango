# 추상화와 캡슐화 레퍼런스

인터페이스 설계, 정보 은닉, 캡슐화와 관련된 규칙과 예시를 다룬다.

---

### 1.1 추상화의 두 가지 방법 [OO]

- **일반화** -- 공통점을 취하고 차이점을 버린다
- **단순화** -- 불필요한 세부 사항을 제거한다

### 1.2 구현이 아니라 인터페이스에 맞춰 코딩하라 [IP] [OO]

설계상의 결정을 필요 이상으로 노출하지 마라.

```python
# bad — 구체적 구현에 의존
class ReportGenerator:
    def generate(self, data: list):
        mysql_conn = MySQLConnection()
        mysql_conn.save(data)

# good — 추상화에 의존
class ReportGenerator:
    def __init__(self, storage: StorageInterface):
        self._storage = storage

    def generate(self, data: list):
        self._storage.save(data)
```

### 1.3 상태를 캡슐화하라 [OO]

객체의 자율성은 내부와 외부를 명확하게 구분하는 것으로부터 나온다.
외부 코드는 객체가 무엇(what)을 수행하는지 알 수 있지만 어떻게(how) 수행하는지는 알 수 없어야 한다.

```python
# bad — 외부에서 직접 수정 가능
class BankAccount:
    def __init__(self):
        self.balance = 0

account.balance = -1000  # 불변식 위반

# good
class BankAccount:
    def __init__(self):
        self._balance = 0

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Amount must be positive")
        self._balance += amount

    def get_balance(self) -> float:
        return self._balance
```

### 1.4 정보 은닉 (Information Hiding) [APoSD]

깊은 모듈을 달성하는 가장 중요한 기법이다. 설계 결정과 내부 정보를
인터페이스 뒤에 캡슐화하여 외부에 노출하지 않는다.

```python
# bad — 정보 누출: 두 모듈이 같은 파일 형식 지식을 공유
class CSVReader:
    def read(self, path):
        with open(path) as f:
            return [line.strip().split(",") for line in f]

class CSVWriter:
    def write(self, path, rows):
        with open(path, "w") as f:
            for row in rows:
                f.write(",".join(row) + "\n")

# good — 형식 지식을 한 모듈에 집중
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
