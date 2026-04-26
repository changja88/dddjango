# 멀티 테넌트 HR SaaS - DDD 바운디드 컨텍스트 설계

## 1. 바운디드 컨텍스트 식별

### BC 1: Tenant Management (테넌트 관리)
- **핵심 책임**: 멀티 테넌트 격리, 테넌트 등록/설정, 구독 플랜 관리
- **주요 개념**: Tenant, Subscription, Plan, TenantConfiguration
- **유형**: Generic Subdomain

### BC 2: Identity & Access (인증/인가)
- **핵심 책임**: 사용자 인증, 역할 기반 접근 제어, 테넌트별 권한 관리
- **주요 개념**: User, Role, Permission, AuthToken
- **유형**: Generic Subdomain

### BC 3: Recruitment (채용)
- **핵심 책임**: 채용 공고 등록, 지원자 추적, 면접 일정 관리, 채용 파이프라인
- **주요 개념**: JobPosting, Applicant, Application, Interview, InterviewSchedule, HiringPipeline
- **주요 Aggregate**: JobPosting (Root), Application (Root)
- **유형**: Core Domain

### BC 4: Employee Management (직원/인사 관리)
- **핵심 책임**: 직원 온보딩, 인사 정보 관리, 조직도, 부서/직급 체계
- **주요 개념**: Employee, Department, Position, OrganizationChart, OnboardingProcess
- **주요 Aggregate**: Employee (Root), Department (Root)
- **유형**: Core Domain

### BC 5: Attendance (근태 관리)
- **핵심 책임**: 출퇴근 기록, 근무 시간 계산, 초과 근무 관리
- **주요 개념**: AttendanceRecord, WorkSchedule, Overtime, TimeSheet
- **주요 Aggregate**: TimeSheet (Root)
- **유형**: Core Domain

### BC 6: Leave (휴가 관리)
- **핵심 책임**: 휴가 신청, 승인 워크플로, 잔여 휴가 관리, 휴가 정책
- **주요 개념**: LeaveRequest, LeaveBalance, LeavePolicy, ApprovalWorkflow
- **주요 Aggregate**: LeaveRequest (Root), LeaveBalance (Root)
- **유형**: Core Domain

### BC 7: Payroll (급여)
- **핵심 책임**: 급여 계산, 세금 처리, 공제 항목 관리, 급여 명세서 발행
- **주요 개념**: PayrollRun, SalaryStructure, TaxCalculation, Deduction, PaySlip
- **주요 Aggregate**: PayrollRun (Root), SalaryStructure (Root)
- **유형**: Core Domain

### BC 8: Performance (성과/목표 관리)
- **핵심 책임**: 성과 평가 주기 관리, OKR 설정/추적, 평가 결과 관리
- **주요 개념**: ReviewCycle, PerformanceReview, Objective, KeyResult, Rating
- **주요 Aggregate**: ReviewCycle (Root), Objective (Root)
- **유형**: Core Domain

---

## 2. 컨텍스트 맵

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Tenant Management (U)                            │
│                  [테넌트 격리 / 구독 관리]                            │
└──────┬──────────────┬──────────┬──────────┬──────────┬──────┬───────┘
       │ OHS/PL       │          │          │          │      │
       ▼              ▼          ▼          ▼          ▼      ▼
┌─────────────┐  ┌─────────┐ ┌──────┐ ┌───────┐ ┌────────┐ ┌─────────┐
│  Identity   │  │Recruit- │ │Emplo-│ │Attend-│ │ Leave  │ │Perfor-  │
│  & Access   │  │ment     │ │yee   │ │ance   │ │        │ │mance    │
│    (U)      │  │         │ │Mgmt  │ │       │ │        │ │         │
└──┬──┬──┬────┘  └────┬────┘ └──┬───┘ └───┬───┘ └───┬────┘ └────┬────┘
   │  │  │            │         │         │         │            │
   │  │  │            │    ┌────┘         │         │            │
   │  │  │            │    │              │         │            │
   │  │  └────────────┼────┼──────────────┼─────────┼────────────┘
   │  │               │    │              │         │
   │  │               ▼    ▼              │         │
   │  │          ┌──────────────┐         │         │
   │  │          │   Payroll    │◄────────┘─────────┘
   │  │          │  [급여 계산]  │
   │  │          └──────────────┘
   │  │
   │  └──── (OHS/PL: 모든 BC에 인증/인가 제공)
   │
   └──── (CF: Recruitment → Employee Mgmt 채용 확정 시)
