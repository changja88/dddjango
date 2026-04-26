# TDD vs Test-Last 분석: TokenManager

## 판정: Test-Last일 가능성이 높다 (확신도: ~75%)

이 코드에는 TDD로 작성되었다는 구조적 근거가 부족하고, test-last에서 나타나는 패턴이 여럿 관찰된다. 다만 코드만으로 작성 순서를 100% 확정할 수는 없으므로, 근거별로 확신도와 불확실성을 함께 서술한다.

---

## TDD 근거가 부족한 점 (test-last 신호)

### 1. 완성된 클래스가 통째로 존재한다

[Red-Green-Refactor Cycle] -- TDD에서는 테스트 하나를 작성하고, 그 테스트만 통과시키는 최소한의 코드를 작성한 뒤, 리팩토링한다. 이 사이클을 반복하면 프로덕션 코드가 점진적으로 성장한다.

그러나 `TokenManager` 클래스는 `create_token`, `validate`, `revoke`, `active_count` 네 개의 메서드가 완전한 형태로 한꺼번에 존재한다. TDD로 작성했다면 첫 번째 테스트(`test_create_returns_32char_hex`)에 대해 `create_token`만 존재하고, `validate`는 다음 테스트가 요구할 때 비로소 등장하는 것이 자연스럽다. 물론 최종 결과물에서는 TDD든 test-last든 동일한 코드가 나올 수 있으므로, 이 신호만으로 확정할 수는 없다.

**확신도**: 중간. 최종 결과물만으로는 중간 과정을 확인할 수 없다는 한계가 있다.

### 2. 점진적 일반화(incremental generalization)의 흔적이 없다

[Green Bar Patterns: Fake It, Triangulation] -- TDD에서는 Fake It(상수 반환 후 일반화), Triangulation(두 예제로 추상화 강제) 등의 전략을 사용하여 점진적으로 구현한다.

`create_token`의 구현을 보면, 첫 번째 테스트가 "32자 hex 문자열 반환"을 검증한다. TDD라면 이 테스트를 통과시키기 위해 처음에는 `return "a" * 32`처럼 가짜 구현을 했을 수 있다. 그러나 현재 코드에는 hashlib, datetime, 딕셔너리 저장 등이 한꺼번에 포함되어 있다. 이는 "첫 테스트를 통과시키기 위한 최소한의 코드"보다 훨씬 많은 구현이다.

특히 `_tokens` 딕셔너리에 `user_id`, `created_at`, `expires_at`를 모두 저장하는 구조는 `validate`와 `active_count`의 요구사항까지 미리 알고 설계한 것이다. TDD라면 `validate` 테스트를 작성하는 시점에 비로소 이 저장 구조가 필요해진다.

**확신도**: 높음. 이 패턴은 전체 설계를 먼저 하고 구현한 뒤에 테스트를 붙인 test-last의 전형적 특징이다.

### 3. 테스트가 프로덕션 코드의 기능을 "확인"하는 구조이다

[TDD Philosophy: 테스트가 설계를 주도한다] -- TDD에서 테스트는 "어떤 행위가 필요한가"를 먼저 정의하는 도구다. 따라서 테스트가 설계를 주도하면, 테스트 이름과 구조가 사용자 관점의 행위를 서술하게 된다.

이 코드의 테스트 목록을 보면:
- `test_create_returns_32char_hex` -- 구현 세부사항(32자, hex) 확인
- `test_validate_returns_user_id` -- 메서드 반환값 확인
- `test_validate_unknown_token` -- 메서드 반환값 확인
- `test_revoke_existing_token` -- 메서드 반환값 확인
- `test_revoke_nonexistent` -- 메서드 반환값 확인
- `test_active_count` -- 메서드 반환값 확인
- `test_expired_token_returns_none` -- 메서드 반환값 확인
- `test_different_users_get_different_tokens` -- 속성 확인
- `test_custom_ttl` -- 속성 확인

테스트가 메서드 단위로 1:1 대응하며, 각 메서드의 반환값을 사후적으로 확인하는 패턴이다. TDD에서 테스트가 설계를 주도했다면, "토큰을 발급받은 사용자는 해당 토큰으로 인증할 수 있다"처럼 행위 중심의 시나리오가 먼저 등장하고, 그 시나리오를 통과시키면서 `create_token`과 `validate`가 함께 태어나는 것이 자연스럽다.

**확신도**: 중간-높음. 메서드별 테스트 매핑은 test-last의 강한 신호이지만, TDD에서도 단순한 구조에서는 이런 패턴이 나올 수 있다.

### 4. 시작 테스트(Starter Test)가 가장 단순한 경우가 아니다

[Red Bar Patterns: 시작 테스트] -- TDD에서 첫 테스트는 "오퍼레이션이 아무 일도 하지 않는 경우"부터 시작한다. 가장 단순한 경우에서 시작하여 아는 것에서 모르는 것으로 방향을 잡는다.

첫 테스트가 `test_create_returns_32char_hex`인데, 이것은 이미 hashlib SHA-256의 출력 형식을 알고 있어야 성립하는 테스트다. TDD로 토큰 관리자를 처음 만든다면, "토큰 매니저를 생성할 수 있다" 또는 "빈 매니저에는 활성 토큰이 0개다" 같은 가장 단순한 경우가 먼저 올 가능성이 높다.

