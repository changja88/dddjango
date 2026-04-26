# LMS(온라인 학습 관리 시스템) 애그리거트 설계

## 식별된 애그리거트

### 1. Course (코스) 애그리거트

**Aggregate Root:** `Course`

**포함 엔티티/VO:**
- `Section` (엔티티) -- 코스 내 섹션
- `Lesson` (엔티티) -- 섹션 내 레슨
- `CourseStatus` (VO) -- Draft, Published, Archived

**구조:**
```
Course (AR)
├── courseId: CourseId
├── instructorId: InstructorId (다른 애그리거트 참조)
├── title: String
├── description: String
├── status: CourseStatus
├── sections: List<Section>
│   ├── sectionId: SectionId
│   ├── title: String
│   ├── orderIndex: int
│   └── lessons: List<Lesson>
│       ├── lessonId: LessonId
│       ├── title: String
│       ├── content: LessonContent
│       └── orderIndex: int
├── createdAt: DateTime
└── updatedAt: DateTime
```

**비즈니스 규칙:**
- 코스는 최소 1개의 섹션이 있어야 발행 가능
- 각 섹션은 최소 1개의 레슨이 있어야 함
- `publish()` 시 위 조건을 Course AR이 직접 검증

**설계 근거:**
- Section과 Lesson은 Course 없이 독립적으로 존재할 의미가 없다.
- "최소 1개 섹션, 섹션당 최소 1개 레슨" 불변식은 Course-Section-Lesson을 하나의 트랜잭션 경계로 묶어야 보장된다.
- Section이나 Lesson을 별도 애그리거트로 분리하면 발행 시점에 여러 애그리거트를 조회해야 하므로 불변식 보장이 어렵다.

---

### 2. Enrollment (수강 등록/진도) 애그리거트

**Aggregate Root:** `Enrollment`

**포함 엔티티/VO:**
- `LessonProgress` (엔티티) -- 레슨별 완료 여부
- `EnrollmentStatus` (VO) -- InProgress, Completed
- `CompletionRate` (VO) -- 진도율

**구조:**
```
Enrollment (AR)
├── enrollmentId: EnrollmentId
├── studentId: StudentId (다른 애그리거트 참조)
├── courseId: CourseId (다른 애그리거트 참조)
├── status: EnrollmentStatus
├── completionRate: CompletionRate
├── lessonProgresses: List<LessonProgress>
│   ├── lessonId: LessonId
│   ├── completed: boolean
│   └── completedAt: DateTime
├── enrolledAt: DateTime
└── completedAt: DateTime (nullable)
```

**비즈니스 규칙:**
- 수강생이 레슨을 완료하면 진도율이 자동 재계산됨
- 모든 레슨 완료 시 상태가 Completed로 변경되고 `CertificateIssuedEvent` 도메인 이벤트 발행

**설계 근거:**
- 진도율 계산은 "해당 수강생의 전체 레슨 완료 현황"을 알아야 하므로 LessonProgress들이 하나의 트랜잭션 경계 안에 있어야 한다.
- Course와 분리하는 이유: 수강 진도는 수강생마다 독립적이며, Course 수정과 수강 진도 업데이트는 동시성 충돌이 발생하면 안 된다. ID 참조로 느슨하게 연결한다.
- 수료증 발급은 Enrollment 상태 변경의 결과이므로, 도메인 이벤트를 통해 처리한다(별도 Certificate 애그리거트 또는 외부 서비스).

---

### 3. Question (질문/답변) 애그리거트

**Aggregate Root:** `Question`

**포함 엔티티/VO:**
- `Answer` (VO) -- 강사의 답변

**구조:**
```
Question (AR)
├── questionId: QuestionId
├── lessonId: LessonId (다른 애그리거트 참조)
├── courseId: CourseId (다른 애그리거트 참조)
├── studentId: StudentId (다른 애그리거트 참조)
├── content: String
├── answer: Answer (nullable)
│   ├── content: String
│   ├── instructorId: InstructorId
│   └── answeredAt: DateTime
├── status: QuestionStatus (Unanswered, Answered)
└── createdAt: DateTime
```

**비즈니스 규칙:**
- 수강생만 질문 가능 (Enrollment 존재 여부는 Application Service에서 확인)
- 해당 코스의 강사만 답변 가능