```

---

## 3. 컨텍스트 간 관계 상세 정의

### 3.1 Tenant Management --> 모든 BC
- **관계 유형**: Open Host Service / Published Language (OHS/PL)
- **방향**: Tenant Management (Upstream) --> 모든 BC (Downstream)
- **설명**: 테넌트 정보와 격리 정책을 표준화된 인터페이스로 모든 컨텍스트에 제공한다. 각 BC는 요청 시 TenantId를 포함하며, Tenant Management가 제공하는 테넌트 컨텍스트 정보를 Conformist로 수용한다.
- **통합 방식**: 공유 커널 수준의 TenantId를 각 BC에서 참조

### 3.2 Identity & Access --> 모든 BC
- **관계 유형**: Open Host Service / Published Language (OHS/PL)
- **방향**: Identity & Access (Upstream) --> 모든 BC (Downstream)
- **설명**: 인증 토큰 검증, 역할/권한 확인 API를 표준 인터페이스로 제공한다. 각 BC는 ACL을 통해 인증 정보를 자체 도메인 개념으로 변환한다.
- **통합 방식**: JWT 토큰 기반 인증, 각 BC에서 ACL로 권한 개념 변환

### 3.3 Recruitment --> Employee Management
- **관계 유형**: Customer-Supplier (고객-공급자)
- **방향**: Recruitment (Upstream) --> Employee Management (Downstream/Customer)
- **설명**: 채용이 확정되면 Recruitment가 `HiringCompleted` 도메인 이벤트를 발행한다. Employee Management는 이를 구독하여 신규 직원 온보딩 프로세스를 시작한다. Employee Management가 고객으로서 필요한 데이터 형식을 Recruitment에 요구할 수 있다.
- **통합 방식**: 비동기 도메인 이벤트 (`HiringCompleted`)
- **ACL**: Employee Management 측에 Anti-Corruption Layer를 두어 Applicant 개념을 Employee 개념으로 변환

### 3.4 Employee Management --> Attendance
- **관계 유형**: Customer-Supplier (고객-공급자)
- **방향**: Employee Management (Upstream) --> Attendance (Downstream/Customer)
- **설명**: Attendance는 직원 정보(소속 부서, 근무 형태 등)를 Employee Management로부터 받는다. 직원 입/퇴사, 부서 이동 시 Attendance가 관련 정보를 갱신한다.
- **통합 방식**: 도메인 이벤트 (`EmployeeOnboarded`, `EmployeeTransferred`, `EmployeeTerminated`)
- **ACL**: Attendance 측에서 Employee를 WorkerProfile이라는 자체 개념으로 변환

### 3.5 Employee Management --> Leave
- **관계 유형**: Customer-Supplier (고객-공급자)
- **방향**: Employee Management (Upstream) --> Leave (Downstream/Customer)
- **설명**: Leave는 직원의 입사일, 직급, 근속 연수 등을 기반으로 휴가 정책을 적용한다. 직원 상태 변경 이벤트를 구독하여 휴가 잔여일을 조정한다.
- **통합 방식**: 도메인 이벤트 (`EmployeeOnboarded`, `EmployeeTerminated`)
- **ACL**: Leave 측에서 Employee를 LeaveEligibility라는 자체 개념으로 변환

### 3.6 Employee Management --> Payroll
- **관계 유형**: Customer-Supplier (고객-공급자)
- **방향**: Employee Management (Upstream) --> Payroll (Downstream/Customer)
- **설명**: Payroll은 직원의 급여 등급, 직급, 입사일 등 인사 정보를 기반으로 급여를 계산한다. Employee Management가 공급자로서 직원 정보 변경을 이벤트로 알린다.
- **통합 방식**: 도메인 이벤트 (`EmployeeOnboarded`, `SalaryGradeChanged`, `EmployeeTerminated`)
- **ACL**: Payroll 측에서 Employee를 PayrollProfile로 변환

### 3.7 Employee Management --> Performance
- **관계 유형**: Customer-Supplier (고객-공급자)
- **방향**: Employee Management (Upstream) --> Performance (Downstream/Customer)
- **설명**: Performance는 직원의 소속 부서, 직급, 관리자 정보를 기반으로 평가 대상/평가자를 결정한다.
- **통합 방식**: 동기 API 호출 (조직 구조 조회)
- **ACL**: Performance 측에서 Employee를 Reviewee/Reviewer로 변환

### 3.8 Attendance --> Payroll
- **관계 유형**: Customer-Supplier (고객-공급자)
- **방향**: Attendance (Upstream) --> Payroll (Downstream/Customer)
- **설명**: Payroll은 급여 계산 시 근태 데이터(근무 시간, 초과 근무, 결근)를 Attendance로부터 조회한다. Payroll이 고객으로서 필요한 데이터 형식(월별 근태 요약)을 요구한다.
- **통합 방식**: 동기 API 호출 (월별 TimeSheet 요약 조회)
- **ACL**: Payroll 측에서 TimeSheet를 WorkedHoursSummary로 변환

### 3.9 Leave --> Payroll
- **관계 유형**: Customer-Supplier (고객-공급자)
- **방향**: Leave (Upstream) --> Payroll (Downstream/Customer)
- **설명**: Payroll은 급여 계산 시 유급/무급 휴가 사용 내역을 Leave로부터 조회하여 급여에 반영한다.
- **통합 방식**: 동기 API 호출 (월별 휴가 사용 내역 조회)
- **ACL**: Payroll 측에서 LeaveRecord를 PaidAbsence/UnpaidAbsence로 변환

### 3.10 Leave --> Attendance
- **관계 유형**: Partnership (파트너십)
- **방향**: 양방향
- **설명**: 휴가가 승인되면 Attendance에 해당 날짜를 휴가로 기록해야 하고, Attendance의 결근 기록이 사후 휴가 처리로 전환될 수 있다. 두 팀이 동등한 관계에서 협력한다.
- **통합 방식**: 양방향 도메인 이벤트 (`LeaveApproved`, `AbsenceRecorded`)

### 3.11 Performance --> Payroll
- **관계 유형**: Customer-Supplier (고객-공급자)
- **방향**: Performance (Upstream) --> Payroll (Downstream/Customer)
- **설명**: 성과 평가 결과가 확정되면 성과급/인센티브 계산에 반영된다. Payroll이 고객으로서 평가 결과 데이터를 요구한다.
- **통합 방식**: 도메인 이벤트 (`ReviewCycleCompleted`)
- **ACL**: Payroll 측에서 PerformanceRating을 IncentiveGrade로 변환

---

## 4. 컨텍스트 맵 요약 테이블

| # | Upstream (공급자) | Downstream (고객) | 관계 유형 | 통합 패턴 | 핵심 이벤트/API |
|---|---|---|---|---|---|
| 1 | Tenant Mgmt | 모든 BC | OHS/PL | Shared Kernel (TenantId) | - |
| 2 | Identity & Access | 모든 BC | OHS/PL | JWT + ACL | - |
| 3 | Recruitment | Employee Mgmt | Customer-Supplier | 비동기 이벤트 + ACL | `HiringCompleted` |
| 4 | Employee Mgmt | Attendance | Customer-Supplier | 비동기 이벤트 + ACL | `EmployeeOnboarded` |
| 5 | Employee Mgmt | Leave | Customer-Supplier | 비동기 이벤트 + ACL | `EmployeeOnboarded` |
| 6 | Employee Mgmt | Payroll | Customer-Supplier | 비동기 이벤트 + ACL | `SalaryGradeChanged` |
| 7 | Employee Mgmt | Performance | Customer-Supplier | 동기 API + ACL | 조직 구조 조회 |
| 8 | Attendance | Payroll | Customer-Supplier | 동기 API + ACL | TimeSheet 요약 조회 |
| 9 | Leave | Payroll | Customer-Supplier | 동기 API + ACL | 휴가 내역 조회 |
| 10 | Leave | Attendance | Partnership | 양방향 이벤트 | `LeaveApproved` |
| 11 | Performance | Payroll | Customer-Supplier | 비동기 이벤트 + ACL | `ReviewCycleCompleted` |

---

## 5. Shared Kernel

모든 BC가 공유하는 최소한의 개념:

```
Shared Kernel
├── TenantId (Value Object)
├── EmployeeId (Value Object)
├── Money (Value Object) — 통화, 금액
├── DateRange (Value Object) — 기간 표현
└── AuditInfo (Value Object) — 생성자, 생성일, 수정자, 수정일
```

- Shared Kernel은 최소한으로 유지하며, 변경 시 모든 BC 팀의 합의가 필요하다.
- EmployeeId는 Employee Management에서 발급하고 다른 BC에서 참조 키로만 사용한다.

---

## 6. 주요 도메인 이벤트 흐름

### 채용 -> 온보딩 흐름
```
Recruitment                    Employee Management
    │                                │
    │  HiringCompleted               │
    │  {applicantId, position,       │
    │   startDate, offer}            │
    ├───────────────────────────────►│
    │                   [ACL 변환]    │
    │                   Applicant    │
    │                   → Employee   │
    │                                ├──► EmployeeOnboarded
    │                                │    {employeeId, dept, startDate}
    │                                │
    │                                ├───────► Attendance (근태 프로필 생성)
    │                                ├───────► Leave (휴가 잔여일 초기화)
    │                                ├───────► Payroll (급여 구조 설정)
    │                                └───────► Performance (평가 대상 등록)
