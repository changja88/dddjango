# 유스케이스(area) 간 공유 — 자료 조사 (T61)

2026-08-11 · 물음 둘: ① 유스케이스가 다른 area 의 것을 직접 import 해도 되는가 ② «공용 모듈 칸»을 트리에 신설해야 하는가. 축은 Clean Architecture(사용자 지정), 보조로 헥사고날·VSA·로컬 코퍼스.

## 원전 근거

### 1. Clean Architecture — 공유의 일급 자리는 «아래층(Entities)»이다

- **Entities 계층 정의**: *"Entities encapsulate **Enterprise wide** business rules."* — 여러 애플리케이션·유스케이스가 공유하는 규칙의 자리로 **설계 자체가 그렇게** 되어 있다.
- **Use Cases 계층 정의**: *"The software in this layer contains **application specific** business rules."* — 유스케이스 층에는 그 유스케이스 고유의 것만 남는다.
- 즉 CA 의 구조에서 «유스케이스들이 공유하는 것»은 정의상 **Entities(우리 트리의 domain_layer)로 내려간 것**이지, 유스케이스 층 옆의 공용 폴더가 아니다.

### 2. Clean Architecture ch.16 (Independence) — 유스케이스 간 통합은 명시 경고 대상

- **수직 분리**: 유스케이스 단위로 시스템을 세로로 갈라 *"'add Order' 팀이 'delete Order' 팀과 간섭하지 않도록"* 하라 — 유스케이스 간 결합 최소화가 목적 그 자체.
- **True vs Accidental Duplication**: *"두 코드가 서로 다른 경로로, 다른 속도·다른 이유로 진화한다면 그것은 진짜 중복이 아니다."* — 그리고 **«유스케이스 사이에 비슷해 보이는 코드»가 우발적 중복의 대표 사례**로 지목된다. 이를 합치면(공용 모듈로 통합하면) 나중에 분리가 어려워 아키텍처가 손상된다.
- → «두 유스케이스가 같이 쓰는 모듈 칸»은 CA 가 **명시적으로 경고하는 함정의 상설화**다.

### 3. Clean Architecture ch.34 (Missing Chapter, Simon Brown) — 접근은 «여는» 게 아니라 «막는» 것

- 조직 4방식(package by layer / by feature / ports&adapters / by component) 비교 끝에: *"아키텍처를 강제하는 최선의 접근은 컴파일러"* — 가시성 제한으로 **잘못된 import 를 불가능하게** 만들라(예: Controller 가 Repository 를 import 못 하게).
- 컴포넌트 원칙: 관련 코드가 «한 컴포넌트 안에서 함께 여행»(컴포넌트 **안** 최대 응집) — 컴포넌트 **간** 공유 통로를 여는 방향이 아니다. 파이썬엔 가시성 수정자가 없으므로 그 컴파일러 역할을 우리 검사기(#189·#205)가 한다.

### 4. Vertical Slice Architecture (Bogard) — 슬라이스 간 공유는 최소로, 필요하면 도메인으로

- *"Minimize coupling **between** slices, and maximize coupling **in** a slice."*
- *"we keep our cross-slice logic sharing to a minimum"*
- 공유가 진짜 필요해지면: *"push complex logic into the domain, into what DDD services **should** have been"* — 공용 helper 가 아니라 **도메인(엔티티·도메인 서비스)으로 내려보낸다**. 리팩터링 시점은 사전 설계가 아니라 냄새가 났을 때.
- 계열 정리: *"Duplication is vastly cheaper than coupling."*

### 5. 헥사고날 (Cockburn) — 이 물음은 포트의 관할이 아니다

- *"A port identifies a **purposeful conversation**"* — 포트는 «바깥과의 목적 있는 대화» 자리다. 애플리케이션 **내부**의 조직(유스케이스 간 공유 포함)은 이 패턴의 범위 밖 — «use_case 는 port 로 절차를 표현한다»는 절반(바깥 대화)만 맞는 이유.

### 6. 로컬 코퍼스 (architecture-ddd final.md) — 같은 결

- 632행: *"판정·불변식은 도메인이 소유 … 응용 서비스는 조회 → 도메인 기능 실행 → 영속화"* — 응용층에 공유할 «판정»이 남아 있으면 그 자체가 빈혈 신호.
- 361행: 공용 승격은 «공유 커널 결정»으로 엄격 통제(같은 변경 사유 근거 필수·범위 최소화) — 편의 공유 통로를 열지 않는 전통.

## 결론

**① 다른 area 직접 import — 금지 유지.** CA 수직 분리(간섭 금지)·Bogard(minimize coupling between slices)·Simon Brown(잘못된 import 를 컴파일러로 차단)이 모두 같은 방향. 유스케이스→타 유스케이스(같은 area 든 다른 area 든) import 는 슬라이스 간 결합 그 자체다. 현행 #189 금지부·#205 유지.

**② 공용 칸 신설 — 원전 지지 근거 없음(반대 근거는 명시적).** 조사한 어느 원전도 «유스케이스 층의 공용 모듈 자리»를 제시하지 않고, CA ch.16 은 그 통합을 우발적 중복의 대표 함정으로 경고한다. 원전들의 공통 답: **공유는 옆(같은 층 공용 폴더)이 아니라 아래(도메인)로 간다** — 업무 지식 → domain_layer(#194 와 합치) · 바깥 능력 → port/ · 기술 → framework/ · 어디도 아니면 중복이 결합보다 싸다.

**→ T61 은 ⓑ(#189 처방부 개정)가 원전 정합**: «올린다» → «제자리로 보낸다(도메인/port/framework), 남으면 중복해 둔다».

## 출처

- Uncle Bob, [The Clean Architecture (2012)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html) — Entities/Use Cases 정의
- serodriguez68 요약, [Part 5 — Independence(ch.16)](https://github.com/serodriguez68/clean-architecture/blob/master/part-5-1-architecture.md) · [Part 6 — Missing Chapter(ch.34)](https://github.com/serodriguez68/clean-architecture/blob/master/part-6-details.md)
- Jimmy Bogard, [Vertical Slice Architecture](https://www.jimmybogard.com/vertical-slice-architecture/)
- Alistair Cockburn, [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)
- 보조: [Vertical slices vs Clean Architecture 논의](https://jeremiahflaga.github.io/2019/05/20/vertical-slice-architecture-is-it-incompatible-with-clean-architecture/) · [architecture-weekly — vertical slices 정리](https://www.architecture-weekly.com/p/my-thoughts-on-vertical-slices-cqrs)
