# DDD와 아키텍처

> **[의사결정 #5] Internal 채택**: 계층+DIP 기반 동기적 흐름을 기본으로 한다 (메시지 주도는 별도 고급 주제로 다룸).

## 5.1 계층 아키텍처

> 출처: [A][C]

```
표현(Presentation) -> 응용(Application) -> 도메인(Domain) -> 인프라(Infrastructure)
```

**핵심 규칙:**
- 상위 계층에서 하위 계층으로만 의존한다 (하위 -> 상위 절대 불가)
- 도메인 영역, 응용 영역, 표현 영역은 인프라의 구현 기술을 직접 사용하지 않는다
- DIP를 적용하여 도메인 영역에 정의한 인터페이스를 인프라에서 구현한다

## 5.2 DIP (의존성 역전 원칙)

> 출처: [A][C]

고수준 모듈이 저수준 모듈에 의존하지 않도록 추상화에 의존한다. 인터페이스는 고수준(도메인) 영역에 위치해야 한다.

```python
from abc import ABC, abstractmethod


# 도메인 영역 (고수준): 인터페이스 정의
class RuleDiscounter(ABC):
    """할인 규칙 인터페이스 - 도메인(고수준)에 위치"""

    @abstractmethod
    def apply_rules(
        self, customer_id: str, order_lines: List[OrderLineItem]
    ) -> Money:
        ...


# 인프라 영역 (저수준): 구현체
class DroolsRuleDiscounter(RuleDiscounter):
    """Drools 엔진 기반 구현 - 인프라(저수준)에 위치"""

    def apply_rules(
        self, customer_id: str, order_lines: List[OrderLineItem]
    ) -> Money:
        ...


# 응용 서비스: 추상화에만 의존
class CalculateDiscountService:
    """DIP 적용 예시
    - RuleDiscounter 인터페이스에만 의존
    - Drools든 Simple이든 상관없이 동작
    - 테스트 시 Mock 객체 주입 가능
    """

    def __init__(self, rule_discounter: RuleDiscounter):
        self._rule_discounter = rule_discounter

    def calculate_discount(
        self, order_lines: List[OrderLineItem], customer_id: str
    ) -> Money:
        return self._rule_discounter.apply_rules(customer_id, order_lines)
```

## 5.3 핵사고날 아키텍처 (포트와 어댑터)

> 출처: [C]

[C]는 헥사고날 아키텍처를 DDD 구현의 주요 아키텍처 스타일로 권장한다. 포트와 어댑터의 상세한 설명과 구현은 **architecture-implementation-patterns** 스킬을 참조한다.

## 5.4 CQRS (커맨드-쿼리 책임 분리)

> 출처: [C], Greg Young, Martin Fowler
> **[의사결정 #2] External 채택**: CQRS는 보조 패턴으로 선택적 적용한다.

> "CQRS는 최상위 아키텍처가 아니다! 보조 패턴으로 취급하고, 선택적으로 일부 바운디드 컨텍스트에만 적용하라." -- Greg Young (CQRS 창시자)

커맨드(상태 변경)와 쿼리(데이터 조회)의 모델을 분리한다. 핵심 원칙: "질문하는 행동이 대답을 바꿔서는 안 된다." 시스템 전체가 아닌 필요한 컨텍스트에만 선택 적용하는 것이 안전하다.

CQRS의 상세 구현과 아키텍처 패턴은 **architecture-implementation-patterns** 스킬을 참조한다.

## 5.5 대규모 구조 (Large-Scale Structure)

> 출처: Evans 파란책 Chapter 16

시스템 전체에 적용되는 고수준 조직 패턴이다.

| 패턴 | 설명 |
|------|------|
| 진화하는 질서 (Evolving Order) | 대규모 구조를 처음부터 완벽히 설계하지 말고, 시스템과 함께 진화시켜라 |
| 시스템 은유 (System Metaphor) | 시스템 전체를 관통하는 비유를 찾아 명시화하라 |
| 책임 계층 (Responsibility Layers) | 도메인 모델을 의미 있는 책임 계층으로 구조화하라 |
| 지식 수준 (Knowledge Level) | 운영 수준의 핵심 동작을 구성할 수 있는 메타 수준을 분리하라 |
| 플러그형 컴포넌트 프레임워크 | 핵심 추상화와 구현을 플러그인 구조로 분리하라 |

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# === 지식 수준 (Knowledge Level) 패턴 ===

class FieldType(Enum):
    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    CHOICE = "choice"


@dataclass(frozen=True)
class FieldDefinition:
    """지식 수준(Knowledge Level): 필드의 구조를 정의하는 메타 객체"""
    name: str
    field_type: FieldType
    required: bool = True
    choices: tuple[str, ...] = ()


@dataclass(frozen=True)
class FormTemplate:
    """지식 수준: 양식의 구조를 정의"""
    template_name: str
    field_definitions: tuple[FieldDefinition, ...]


@dataclass
class FormInstance:
    """운영 수준(Operational Level): 실제 사용자가 작성하는 양식 인스턴스"""
    template: FormTemplate
    values: dict[str, Any] = field(default_factory=dict)

    def set_field(self, field_name: str, value: Any) -> None:
        """지식 수준의 정의에 따라 운영 수준의 동작이 제어된다"""
        definition = self._find_definition(field_name)
        if definition is None:
            raise ValueError(f"템플릿에 '{field_name}' 필드가 없습니다")
        if definition.field_type == FieldType.CHOICE and value not in definition.choices:
            raise ValueError(f"허용된 선택지가 아닙니다: {definition.choices}")
        self.values[field_name] = value

    def _find_definition(self, name: str) -> FieldDefinition | None:
        return next(
            (d for d in self.template.field_definitions if d.name == name), None
        )
```