```

### 월말 급여 계산 흐름
```
Payroll                        Attendance        Leave         Performance
    │                              │               │               │
    │  GET /timesheet-summary      │               │               │
    ├─────────────────────────────►│               │               │
    │◄─────────────────────────────┤               │               │
    │  [ACL: WorkedHoursSummary]   │               │               │
    │                              │               │               │
    │  GET /leave-records          │               │               │
    ├──────────────────────────────┼──────────────►│               │
    │◄─────────────────────────────┼───────────────┤               │
    │  [ACL: PaidAbsence]          │               │               │
    │                              │               │               │
    │  ReviewCycleCompleted (이벤트, 평가 주기 종료 시)              │
    │◄─────────────────────────────┼───────────────┼───────────────┤
    │  [ACL: IncentiveGrade]       │               │               │
    │                              │               │               │
    ├──► PayrollCalculated         │               │               │
    ├──► PaySlipIssued             │               │               │
```

---

## 7. 멀티 테넌시 전략

| 계층 | 격리 전략 | 설명 |
|---|---|---|
| 데이터 | Schema-per-Tenant | 테넌트별 별도 스키마로 데이터 완전 격리 |
| 애플리케이션 | 공유 인스턴스 + TenantContext | 요청마다 TenantId를 주입하여 필터링 |
| 도메인 | Tenant-Scoped Aggregate | 모든 Aggregate Root가 TenantId를 포함 |

- 모든 Repository 호출은 TenantContext를 통해 자동으로 테넌트 필터가 적용된다.
- 테넌트 간 데이터 접근은 인프라 계층에서 원천 차단한다.

---

## 8. 설계 결정 근거

1. **Attendance와 Leave를 분리한 이유**: 근태 기록(출퇴근, 근무 시간)과 휴가(신청/승인 워크플로, 정책)는 변경 사유와 비즈니스 규칙이 다르다. 휴가 정책은 법규에 따라 자주 변경되지만 근태 기록 방식은 상대적으로 안정적이다.

2. **Payroll을 최하류(Downstream)에 배치한 이유**: 급여 계산은 근태, 휴가, 성과, 인사 정보를 모두 종합하는 최종 소비자다. 다른 BC에 영향을 주지 않으므로 독립적으로 변경 가능하다.

3. **Recruitment과 Employee Management를 분리한 이유**: 지원자(Applicant)와 직원(Employee)은 서로 다른 생명주기를 가진다. 채용 프로세스의 유비쿼터스 언어(파이프라인, 면접, 오퍼)와 인사 관리의 언어(부서, 직급, 조직도)가 명확히 다르다.

4. **ACL을 Downstream 측에 배치한 이유**: 각 BC가 자신의 도메인 모델을 보호하고, Upstream의 모델 변경이 자신의 핵심 도메인을 오염시키지 않도록 방어한다.
