# 멀티 테넌트 SaaS HR 시스템 -- DDD 전략 설계

## 1. 도메인 비전 선언문

이 시스템은 멀티 테넌트 SaaS 형태의 통합 인사관리 플랫폼이다. 채용부터 온보딩, 근태, 급여, 성과 평가까지 직원 생명주기 전체를 다루며, 각 테넌트(기업 고객)가 독립된 인사 정책과 조직 구조를 운영할 수 있도록 한다.

---

## 2. 하위 도메인 식별 및 분류

전략 설계의 출발점으로, 비즈니스 영역을 하위 도메인으로 분류한다. 하위 도메인은 "발견"하는 것이며, 바운디드 컨텍스트는 "설계"하는 것이다.

| 하위 도메인 | 유형 | 근거 |
|------------|------|------|
| 채용 관리 (Recruitment) | **핵심(Core)** | 채용 파이프라인과 지원자 평가 기준은 기업마다 크게 다르며, SaaS 제품의 차별화 포인트다. 기업별 채용 워크플로우 커스터마이징이 경쟁력이다. |
| 성과 평가 (Performance) | **핵심(Core)** | OKR/KPI 관리와 평가 프로세스는 기업 문화에 따라 고도로 커스터마이징되어야 하며, 이 시스템의 핵심 가치 제안이다. |
| 인사 관리 (Personnel) | **지원(Supporting)** | 직원 정보, 조직도 관리는 HR 시스템의 기본 기능이다. 비즈니스 로직이 복잡하지 않으나, 다른 모든 컨텍스트가 의존하는 기반 데이터를 보유한다. |
| 근태 관리 (Attendance) | **지원(Supporting)** | 출퇴근 기록과 휴가 신청/승인은 정형화된 비즈니스 규칙이다. 기업별 휴가 정책 차이가 있으나 패턴은 정해져 있다. |
| 급여 관리 (Payroll) | **지원(Supporting)** | 급여 계산 자체는 복잡하지만, 세금 규칙과 4대보험 계산은 법률에 의해 정의된 알고리즘이다. 급여 계산 엔진은 응집력 있는 메커니즘(Cohesive Mechanism)으로 분리할 수 있다. |
| 테넌트 관리 (Tenant) | **일반(Generic)** | 멀티 테넌시 기반 구독/과금/테넌트 격리는 SaaS 플랫폼의 범용 기능이다. 기존 솔루션이나 표준 패턴을 활용한다. |
| 인증/권한 (Identity & Access) | **일반(Generic)** | SSO, RBAC, 감사 로그 등은 산업 표준 솔루션(OAuth2, OIDC)으로 해결한다. |
| 알림 (Notification) | **일반(Generic)** | 이메일, 슬랙, 푸시 알림 발송은 범용 인프라다. |

---

## 3. 바운디드 컨텍스트 정의

하위 도메인을 기반으로 바운디드 컨텍스트를 설계한다. 각 컨텍스트는 자체 유비쿼터스 언어를 가지며, 하나의 팀이 소유한다.

### 3.1 Recruitment Context (채용 컨텍스트)

**소유 팀:** 채용 스트림 팀

**유비쿼터스 언어:**

| 용어 | 정의 |
|------|------|
| Job Posting (채용 공고) | 채용할 포지션의 요건과 조건을 명시한 공개 문서 |
| Applicant (지원자) | 채용 공고에 지원한 후보자 |
| Application (지원서) | 지원자가 특정 채용 공고에 제출한 이력서와 자기소개 |
| Hiring Pipeline (채용 파이프라인) | 서류 심사 -> 코딩 테스트 -> 1차 면접 -> 2차 면접 -> 최종 합격 등의 단계 |
| Interview (면접) | 면접관과 지원자 간의 평가 세션. 일정, 장소, 면접관, 평가 결과를 포함 |
| Evaluation (평가) | 면접관이 지원자에 대해 작성한 정량/정성 평가 |
| Offer (오퍼) | 최종 합격자에게 제시하는 입사 조건 (연봉, 직급, 입사일 등) |

**핵심 애그리거트 후보:**
- `JobPosting` -- 채용 공고의 생명주기 관리 (초안 -> 게시 -> 마감)
- `Application` -- 지원서의 파이프라인 단계 진행 관리
- `Interview` -- 면접 일정 조율 및 평가 결과 기록