**확신도**: 중간. 숙련된 개발자가 구현에 확신이 있으면 Obvious Implementation 전략으로 바로 이런 테스트를 쓸 수도 있다.

### 5. 테스트 간 학습 곡선(progression)이 보이지 않는다

[Red Bar Patterns: 한 단계 테스트] -- TDD에서는 각 테스트가 "새로운 무언가를 가르쳐 줄 수 있으며, 구현할 수 있다는 확신이 드는 테스트"를 선택한다. 아는 것에서 모르는 것으로 이동한다.

테스트 목록의 순서를 보면 `create` -> `validate` -> `validate(unknown)` -> `revoke` -> `revoke(nonexistent)` -> `active_count` -> `expired` -> `different_users` -> `custom_ttl`이다. 이 순서는 메서드를 하나씩 훑어가는 API 문서 순서에 가깝다. TDD에서 자연스러운 순서라면, 핵심 시나리오(`create` + `validate` 통합)를 먼저 다루고, 경계 사례(expired, unknown)로 확장하며, 부가 기능(`revoke`, `active_count`)이 나중에 등장하는 흐름이 더 자연스럽다.

**확신도**: 중간. 테스트 순서는 나중에 재배치할 수 있으므로, 작성 순서와 최종 순서가 다를 수 있다.

---

## TDD일 수 있는 근거 (반대 방향)

완전히 공정하게 판단하기 위해, TDD의 가능성을 지지하는 점도 기록한다.

### 좋은 점 1: 테스트 격리가 양호하다

[Testing Patterns: 테스트 격리] -- 모든 테스트가 독립적으로 `TokenManager`를 새로 생성한다. 공유 상태가 없어 Erratic Test 냄새가 없다. TDD에서 자연스럽게 나오는 습관이지만, 테스트 작성 경험이 있는 개발자라면 test-last에서도 이렇게 한다.

### 좋은 점 2: 경계 사례가 포함되어 있다

`test_expired_token_returns_none`, `test_validate_unknown_token`, `test_revoke_nonexistent` 등 경계 사례를 다루고 있다. TDD에서 테스트 목록을 사전에 작성하고 하나씩 구현하면 자연스럽게 포함되지만, 꼼꼼한 test-last에서도 동일하게 나타난다.

### 좋은 점 3: Mock이 없는 순수 상태 기반 테스트

[Four Pillars / Test Styles] -- 모든 테스트가 출력 기반 또는 상태 기반이며, Mock을 사용하지 않는다. 이는 고전 학파 TDD의 특성과 부합하며, 리팩토링 내성이 높다.

---

## 리뷰 체크리스트 점검

| 항목 | 판정 |
|------|------|
| Tests written after production code | **의심됨** -- 위 근거 #1~#5에 해당 |
| No Red-Green-Refactor cycle evidence | **해당** -- 완성된 프로덕션 코드, 점진적 성장 흔적 없음 |
| Tests coupled to implementation details | **경미** -- `test_create_returns_32char_hex`가 SHA-256의 구체적 출력 형식에 결합 |
| Mock overuse for internal collaborators | **해당 없음** -- Mock 미사용 |
| Missing test isolation | **해당 없음** -- 격리 양호 |
| Test smells | **경미** -- `test_expired_token_returns_none`에서 `time.sleep(0.01)` 사용은 Slow Test/Erratic Test의 잠재적 냄새. 만료 시간 비교가 타이밍에 의존한다 |
| No incremental development | **해당** -- 전체 클래스가 big-bang으로 구현된 것으로 보임 |
| Communication-based testing where output-based would suffice | **해당 없음** |
| Missing boundary/edge case tests | **경미** -- 동일 user_id로 중복 토큰 생성, 만료 후 active_count 감소, secret이 다르면 다른 토큰 생성 등이 빠져 있다 |
| Tests that don't drive design | **해당** -- 테스트가 기존 설계를 확인하는 구조 |

---

## 결론

**이 코드는 test-last로 작성되었을 가능성이 높다.** 주요 근거는 세 가지다:

1. `create_token`의 첫 테스트만 통과시키기에 필요한 것보다 훨씬 많은 구현(딕셔너리 저장, 만료 시간 설정)이 이미 포함되어 있다. 이는 전체 설계를 먼저 하고 구현한 뒤에 테스트를 붙인 패턴이다.
2. 테스트가 메서드와 1:1로 대응하며 반환값을 확인하는 구조로, 설계를 주도하는 테스트가 아니라 기존 API를 사후 검증하는 테스트다.
3. 점진적 일반화(Fake It, Triangulation)의 흔적이 전혀 없고, 모든 메서드가 완전한 형태로 존재한다.

**불확실성 표현**: 코드의 최종 상태만으로는 작성 과정을 완벽히 복원할 수 없다. 숙련된 TDD 개발자가 Obvious Implementation 전략을 적극 사용하고, 마지막에 코드를 정리하면 비슷한 결과물이 나올 수 있다. 그러나 그 경우에도 테스트 순서가 행위 시나리오 중심으로 배열되고, 첫 테스트가 더 단순한 경우에서 시작하는 것이 일반적이다. 이 코드에서는 그런 흔적이 관찰되지 않는다.
