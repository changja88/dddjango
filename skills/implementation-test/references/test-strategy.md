# 테스트 전략과 피라미드 레퍼런스

테스트 전략과 분류 체계에 대한 상세 규칙과 예시.

---

## 1. Martin Fowler의 테스트 피라미드

Mike Cohn이 "Succeeding with Agile"에서 처음 제안하고, Martin Fowler가 확장한 개념이다.

```
        /  E2E  \          <- 적게, 느리지만 높은 신뢰도
       /----------\
      / Integration \      <- 중간 수준
     /----------------\
    /    Unit Tests     \  <- 많이, 빠르고 저렴
   /--------------------\
```

**핵심 비율 (Google 기준)**:
- 단위 테스트: ~80%
- 통합 테스트: ~15%
- E2E 테스트: ~5%

**계층별 특성**:

| 구분 | 단위 | 통합 | E2E |
|------|------|------|-----|
| 속도 | 밀리초 | 초 | 분 |
| 범위 | 함수/클래스 | 모듈 간 | 전체 시스템 |
| 격리 | 완전 격리 | 부분 격리 | 실제 환경 |
| 유지비용 | 낮음 | 중간 | 높음 |

**Martin Fowler의 핵심 조언**: "상위 레벨 테스트에서 버그를 발견하면, 해당 버그를 재현하는 단위 테스트를 먼저 작성한 후 수정하라."

> 출처: The Practical Test Pyramid - Ham Vocke, Test Pyramid - Martin Fowler

---

## 2. Google의 SMURF 프레임워크

Google Testing Blog(2024.10)에서 발표한 테스트 피라미드의 확장 모델이다. 테스트 스위트가 성장하면서 단순한 피라미드만으로는 부족한 트레이드오프를 다루기 위한 5가지 차원을 제시한다.

**SMURF = Speed + Maintainability + Utilization + Reliability + Fidelity**

- **Speed(속도)**: 단위 테스트는 빠르므로 자주 실행할 수 있고, 문제를 일찍 발견한다.
- **Maintainability(유지보수성)**: 테스트 디버깅과 유지보수의 누적 비용은 빠르게 증가한다.
- **Utilization(활용도)**: 테스트가 실제로 결함을 발견하는 빈도와 효과.
- **Reliability(신뢰성)**: 테스트 결과의 일관성. flaky 테스트는 신뢰를 떨어뜨린다.
- **Fidelity(충실도)**: 실제 운영 환경에 가까운 테스트일수록 프로덕션 동작을 정확히 예측한다.

**핵심 인사이트**: 이 5개 차원은 종종 긴장 관계에 있다. 한 차원을 개선하면 다른 차원이 영향받을 수 있지만, 다른 차원을 해치지 않으면서 개선할 수 있다면 반드시 그렇게 해야 한다.

> 출처: Google Testing Blog: SMURF: Beyond the Test Pyramid

---

## 3. Google의 테스트 크기 분류

Google은 테스트를 유형(unit/integration/e2e)보다 **크기(size)**로 분류한다.

| 크기 | 제약 |
|------|------|
| Small | 단일 스레드, 단일 프로세스, 단일 머신, I/O 금지, sleep 금지, 블로킹 콜 금지 |
| Medium | 단일 머신, 다중 프로세스 허용 |
| Large | 다중 머신 허용, 네트워크 호출 허용 |

"테스트의 크기는 코드 줄 수가 아니라, 어떻게 실행되고 무엇이 허용되며 얼마나 많은 자원을 소비하는지로 결정된다." - Adam Bender, Software Engineering at Google

> 출처: [Software Engineering at Google - Chapter 11](https://abseil.io/resources/swe-book/html/ch11.html), [Google Testing Blog: Just Say No to More End-to-End Tests](https://testing.googleblog.com/2015/04/just-say-no-to-more-end-to-end-tests.html)