**주요 도메인 이벤트:**
- `JobPostingPublished` -- 채용 공고가 게시됨
- `ApplicationSubmitted` -- 지원서가 접수됨
- `ApplicationAdvanced` -- 지원서가 다음 단계로 이동함
- `InterviewScheduled` -- 면접 일정이 확정됨
- `InterviewEvaluated` -- 면접 평가가 완료됨
- `OfferExtended` -- 입사 오퍼가 발송됨
- `OfferAccepted` -- 입사 오퍼가 수락됨 (-> Personnel Context로 온보딩 트리거)

---

### 3.2 Personnel Context (인사 관리 컨텍스트)

**소유 팀:** 인사 스트림 팀

**유비쿼터스 언어:**

| 용어 | 정의 |
|------|------|
| Employee (직원) | 회사에 소속된 구성원. 사번, 이름, 직급, 부서 등의 인사 정보를 보유 |
| Onboarding (온보딩) | 신규 입사자의 입사 절차. 계정 생성, 장비 지급, 교육 등의 체크리스트 |
| Department (부서) | 조직도 상의 조직 단위 |
| Position (직위) | 직원이 맡고 있는 역할/직급 |
| Transfer (이동) | 부서 이동 또는 직급 변경 |
| Termination (퇴직) | 직원의 고용 관계 종료 |

주의: "직원"이라는 용어는 이 컨텍스트에서만 전체 인사 정보를 포함한다. 다른 컨텍스트에서는 `employee_id`만 참조하거나, 각 컨텍스트에 맞는 투영(projection)으로 변환한다.

**핵심 애그리거트 후보:**
- `Employee` -- 직원 인사 정보의 생명주기 관리 (온보딩 -> 재직 -> 퇴직)
- `Department` -- 조직도 구조 관리
- `Onboarding` -- 온보딩 체크리스트 진행 추적

**주요 도메인 이벤트:**
- `EmployeeOnboarded` -- 신규 직원이 온보딩 완료됨
- `EmployeeTransferred` -- 직원이 부서/직급 이동함
- `EmployeeTerminated` -- 직원이 퇴직함
- `DepartmentRestructured` -- 조직 구조가 변경됨

---

### 3.3 Attendance Context (근태 관리 컨텍스트)

**소유 팀:** 근태/급여 스트림 팀

**유비쿼터스 언어:**

| 용어 | 정의 |
|------|------|
| Attendance Record (근태 기록) | 특정 날짜의 출근/퇴근 시각 기록 |
| Leave Request (휴가 신청) | 직원이 제출한 휴가 사용 요청 |
| Leave Approval (휴가 승인) | 관리자가 휴가 신청을 승인 또는 반려 |
| Leave Balance (휴가 잔여) | 직원의 휴가 유형별 잔여 일수 |
| Leave Policy (휴가 정책) | 테넌트별 휴가 유형, 부여 규칙, 이월 정책 등 |
| Overtime (초과 근무) | 정규 근무 시간을 초과한 근무 |

**핵심 애그리거트 후보:**
- `AttendanceRecord` -- 일별 출퇴근 기록 관리
- `LeaveRequest` -- 휴가 신청의 생명주기 (신청 -> 승인/반려 -> 사용)
- `LeaveBalance` -- 직원별 휴가 잔여 일수 추적

**주요 도메인 이벤트:**
- `AttendanceRecorded` -- 출퇴근이 기록됨
- `LeaveRequested` -- 휴가가 신청됨
- `LeaveApproved` -- 휴가가 승인됨
- `LeaveRejected` -- 휴가가 반려됨
- `LeaveTaken` -- 휴가가 사용됨 (-> 잔여 일수 차감)
- `OvertimeRecorded` -- 초과 근무가 기록됨 (-> Payroll에 반영)

---

### 3.4 Payroll Context (급여 관리 컨텍스트)

**소유 팀:** 근태/급여 스트림 팀

**유비쿼터스 언어:**

