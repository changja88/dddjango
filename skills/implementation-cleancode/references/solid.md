# SOLID 원칙 레퍼런스

SRP, OCP, LSP, ISP, DIP 다섯 가지 객체지향 설계 원칙의 규칙과 예시를 다룬다.

---

### 3.1 단일 책임 원칙 (SRP) [PC] [CC]

클래스는 하나의 책임만 가져야 하며, 변경 이유도 단 하나여야 한다.

```python
# bad — 세 가지 독립적 책임
class SystemMonitor:
    def load_activity(self): ...
    def identify_events(self): ...
    def stream_events(self): ...

# good
class ActivityLoader: ...
class EventIdentifier: ...
class EventStreamer: ...
```

### 3.2 개방/폐쇄 원칙 (OCP) [PC] [CC]

확장에는 개방되고 수정에는 폐쇄되어야 한다.

```python
# bad — 새 이벤트마다 이 메서드를 수정해야 한다
class SystemMonitor:
    def identify_event(self):
        if self.event_data["before"]["session"] == 0 and \
           self.event_data["after"]["session"] == 1:
            return LoginEvent(self.event_data)

# good — 새 Event 서브클래스를 추가하면 SystemMonitor 수정 불필요
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

### 3.3 리스코프 치환 원칙 (LSP) [PC] [OO]

하위 클래스는 부모 클래스를 대체할 수 있어야 한다.

```python
# bad — 파라미터 타입 변경
class LoginEvent(Event):
    def meets_condition(self, event_data: list) -> bool: ...  # LSP 위반

# good — 부모와 동일한 서명 유지
class LoginEvent(Event):
    def meets_condition(self, event_data: dict) -> bool:
        return event_data.get("after", {}).get("session") == 1
```

### 3.4 인터페이스 분리 원칙 (ISP) [PC]

클라이언트가 필요하지 않은 메서드를 구현하도록 강제하지 마라.

```python
# bad — 뚱뚱한 인터페이스
class EventParser:
    def from_xml(self): ...
    def from_json(self): ...

# good — 분리된 인터페이스
class XMLEventParser:
    def from_xml(self): ...

class JSONEventParser:
    def from_json(self): ...
```

### 3.5 의존성 역전 원칙 (DIP) [PC]

구체적 구현이 아닌 추상화에 의존하라. 세부 사항은 추상화에 의존해야 한다.

```python
# bad
class EventStreamer:
    def __init__(self):
        self._target = Syslog()  # 구체 클래스에 직접 의존

# good
class EventStreamer:
    def __init__(self, target: DataTargetClient):
        self._target = target

    def stream(self, events):
        for event in events:
            self._target.send(event.serialize())
```
