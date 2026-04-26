# TDD와 AI 코딩 레퍼런스

TDD를 AI 코딩 도구와 결합하는 방법론과 TDAID 워크플로우를 정리한다.

---

## TDD as Prompt Engineering

> "TDD는 프롬프트 엔지니어링이다. 테스트가 AI에게 '무엇을' 만들고 '언제 완료인지'를 알려준다."

TDD의 Red-Green-Refactor 사이클은 AI 코딩 도구와 자연스럽게 결합된다.

```
전통 TDD:     개발자가 테스트 작성 -> 개발자가 구현
AI 보조 TDD:  개발자가 테스트 작성 -> AI가 구현 제안 -> 개발자가 검증
TDAID:        Plan -> Red -> Green(AI) -> Refactor(AI+개발자) -> Validate
```

---

## AI 보조 TDD 워크플로우

```python
# 1단계: 개발자가 명세로서의 테스트를 작성한다 (Red)
def test_parse_korean_date():
    """한국어 날짜 문자열을 파싱한다."""
    assert parse_date("2026년 4월 4일") == date(2026, 4, 4)
    assert parse_date("2026년 12월 25일") == date(2026, 12, 25)


def test_parse_korean_date_edge_cases():
    """엣지케이스를 포함한다."""
    with pytest.raises(ValueError):
        parse_date("잘못된 날짜")
    with pytest.raises(ValueError):
        parse_date("2026년 13월 1일")  # 13월은 없다

# 2단계: AI에게 구현을 요청한다 (Green)
# "위 테스트를 통과하는 parse_date 함수를 구현해줘"
# -> AI가 구현 제안

# 3단계: 개발자가 AI 구현을 검증하고 리팩토링한다 (Refactor)
# - 테스트가 통과하는가?
# - 코드가 의도대로인가?
# - 보안 문제나 환각(hallucination)이 없는가?
```

---

## TDD가 AI 코딩에서 더 중요한 이유

| 위험 | TDD의 방어 효과 |
|------|---------------|
| AI 환각 (hallucinated code) | 실패하는 테스트가 잘못된 구현을 즉시 감지 |
| 의도와 다른 구현 | 테스트가 명세 역할을 하여 의도를 명시 |
| 보안 취약점 | 보안 테스트가 AI 생성 코드의 취약점 포착 |
| 과도한 신뢰 | Red-Green 사이클이 점진적 검증을 강제 |

---

## Test-Driven AI Development (TDAID) 5단계

```
1. Plan     : 기능 요구사항을 테스트 목록으로 변환
2. Red      : 실패하는 테스트 작성 (개발자)
3. Green    : 테스트를 통과하는 구현 (AI 보조)
4. Refactor : 코드 품질 개선 (AI + 개발자 협업)
5. Validate : AI 생성 코드의 정확성, 보안, 성능 최종 검증
```

---

> 출처: 테스트주도 개발 §17

---

## 부록: TDD와 BDD의 관계

BDD는 TDD의 **진화형**이다. TDD가 개발자 중심의 코드 정확성에 집중한다면, BDD는 비즈니스 요구사항을 자연어로 표현하여 이해관계자와의 소통을 중시한다.

```
TDD 진화 경로:
TDD (코드 정확성) -> ATDD (인수 테스트) -> BDD (행위 명세 + 소통)
```

| 구분 | TDD | BDD |
|------|-----|-----|
| 관점 | 개발자 중심 | 사용자/비즈니스 중심 |
| 명세 언어 | 프로그래밍 언어 | 자연어 (Gherkin) |
| 테스트 단위 | 함수/클래스 | 시나리오/행위 |
| 산출물 | 단위 테스트 | 살아있는 문서(living documentation) |
| 참여자 | 개발자 | 개발자 + 기획자 + QA |

pytest-bdd 구현 상세는 **coding-test.md**를 참조한다.

> 출처: Cucumber, pytest-bdd §16.1