| 용어 | 정의 |
|------|------|
| Payroll Run (급여 정산) | 특정 기간(월)에 대한 급여 일괄 계산 실행 |
| Pay Stub (급여 명세서) | 직원 개인에게 발급되는 급여 상세 내역서 |
| Base Salary (기본급) | 직원의 기본 월 급여 |
| Allowance (수당) | 직책수당, 식대, 교통비 등 추가 급여 항목 |
| Deduction (공제) | 소득세, 4대보험 등 급여에서 차감되는 항목 |
| Tax Calculation (세금 계산) | 근로소득세, 주민세 등의 세금 산출 |
| Net Pay (실수령액) | 기본급 + 수당 - 공제 후 최종 지급 금액 |

주의: 이 컨텍스트에서 "직원"은 급여 수령자(Payee)로만 인식된다. 인사 정보 전체가 아닌 사번, 급여 등급, 계좌 정보만 필요하다.

**핵심 애그리거트 후보:**
- `PayrollRun` -- 월별 급여 정산의 생명주기 (준비 -> 계산 -> 확정 -> 지급)
- `PayStub` -- 개인별 급여 명세서 생성 및 발급

**주요 도메인 이벤트:**
- `PayrollCalculated` -- 급여 계산이 완료됨
- `PayrollConfirmed` -- 급여가 확정됨
- `PayStubIssued` -- 급여 명세서가 발급됨
- `PaymentDispatched` -- 급여가 이체됨

---

### 3.5 Performance Context (성과 평가 컨텍스트)

**소유 팀:** 성과 스트림 팀

**유비쿼터스 언어:**

| 용어 | 정의 |
|------|------|
| Review Cycle (평가 주기) | 반기/연간 성과 평가 기간 |
| Objective (목표) | OKR의 Objective. 달성하고자 하는 정성적 목표 |
| Key Result (핵심 결과) | OKR의 Key Result. 목표 달성을 측정하는 정량적 지표 |
| Self Review (자기 평가) | 직원 본인이 작성하는 성과 자기 평가 |
| Peer Review (동료 평가) | 동료가 작성하는 상호 평가 |
| Manager Review (상위 평가) | 관리자가 작성하는 하향 평가 |
| Performance Rating (성과 등급) | 최종 산출되는 성과 등급 (S/A/B/C/D 등) |
| Calibration (보정) | 부서/전사 차원에서 평가 등급 분포를 조정하는 과정 |

**핵심 애그리거트 후보:**
- `ReviewCycle` -- 평가 주기의 생명주기 (설정 -> 목표 수립 -> 중간 점검 -> 최종 평가 -> 보정 -> 확정)
- `ObjectiveSet` -- 직원의 OKR 목표 세트 관리
- `PerformanceReview` -- 개인별 평가 결과 (자기/동료/상위 평가를 종합)

**주요 도메인 이벤트:**
- `ReviewCycleOpened` -- 평가 주기가 시작됨
- `ObjectivesSubmitted` -- OKR 목표가 제출됨
- `SelfReviewSubmitted` -- 자기 평가가 제출됨
- `ManagerReviewCompleted` -- 상위 평가가 완료됨
- `CalibrationCompleted` -- 보정이 완료됨
- `FinalRatingConfirmed` -- 최종 성과 등급이 확정됨

---

### 3.6 Tenant Context (테넌트 관리 컨텍스트)

**소유 팀:** 플랫폼 팀

**유비쿼터스 언어:**

| 용어 | 정의 |
|------|------|
| Tenant (테넌트) | SaaS 플랫폼을 구독하는 기업 고객 |
| Subscription (구독) | 테넌트의 요금제와 구독 상태 |
| Plan (요금제) | 기능 범위와 사용자 수 제한을 정의하는 과금 단위 |
| Tenant Configuration (테넌트 설정) | 테넌트별 커스텀 설정 (근무 시간, 휴일, 평가 등급 체계 등) |

**핵심 애그리거트 후보:**
- `Tenant` -- 테넌트의 생명주기 관리 (가입 -> 활성 -> 해지)
- `Subscription` -- 구독/요금제 관리

---

### 3.7 Identity & Access Context (인증/권한 컨텍스트)

**소유 팀:** 플랫폼 팀

**유비쿼터스 언어:**

| 용어 | 정의 |
|------|------|
| User (사용자) | 시스템에 로그인하는 계정 |
| Role (역할) | 시스템 기능에 대한 권한 묶음 (관리자, HR 매니저, 직원 등) |
| Permission (권한) | 개별 기능 수행 허가 |

