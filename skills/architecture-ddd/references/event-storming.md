# 이벤트 스토밍과 팀 토폴로지

## 2.7 Event Storming (이벤트 스토밍)

> 출처: Alberto Brandolini, "Introducing EventStorming"; Vernon "DDD Distilled"

도메인 발견 기법이다. DDD의 전략 설계(바운디드 컨텍스트 식별, 핵심 도메인 발견)를 실행하기 위한 워크숍 방법론이다.

### 포스트잇 색상 체계

| 색상 | 개념 | 설명 | 시제 |
|------|------|------|------|
| 주황색 | 도메인 이벤트 (Domain Event) | 비즈니스에서 발생한 사건 | 과거형 ("주문이 접수되었다") |
| 파란색 | 커맨드 (Command) | 이벤트를 유발하는 의도적 행동 | 현재형 ("주문을 접수하라") |
| 노란색 | 애그리거트 (Aggregate) | 커맨드를 받아 이벤트를 발생시키는 주체 | -- |
| 라일락(lilac) | 정책/프로세스 (Policy) | 이벤트에 반응하여 새로운 커맨드를 생성하는 비즈니스 규칙 | -- |
| 초록색 | 읽기 모델 (Read Model) | 사용자가 커맨드를 실행하기 위해 보는 정보 | -- |
| 분홍색 | 외부 시스템 (External System) | 도메인 밖에서 커맨드를 유발하는 시스템 | -- |
| 작은 노란색 | 액터 (Actor/Person) | 커맨드를 실행하는 사용자 역할 | -- |
| 빨간색/핫핑크 | 핫스팟 (Hot Spot) | 논쟁, 질문, 불확실한 영역 | -- |

### 세 가지 변형

| 변형 | 목적 | 참여자 | 결과물 |
|------|------|--------|--------|
| Big Picture | 전체 비즈니스 프로세스를 조감도로 파악 | 10~30명, 다양한 부서 | 바운디드 컨텍스트 경계 후보 |
| Process Modelling | 특정 비즈니스 프로세스를 상세 모델링 | 5~10명, 도메인 전문가 + 개발자 | 커맨드, 이벤트, 정책 흐름 |
| Software Design | 구체적인 소프트웨어 설계로 전환 | 3~5명, 개발 팀 | 애그리거트, 읽기 모델, 외부 시스템 설계 |

## 2.8 전략 DDD와 팀 토폴로지

> 출처: Matthew Skelton & Manuel Pais, "Team Topologies" (2019); Martin Fowler, Conway's Law

**Conway의 법칙:** "시스템을 설계하는 조직은 자신의 커뮤니케이션 구조를 복제하는 설계를 산출하게 된다."

**역 Conway 기동(Inverse Conway Maneuver):** 원하는 소프트웨어 아키텍처를 먼저 설계하고, 그에 맞게 팀 구조를 의도적으로 재편한다.

| 팀 토폴로지 유형 | DDD 개념 매핑 |
|---------------|-------------|
| Stream-aligned Team | 핵심/지원 하위 도메인의 바운디드 컨텍스트를 소유 |
| Platform Team | 일반 하위 도메인에 해당. 공통 인프라를 OHS로 제공 |
| Enabling Team | 컨텍스트 매핑에서 Partnership 관계 |
| Complicated Subsystem Team | 응집력 있는 메커니즘(Cohesive Mechanism) 담당 |
