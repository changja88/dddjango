# 테스트 코드 리뷰: PasswordValidator

## 진단 요약

라인 커버리지 100%임에도 버그가 발생하는 이유는 **테스트가 "모든 코드 라인을 실행하는 것"에만 집중하고, 실제 동작의 정확성을 검증하지 않기 때문**이다. 아래에서 구체적인 문제점을 분류하여 설명한다.

---

## 1. 약한 단언(Weak Assertions) -- 가장 핵심적인 문제

대부분의 실패 케이스 테스트가 `assert valid is False`만 확인하고, **어떤 에러가 반환되었는지 검증하지 않는다**.

```python
# 현재 코드 -- "실패했다"만 확인
def test_too_short():
    v = PasswordValidator()
    valid, errors = v.validate('Ab1!')
    assert valid is False
    # errors의 내용을 전혀 검증하지 않음

# 개선 -- 정확한 에러 메시지와 에러 개수까지 검증
def test_too_short():
    v = PasswordValidator()
    valid, errors = v.validate('Ab1!')
    assert valid is False
    assert '최소 8자 이상이어야 합니다' in errors
    assert len(errors) == 1  # 길이만 짧고, 나머지 조건은 충족하는지 확인
```

**이 문제가 버그를 놓치는 이유**: `validate`가 잘못된 에러 메시지를 반환하거나, 에러 목록이 불완전하거나, 엉뚱한 에러를 포함해도 테스트는 통과한다. 호출하는 쪽에서 에러 메시지를 사용자에게 보여주거나 분기 처리에 쓴다면 실제 버그로 이어진다.

**해당 테스트 목록**: `test_too_short`, `test_no_uppercase`, `test_no_lowercase`, `test_no_digit`, `test_no_special`

---

## 2. 경계값(Boundary) 테스트 부재

### 2-1. min_length 경계

```python
# 현재: 명확히 짧은 값(4자)과 명확히 긴 값(8자)만 테스트
# 누락: 정확히 경계인 7자, 8자를 테스트하지 않음

def test_length_boundary_just_below():
    v = PasswordValidator()  # min_length=8
    valid, errors = v.validate('Abcde1!')  # 7자 -- 실패해야 함
    assert valid is False
    assert '최소 8자 이상이어야 합니다' in errors

def test_length_boundary_exact():
    v = PasswordValidator()
    valid, errors = v.validate('Abcdef1!')  # 정확히 8자 -- 통과해야 함
    assert valid is True
```

### 2-2. strength 점수 경계

`strength` 메서드의 점수 계산에서 `score >= 2`가 기준인데, score가 정확히 1인 경우(medium)와 정확히 2인 경우(strong)의 경계를 명시적으로 테스트하지 않는다.

```python
# score=1 (12자 이상이지만 16자 미만, 특수문자 1개) -> medium
def test_strength_score_exactly_1():
    v = PasswordValidator()
    result = v.strength('Abcdefghij1!')  # 12자, 특수문자 1개 -> score=1
    assert result == 'medium'

# score=2 (16자 이상, 특수문자 1개) -> strong
def test_strength_score_exactly_2():
    v = PasswordValidator()
    result = v.strength('Abcdefghijklmn1!')  # 16자, 특수문자 1개 -> score=2
    assert result == 'strong'
```

---

## 3. 조합(Combination) 테스트 부재

각 검증 규칙을 하나씩만 위반하는 테스트만 존재한다. **여러 규칙을 동시에 위반하는 경우**를 테스트하지 않는다.

```python
# 여러 조건 동시 위반 시 모든 에러가 올바르게 반환되는지 검증
def test_multiple_violations():
    v = PasswordValidator()
    valid, errors = v.validate('abc')  # 짧고, 대문자 없고, 숫자 없고, 특수문자 없음
    assert valid is False
    assert len(errors) == 4
    assert '최소 8자 이상이어야 합니다' in errors
    assert '대문자를 포함해야 합니다' in errors
    assert '숫자를 포함해야 합니다' in errors
    assert '특수문자(!@#$%^&*)를 포함해야 합니다' in errors
```

이것이 없으면 에러 목록 조합 과정에서 발생하는 버그(예: 조기 리턴, 에러 덮어쓰기)를 잡을 수 없다.

---

## 4. 엣지 케이스 테스트 부재

### 4-1. 빈 문자열

