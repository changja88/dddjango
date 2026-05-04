# TDD 핵심 철학 레퍼런스

TDD의 궁극적 목표, TDD를 해야 하는 이유, 피드백 간격 통제에 대한 핵심 철학을 정리한다.

---

## TDD의 목표

> 출처: Kent Beck, *테스트주도 개발*

TDD의 궁극적 목표는 **작동하는 깔끔한 코드(clean code that works)** 이다.

- 예측 가능한 개발 방법이다. 끊임없이 발생할 버그에 대해 걱정하지 않고, 일이 언제 마무리될지 알 수 있다
- 코드가 가르쳐주는 모든 교훈을 학습할 기회를 갖게 된다. 처음 생각나는 대로 후딱 완료해 버리면 더 나은 것에 대해 생각할 기회를 잃게 된다

---

## TDD를 해야 하는 이유: 용기

> 출처: Kent Beck, *테스트주도 개발*

TDD는 프로그래밍하면서 나타나는 **두려움을 관리하는 방법**이다.

- 두려움이란 "정말 어려운 문제라서 시작 단계인 지금은 어떻게 마무리될지 알 수 없군"하고 생각하는 합리적인 두려움을 말한다
- TDD란 프로그래밍 도중 내린 결정과 그 결정에 대한 피드백 사이의 간격을 인지하고, 이 간격을 통제할 수 있게 해주는 기술이다
- 단, 보안과 동시성은 TDD만으로 목표 달성을 기계적으로 보여주기 부족한 주제이다

---

## TDD의 한계와 적용 범위

TDD는 만능이 아니다. TDD 창시자 Kent Beck 자신이 "나는 테스트가 아니라 작동하는 코드에 대해 보수를 받는다"고 말했으며, Facebook 해커톤에서 코드의 절반만 TDD에 적합했다고 밝혔다.

| 상황 | TDD가 맞지 않는 이유 | 대안 | 출처 |
|------|---------------------|------|------|
| 탐색적/스파이크 작업 | 테스트할 사전 구조가 없음 | 시각적 검사, 빠른 피드백 루프 | Kent Beck |
| UI 프로토타이핑 | 테스트 피드백을 assertion으로 표현하기 어려움 | 탐색적 테스트, 시각적 리뷰 | Beck/Fowler |
| 비정형 데이터 파싱 | 출력이 미리 예측 불가 | 주입-검사-조정(inject-inspect-tweak) 사이클 | Kent Beck |
| 보안 테스트 | TDD가 보안 목표를 기계적으로 증명 불가 | 보안 감사, 침투 테스트 | Kent Beck |
| 동시성 | TDD만으로 동시성 정확성 보장 불가 | 형식 검증, 스트레스 테스트 | Kent Beck |
| 과도한 Mock 환경 | 과도한 모킹이 설계 명확성을 훼손 | 통합 테스트, 고전 학파 TDD | DHH/Fowler |
| 이미 확신이 높은 경우 | 명백한 구현에 test-first 불필요 | 코드 후 테스트(self-testing code) | Beck/Fowler |

**핵심 인사이트**:
- Martin Fowler: "Self-testing code와 TDD는 다르다. TDD는 self-testing code를 달성하는 한 가지 방법이다."
- Kent Beck: "TDD가 프로그래머들을 과잉 확신에 빠뜨려서 QA가 필요 없다고 느끼게 만들었다. 본인이 아닌 다른 사람이 테스트하지 않으면 높은 품질의 소프트웨어를 만들 수 없다."
- DHH: "테스트하기 어려운 코드가 항상 잘못 설계된 것은 아니다" — 이 격언으로부터 테스트 유도 설계 훼손(test-induced design damage)이 발생한다.

> 출처: Kent Beck, *테스트주도 개발*; Martin Fowler, [Is TDD Dead?](https://martinfowler.com/articles/is-tdd-dead/); DHH, [Test-induced design damage](https://dhh.dk/2014/test-induced-design-damage.html)