주의: 이 컨텍스트에서의 "User"는 인증/인가 대상이다. Personnel Context의 "Employee"와는 다른 개념이다. 동일 인물이지만, 각 컨텍스트에서 다른 모델로 표현된다.

**핵심 애그리거트 후보:**
- `User` -- 계정 생명주기 및 인증 관리
- `Role` -- 역할 기반 접근 제어 관리

---

### 3.8 Notification Context (알림 컨텍스트)

**소유 팀:** 플랫폼 팀

**유비쿼터스 언어:**

| 용어 | 정의 |
|------|------|
| Notification (알림) | 사용자에게 전달되는 메시지 |
| Channel (채널) | 이메일, 슬랙, 인앱 푸시 등 알림 전달 수단 |
| Template (템플릿) | 알림 내용의 정형화된 양식 |

**핵심 애그리거트 후보:**
- `Notification` -- 알림 발송 관리

---

## 4. 컨텍스트 맵

### 4.1 전체 관계 다이어그램

```
                              +-----------------------+
                              |    Tenant Context     |
                              |      (일반/OHS)       |
                              +----------+------------+
                                         |
                        OHS/PL (테넌트 설정, 구독 정보)
                                         |
         +-------------------------------+-------------------------------+
         |               |               |               |               |
         v               v               v               v               v
+--------+------+ +------+--------+ +----+----------+ +--+------------+ +-+-------------+
| Recruitment   | |  Personnel    | |  Attendance   | |   Payroll     | |  Performance  |
|   Context     | |   Context     | |   Context     | |   Context     | |   Context     |
|  (핵심)       | |  (지원)       | |  (지원)       | |  (지원)       | |  (핵심)       |
+--+----+-------+ +--+-----+-----+ +--+----+-------+ +--+----+-------+ +--+----+-------+
   |    |            |     |           |    |            |    |            |    |
   |    +--Event---->+     |           |    |            |    |            |    |
   |  OfferAccepted  |     |           +----+--Event---->+    |            |    |
   |                 |     |         근태/초과근무 데이터 |    |            |    |
   |                 |     +----------ACL--->+           |    |            |    |
   |                 |   직원 기본 정보       |           |    |            |    |
   |                 |     +-----------ACL--->+-----------+    |            |    |
   |                 |     |                                   |            |    |
   |                 |     +-----------------------------------+--ACL----->+    |
   |                 |     |           직원 정보 조회                       |    |
   |                 |     |                                               |    |
   |                 +-----+-----------------------------------------------+    |
   |                       |                                                    |
   v                       v                                                    v
+--+-----------------------+----------------------------------------------------+--+
|                        Identity & Access Context (일반/OHS)                      |
+--+-------------------------------------------------------------------------------+
                                         |
                                    OHS (인증/인가)
                                         |
+--+-------------------------------------------------------------------------------+
|                         Notification Context (일반)                               |
+--+-----+----------+----------+-----------+---------------------------------------+
         ^          ^          ^           ^
    이벤트 구독  이벤트 구독  이벤트 구독  이벤트 구독
   (Recruitment) (Personnel) (Attendance) (Performance)
```

### 4.2 컨텍스트 간 관계 상세

#### (1) Recruitment -> Personnel : 고객-공급자 (Customer-Supplier) + 도메인 이벤트

| 항목 | 내용 |
|------|------|
| 업스트림 | Recruitment Context |
| 다운스트림 | Personnel Context |
| 패턴 | **고객-공급자(Customer-Supplier)** |
| 통합 메커니즘 | 도메인 이벤트 (`OfferAccepted`) |
| 설명 | 지원자가 오퍼를 수락하면 `OfferAccepted` 이벤트가 발행된다. Personnel Context가 이 이벤트를 구독하여 신규 직원 온보딩 프로세스를 시작한다. Recruitment의 "Applicant"가 Personnel의 "Employee"로 변환되는 시점이다. |
| 선택 근거 | Recruitment가 없어도 Personnel은 독립 운영 가능하나, 자동화된 온보딩을 위해 Recruitment가 Personnel의 요구(입사자 기본 정보 형식)를 계획에 반영해야 한다. |

#### (2) Personnel -> Attendance : 고객-공급자 (Customer-Supplier) + ACL