**설계 근거:**
- 질문/답변은 Course나 Enrollment의 불변식에 영향을 주지 않는다.
- 질문이 추가/수정되어도 Course의 섹션/레슨 구조나 수강 진도에 변화가 없다.
- 별도 애그리거트로 분리하면 Course 수정, 진도 업데이트, 질문 작성이 각각 독립적으로 발생할 수 있어 동시성 문제가 없다.
- Answer를 VO로 설계한 이유: 하나의 질문에 하나의 답변만 존재하며, 답변의 독립적인 생명주기가 필요하지 않다.

---

### 4. Review (수강 후기) 애그리거트

**Aggregate Root:** `Review`

**구조:**
```
Review (AR)
├── reviewId: ReviewId
├── courseId: CourseId (다른 애그리거트 참조)
├── studentId: StudentId (다른 애그리거트 참조)
├── rating: Rating (VO, 1~5)
├── content: String
├── createdAt: DateTime
└── updatedAt: DateTime
```

**비즈니스 규칙:**
- 한 수강생은 하나의 코스에 하나의 리뷰만 작성 가능 (유일성 제약)
- 수강 등록된 학생만 리뷰 작성 가능

**설계 근거:**
- 리뷰는 Course의 구조적 불변식(섹션/레슨 구성)과 무관하다.
- 리뷰가 추가되어도 Course 상태가 바뀌지 않는다.
- "수강생당 코스당 1개 리뷰" 유일성 제약은 DB 유니크 제약조건 또는 Application Service 레벨에서 처리한다.

---

## 애그리거트 간 관계 요약

```
┌──────────────┐
│    Course     │ ◄─── courseId로 참조
│  (AR)        │
│  ├─ Section  │
│  └─ Lesson   │
└──────────────┘
       ▲  courseId          ▲  courseId
       │                    │
┌──────────────┐    ┌──────────────┐
│  Enrollment  │    │   Question   │
│  (AR)        │    │   (AR)       │
│  ├─ Lesson   │    │   └─ Answer  │
│  │  Progress │    └──────────────┘
└──────────────┘
       ▲  courseId
       │
┌──────────────┐
│    Review    │
│    (AR)      │
└──────────────┘
```

**모든 애그리거트 간 참조는 ID 참조(간접 참조)를 사용한다.** 직접 객체 참조를 하지 않음으로써 각 애그리거트가 독립적인 트랜잭션 경계를 유지한다.

---

## 도메인 이벤트

| 이벤트 | 발행 주체 | 소비자 |
|--------|----------|--------|
| `CoursePublishedEvent` | Course | (알림 서비스 등) |
| `StudentEnrolledEvent` | Enrollment | (알림 서비스 등) |
| `LessonCompletedEvent` | Enrollment | (알림 서비스 등) |
| `CourseCompletedEvent` | Enrollment | Certificate 발급 서비스 |
| `QuestionPostedEvent` | Question | (강사 알림 등) |
| `AnswerPostedEvent` | Question | (수강생 알림 등) |
| `ReviewPostedEvent` | Review | (평균 별점 업데이트 등) |

---

## 핵심 설계 판단 정리

| 판단 | 결정 | 이유 |
|------|------|------|
| Section/Lesson을 Course에 포함 | 같은 애그리거트 | 발행 불변식(최소 1섹션, 섹션당 최소 1레슨)을 트랜잭션 내에서 보장해야 함 |
| Enrollment을 Course에서 분리 | 별도 애그리거트 | 수강생마다 독립 진도, Course 수정과 동시성 충돌 방지 |
| LessonProgress를 Enrollment에 포함 | 같은 애그리거트 | 진도율 계산 불변식을 트랜잭션 내에서 보장해야 함 |
| Question을 별도 분리 | 별도 애그리거트 | Course/Enrollment 불변식에 영향 없음, 독립적 생명주기 |
| Review를 별도 분리 | 별도 애그리거트 | Course 불변식에 영향 없음, 독립적 생명주기 |
| Certificate를 Enrollment 외부 처리 | 도메인 이벤트 | 수료증 발급은 부수 효과이며, Enrollment의 핵심 불변식이 아님 |