```python
def test_empty_password():
    v = PasswordValidator()
    valid, errors = v.validate('')
    assert valid is False
    # 빈 문자열은 모든 조건을 위반해야 함
    assert len(errors) == 5
```

### 4-2. 특수문자 목록 외의 특수문자

현재 구현은 `!@#$%^&*`만 특수문자로 인정한다. 사용자가 `-`, `_`, `(`, `)` 등을 특수문자로 기대하면 버그로 이어진다.

```python
def test_special_char_not_in_allowed_set():
    v = PasswordValidator()
    valid, errors = v.validate('Abcdefg1-')  # '-'는 특수문자로 인정 안 됨
    assert valid is False
    assert '특수문자(!@#$%^&*)를 포함해야 합니다' in errors
```

### 4-3. 아주 긴 비밀번호

```python
def test_very_long_password():
    v = PasswordValidator()
    long_pw = 'A' * 500 + 'a' * 500 + '1!@'
    valid, errors = v.validate(long_pw)
    assert valid is True
    assert v.strength(long_pw) == 'strong'
```

---

## 5. strength 메서드의 로직 검증 부족

`test_strength_strong`에서 사용한 입력값 `'Abcdefghijklmn1!@'`은 18자이고 특수문자 2개로, score가 3이다 (12자 이상 +1, 16자 이상 +1, 특수문자 2개 이상 +1). 이는 기준(score >= 2)을 크게 초과하는 값이라 경계 근처의 버그를 놓친다.

**strength 점수 조합별 체계적 테스트가 필요하다**:

| 길이 | 특수문자 수 | score | 기대 결과 |
|------|------------|-------|-----------|
| 8    | 1          | 0     | medium    |
| 12   | 1          | 1     | medium    |
| 16   | 1          | 2     | strong    |
| 8    | 2          | 1     | medium    |
| 12   | 2          | 2     | strong   |
| 16   | 2          | 3     | strong    |

---

## 6. require_special=False 경로 테스트 부족

`test_special_not_required`는 특수문자 없이 통과하는 것만 확인한다. 하지만 `require_special=False`일 때 **strength 계산에서 특수문자 개수가 여전히 점수에 반영되는지** 테스트하지 않는다. 이는 의도된 동작인지 버그인지 불분명하며, 테스트로 명시해야 한다.

```python
def test_strength_with_special_not_required():
    v = PasswordValidator(require_special=False)
    # 특수문자 없이도 valid이지만, strength에서 특수문자 보너스는 없어야 하는가?
    result = v.strength('Abcdefghijklmn1')  # 15자, 특수문자 0개
    assert result == 'medium'  # score=1 (12자 이상만 해당)
```

---

## 7. 프로덕션 코드의 잠재적 설계 문제

테스트와 별개로, 프로덕션 코드에도 주의할 점이 있다:

- **특수문자 목록이 하드코딩**: `validate`와 `strength` 모두에서 `'!@#$%^&*'`가 중복되어 있다. 한쪽만 수정하면 불일치가 발생한다. 상수로 추출해야 한다.
- **strength가 validate에 의존**: `strength` 메서드가 내부적으로 `validate`를 호출한다. validate의 동작이 바뀌면 strength의 결과도 변한다. 이 의존성을 테스트에서 명시적으로 다루지 않고 있다.

---

## 핵심 정리

| 문제 유형 | 영향도 | 설명 |
|-----------|--------|------|
| 약한 단언 | **높음** | 에러 내용을 검증하지 않아 잘못된 에러 반환 버그를 놓침 |
| 경계값 미테스트 | **높음** | off-by-one 류 버그를 잡을 수 없음 |
| 조합 미테스트 | **중간** | 다중 위반 시 에러 누락 버그를 놓침 |
| 엣지 케이스 미테스트 | **중간** | 빈 문자열, 허용 외 특수문자 등 실사용 시나리오 미검증 |
| strength 경계 미테스트 | **높음** | score 계산 경계에서 medium/strong 오분류 버그를 놓침 |

**결론**: 라인 커버리지 100%는 "모든 코드 줄이 한 번은 실행되었다"는 의미일 뿐, "모든 동작이 올바르다"를 보장하지 않는다. 이 테스트 스위트의 근본 문제는 (1) 단언이 너무 약하고 (2) 입력값의 다양성이 부족하다는 것이다. 커버리지 지표만으로는 테스트 품질을 판단할 수 없으며, **경계값, 조합, 에러 메시지 정확성**에 대한 검증이 반드시 필요하다.