| 항목 | 내용 |
|------|------|
| 업스트림 | Personnel Context |
| 다운스트림 | Attendance Context |
| 패턴 | **고객-공급자(Customer-Supplier)** + **ACL** |
| 통합 메커니즘 | OHS/PL (Personnel이 직원 기본 정보 API 제공) + ACL (Attendance가 자체 모델로 변환) |
| 설명 | Attendance Context는 근태를 기록하기 위해 직원 정보(사번, 부서, 근무 스케줄)가 필요하다. Personnel이 OHS로 직원 정보를 제공하되, Attendance는 ACL을 통해 전체 인사 정보 중 근태에 필요한 정보만 자체 모델(`AttendanceWorker`)로 변환하여 사용한다. |
| 선택 근거 | Personnel의 Employee 모델에는 급여, 학력, 가족관계 등 근태와 무관한 정보가 포함되어 있다. ACL로 모델 오염을 차단한다. |

#### (3) Personnel -> Payroll : 고객-공급자 (Customer-Supplier) + ACL

| 항목 | 내용 |
|------|------|
| 업스트림 | Personnel Context |
| 다운스트림 | Payroll Context |
| 패턴 | **고객-공급자(Customer-Supplier)** + **ACL** |
| 통합 메커니즘 | OHS/PL + ACL |
| 설명 | Payroll은 급여 계산을 위해 직원의 급여 등급, 입사일, 부서 정보가 필요하다. Personnel의 Employee 모델을 Payroll의 `Payee`(급여 수령자) 모델로 변환하는 ACL을 둔다. |
| 선택 근거 | Payroll에서의 "직원"은 급여 수령자로서의 관점만 필요하다. Personnel의 풍부한 인사 정보가 Payroll 도메인 모델을 오염시키지 않도록 ACL로 방어한다. |

#### (4) Attendance -> Payroll : 고객-공급자 (Customer-Supplier) + 도메인 이벤트

| 항목 | 내용 |
|------|------|
| 업스트림 | Attendance Context |
| 다운스트림 | Payroll Context |
| 패턴 | **고객-공급자(Customer-Supplier)** |
| 통합 메커니즘 | 도메인 이벤트 (`OvertimeRecorded`, `LeaveApproved`, `AttendanceRecorded`) |
| 설명 | 급여 계산에는 근태 데이터(근무 일수, 초과 근무 시간, 유급 휴가 사용일)가 필수다. Attendance에서 발생하는 근태 이벤트를 Payroll이 구독하여 급여 계산 시 반영한다. |
| 선택 근거 | 근태 데이터는 급여 정산 주기(월말)에 일괄 조회하는 것도 가능하지만, 이벤트 기반으로 실시간 집계하면 급여 정산 시점의 부하를 분산할 수 있다. |

#### (5) Personnel -> Performance : 고객-공급자 (Customer-Supplier) + ACL

| 항목 | 내용 |
|------|------|
| 업스트림 | Personnel Context |
| 다운스트림 | Performance Context |
| 패턴 | **고객-공급자(Customer-Supplier)** + **ACL** |
| 통합 메커니즘 | OHS/PL + ACL |
| 설명 | Performance Context는 평가 대상 직원의 정보(사번, 이름, 부서, 직급, 관리자)가 필요하다. ACL을 통해 Personnel의 Employee를 Performance의 `ReviewSubject`(평가 대상자)로 변환한다. |
| 선택 근거 | 성과 평가에서의 "직원"은 평가 대상자/평가자 역할이다. 인사 정보 전체가 아닌 평가에 필요한 속성만 가져야 한다. |

#### (6) Performance -> Payroll : 도메인 이벤트 (비동기)

| 항목 | 내용 |
|------|------|
| 업스트림 | Performance Context |
| 다운스트림 | Payroll Context |
| 패턴 | **고객-공급자(Customer-Supplier)** |
| 통합 메커니즘 | 도메인 이벤트 (`FinalRatingConfirmed`) |
| 설명 | 성과 등급이 확정되면 `FinalRatingConfirmed` 이벤트가 발행된다. Payroll이 이를 구독하여 성과급/인센티브 계산에 반영한다. |
| 선택 근거 | 성과 등급 확정과 급여 반영은 시차가 있으므로, 결과적 일관성(eventual consistency)이 적합하다. |

#### (7) Tenant -> 모든 도메인 컨텍스트 : OHS/PL (발행된 언어)

| 항목 | 내용 |
|------|------|
| 업스트림 | Tenant Context |
| 다운스트림 | Recruitment, Personnel, Attendance, Payroll, Performance |
| 패턴 | **오픈 호스트 서비스(OHS)** + **발행된 언어(Published Language)** |
| 통합 메커니즘 | REST API / 공유 설정 스키마 |
| 설명 | 테넌트 설정(근무 시간, 휴일 목록, 평가 등급 체계, 급여 정책 등)은 각 도메인 컨텍스트에서 참조해야 한다. Tenant Context가 발행된 언어(JSON Schema 등)를 통해 설정 데이터를 제공한다. |
| 선택 근거 | 다수의 다운스트림이 존재하므로 OHS가 적합하다. 각 컨텍스트는 필요한 설정만 선택적으로 소비한다. |

#### (8) Identity & Access -> 모든 컨텍스트 : OHS/PL

| 항목 | 내용 |
|------|------|
| 업스트림 | Identity & Access Context |
| 다운스트림 | 모든 도메인 컨텍스트 |
| 패턴 | **오픈 호스트 서비스(OHS)** + **발행된 언어(Published Language)** |
| 통합 메커니즘 | JWT 토큰 / OAuth2 프로토콜 |
| 설명 | 인증/인가는 표준 프로토콜로 모든 컨텍스트에 횡단 관심사로 제공된다. 각 컨텍스트는 JWT 토큰에서 `tenant_id`, `user_id`, `roles`를 추출하여 사용한다. |
| 선택 근거 | 일반 하위 도메인으로서 산업 표준 프로토콜(OAuth2/OIDC)을 사용하므로, 다운스트림이 **순응주의자(Conformist)** 패턴으로 표준을 그대로 따른다. |

#### (9) 모든 도메인 컨텍스트 -> Notification : 도메인 이벤트 구독

| 항목 | 내용 |
|------|------|
| 업스트림 | Recruitment, Personnel, Attendance, Performance |
| 다운스트림 | Notification Context |
| 패턴 | **순응주의자(Conformist)** |
| 통합 메커니즘 | 도메인 이벤트 구독 |
| 설명 | Notification Context는 각 도메인 컨텍스트의 이벤트를 구독하여 적절한 알림을 발송한다. `InterviewScheduled` -> 면접 일정 알림, `LeaveApproved` -> 휴가 승인 알림, `FinalRatingConfirmed` -> 평가 결과 알림 등. |
| 선택 근거 | Notification은 도메인 이벤트의 구조를 그대로 수용하여 알림을 생성한다. 업스트림 이벤트 스키마에 맞춰 템플릿을 매핑하는 순응주의자 패턴이 적합하다. |

### 4.3 관계 요약 매트릭스

| 업스트림 \ 다운스트림 | Recruitment | Personnel | Attendance | Payroll | Performance | Notification |
|----------------------|-------------|-----------|------------|---------|-------------|--------------|
| **Recruitment** | -- | CS + Event | -- | -- | -- | Conformist |
| **Personnel** | -- | -- | CS + ACL | CS + ACL | CS + ACL | Conformist |
| **Attendance** | -- | -- | -- | CS + Event | -- | Conformist |
| **Performance** | -- | -- | -- | CS + Event | -- | Conformist |
| **Tenant** | OHS/PL | OHS/PL | OHS/PL | OHS/PL | OHS/PL | -- |
| **Identity & Access** | OHS/PL | OHS/PL | OHS/PL | OHS/PL | OHS/PL | OHS/PL |

*CS = Customer-Supplier, ACL = Anti-Corruption Layer, OHS/PL = Open Host Service/Published Language*

---

## 5. 멀티 테넌시 전략적 고려사항

멀티 테넌트 환경에서 바운디드 컨텍스트 설계 시 추가로 고려해야 할 사항:

### 5.1 테넌트 격리와 바운디드 컨텍스트

테넌트 격리는 모든 바운디드 컨텍스트에 횡단으로 적용되는 인프라 관심사다. 도메인 모델 수준에서 `tenant_id`를 명시적으로 포함하되, 이를 도메인 로직이 아닌 인프라 계층(리포지토리, 미들웨어)에서 필터링한다.

### 5.2 테넌트별 정책 차이

같은 바운디드 컨텍스트 안에서도 테넌트별로 다른 비즈니스 규칙이 적용될 수 있다:
- 휴가 정책 (연차 일수, 이월 규칙)
- 평가 등급 체계 (5단계 vs 3단계)
- 채용 파이프라인 단계 (코딩 테스트 유무)
- 급여 체계 (호봉제 vs 연봉제)

이러한 정책 차이는 Tenant Context에서 설정으로 관리하고, 각 도메인 컨텍스트는 `TenantConfiguration`을 참조하여 정책을 적용한다. Strategy 패턴이나 Specification 패턴으로 테넌트별 규칙을 캡슐화한다.

### 5.3 유비쿼터스 언어와 테넌시

"직원"이라는 용어가 각 컨텍스트에서 다르게 표현됨에 주의한다:

| 컨텍스트 | "직원"의 표현 | 포함하는 정보 |
|----------|-------------|-------------|
| Personnel | `Employee` | 전체 인사 정보 (사번, 이름, 주소, 학력, 가족관계, 계좌 등) |
| Attendance | `AttendanceWorker` | 사번, 부서, 근무 스케줄 |
| Payroll | `Payee` | 사번, 급여 등급, 계좌 정보 |
| Performance | `ReviewSubject` | 사번, 이름, 부서, 직급, 관리자 ID |
| Recruitment | `Applicant` (입사 전) | 지원자 정보 (Employee 아님) |
| Identity & Access | `User` | 계정 ID, 이메일, 역할 목록 |

이 분리가 바운디드 컨텍스트의 핵심이다. 같은 인물을 가리키지만 각 컨텍스트가 필요한 속성과 행위만 자체 모델에 포함한다. 컨텍스트 간에는 `employee_id`(ID 참조)로만 연결한다.

---

## 6. 핵심 도메인 이벤트 흐름

주요 비즈니스 프로세스의 이벤트 흐름을 정리한다:

### 6.1 채용 -> 온보딩 흐름

```
[Recruitment Context]                    [Personnel Context]
  Applicant                                Employee
    |                                        |
    +-- ApplicationSubmitted                 |
    +-- InterviewScheduled                   |
    +-- InterviewEvaluated                   |
    +-- OfferExtended                        |
    +-- OfferAccepted -----(Event)---------->+-- 온보딩 시작
                                             +-- EmployeeOnboarded ----+
                                                                       |
                                             [Attendance Context]  <---+
                                               LeaveBalance 초기화
                                                                       |
                                             [Identity & Access]   <---+
                                               User 계정 생성
```

### 6.2 월말 급여 정산 흐름

```
[Attendance Context]         [Performance Context]       [Payroll Context]
  AttendanceRecorded --+       FinalRatingConfirmed --+     |
  OvertimeRecorded ----+                              |     |
  LeaveApproved -------+----(Events)------------------+---->+
                                                            |
                       [Personnel Context]                  |
                         Employee 급여 정보 ----(ACL)------>+
                                                            |
                                                        PayrollRun
                                                            |
                                                        PayrollCalculated
                                                            |
                                                        PayrollConfirmed
                                                            |
                                                        PayStubIssued -----> [Notification]
                                                            |                  알림 발송
                                                        PaymentDispatched
```

---

## 7. 팀 토폴로지 매핑

Conway의 법칙을 역으로 활용하여, 바운디드 컨텍스트에 맞는 팀 구조를 설계한다:

| 팀 유형 | 팀 | 소유 컨텍스트 | 비고 |
|---------|-----|-------------|------|
| Stream-aligned | 채용 스트림 팀 | Recruitment Context | 핵심 도메인 -- 최고 인재 배치 |
| Stream-aligned | 성과 스트림 팀 | Performance Context | 핵심 도메인 -- 최고 인재 배치 |
| Stream-aligned | 인사 스트림 팀 | Personnel Context | 지원 도메인 -- 안정적 운영 |
| Stream-aligned | 근태/급여 스트림 팀 | Attendance + Payroll Context | 지원 도메인 -- 두 컨텍스트가 밀접하므로 한 팀 |
| Platform | 플랫폼 팀 | Tenant + Identity & Access + Notification | 일반 도메인 -- OHS로 공통 서비스 제공 |
