# 온라인 학습 관리 시스템(LMS) 애그리거트 설계

## 1. 전략 설계

### 1.1 하위 도메인 식별

| 하위 도메인 | 유형 | 설명 |
|------------|------|------|
| 코스 관리 | 핵심(Core) | 강사가 코스를 생성/편집/발행하고, 커리큘럼(섹션/레슨)을 구성하는 영역. LMS의 핵심 가치 |
| 수강 및 학습 진도 | 핵심(Core) | 수강생의 등록, 레슨 완료, 진도율 추적, 수료증 발급. LMS의 핵심 경험 |
| Q&A(질의응답) | 지원(Supporting) | 수강생이 레슨에 대해 질문하고 강사가 답변하는 소통 영역 |
| 수강 후기 | 지원(Supporting) | 코스에 대한 리뷰를 남기는 CRUD 수준의 영역 |
| 인증/사용자 관리 | 일반(Generic) | 강사/수강생의 계정 관리, 로그인. 외부 솔루션 활용 가능 |

### 1.2 바운디드 컨텍스트

| 바운디드 컨텍스트 | 대응 하위 도메인 | 핵심 유비쿼터스 언어 |
|-----------------|-----------------|-------------------|
| **코스 관리 컨텍스트** | 코스 관리 | 코스, 섹션, 레슨, 발행, 강사 |
| **학습 컨텍스트** | 수강 및 학습 진도 | 수강 등록, 레슨 완료, 진도율, 수료증 |
| **Q&A 컨텍스트** | Q&A | 질문, 답변 |
| **리뷰 컨텍스트** | 수강 후기 | 리뷰, 평점 |

> 같은 "코스"라는 용어가 코스 관리 컨텍스트에서는 "강사가 편집하고 발행하는 커리큘럼 단위"를, 학습 컨텍스트에서는 "수강생이 등록하여 진행하는 학습 대상"을 의미한다. 이 의미의 분기점이 바운디드 컨텍스트 경계다.

### 1.3 컨텍스트 맵

```
[코스 관리 컨텍스트] ──(OHS/PL)──> [학습 컨텍스트]
       │                                 │
       │                                 ├──(OHS/PL)──> [리뷰 컨텍스트]
       │                                 │
       └──(OHS/PL)──> [Q&A 컨텍스트] <───┘
```

- **코스 관리 -> 학습**: 업스트림-다운스트림 (고객-공급자). 코스가 발행되면 학습 컨텍스트에서 수강 등록이 가능해진다.
- **코스 관리 -> Q&A**: 업스트림-다운스트림. Q&A 컨텍스트는 코스/레슨의 ID만 참조한다.
- **학습 -> 리뷰**: 업스트림-다운스트림. 수강 이력이 있어야 리뷰를 남길 수 있다.

---

## 2. 전술 설계: 애그리거트 식별

### 2.1 애그리거트 도출 근거

Vernon의 4가지 규칙을 기준으로 각 애그리거트를 식별한다.

#### 규칙 1 적용 -- 진정한 불변식을 일관성 경계 안에서 보호하라

어떤 비즈니스 규칙이 반드시 하나의 트랜잭션 안에서 함께 지켜져야 하는가?

- "코스는 최소 1개의 섹션이 있어야 발행할 수 있다" -> 코스와 섹션은 발행 시점에 함께 검증되어야 한다.
- "각 섹션은 최소 1개의 레슨이 있어야 한다" -> 섹션과 레슨은 함께 검증되어야 한다.
- "수강생이 레슨을 완료하면 진도율이 업데이트된다" -> 레슨 완료 기록과 진도율은 하나의 트랜잭션에서 갱신되어야 한다.
- "모든 레슨을 완료하면 수료증이 발급된다" -> 진도율 100% 판단과 수료증 발급은 동일 트랜잭션일 필요가 없다. 결과적 일관성으로 충분하다.

#### 규칙 2 적용 -- 작은 애그리거트를 설계하라

하나의 큰 "Course" 애그리거트에 섹션, 레슨, 수강 이력, Q&A, 리뷰를 모두 넣으면 수천 건의 데이터를 로딩해야 하고, 동시성 충돌이 빈번해진다. 관심사별로 분리한다.

#### 규칙 3 적용 -- 다른 애그리거트는 ID로만 참조하라

수강 등록(Enrollment)은 코스 객체를 직접 참조하지 않고, `course_id`로만 참조한다.

#### 규칙 4 적용 -- 일관성 경계 밖에서는 결과적 일관성을 사용하라

"모든 레슨 완료 -> 수료증 발급"은 도메인 이벤트를 통한 결과적 일관성으로 처리한다.

---

### 2.2 애그리거트 정의

#### 애그리거트 1: Course (코스 관리 컨텍스트)

| 구성요소 | 유형 | 설명 |
|---------|------|------|
| `Course` | 애그리거트 루트 (엔티티) | 코스의 생명주기를 관리 |
| `Section` | 엔티티 | 코스 내부의 섹션. Course를 통해서만 접근 |
| `Lesson` | 엔티티 | 섹션 내부의 레슨. Section을 통해서만 접근 |
| `CourseStatus` | 값 객체 | DRAFT, PUBLISHED, ARCHIVED |

**불변식:**
- 코스는 최소 1개의 섹션이 있어야 발행할 수 있다.
- 각 섹션은 최소 1개의 레슨이 있어야 한다.
- 발행된 코스의 섹션/레슨 구조 변경 시 유효성을 재검증해야 한다.

**Section과 Lesson을 Course 안에 포함하는 이유:**
발행 규칙("최소 1개의 섹션, 각 섹션에 최소 1개의 레슨")은 Course가 publish()될 때 Course-Section-Lesson을 함께 검증해야 하는 진정한 불변식이다. 섹션이나 레슨이 별도 애그리거트라면 이 불변식을 트랜잭션 안에서 보장할 수 없다.

**규모에 대한 판단:**
코스 하나에 섹션은 보통 5~20개, 레슨은 섹션당 5~15개 수준이다. 수백~수천 건이 아니므로 하나의 애그리거트로 묶어도 성능 문제가 없다. 이것은 "작은 애그리거트를 설계하라"는 규칙에 부합한다 -- 작다는 것은 불변식 유지에 필요한 최소치를 의미하지, 무조건 1개의 엔티티만을 의미하지 않는다.

```python
@dataclass
class Lesson:
    id: str
    title: str
    content_url: str
    order: int

@dataclass
class Section:
    id: str
    title: str
    order: int
    _lessons: list[Lesson] = field(default_factory=list)

    def add_lesson(self, lesson: Lesson) -> None:
        self._lessons.append(lesson)

    @property
    def lesson_count(self) -> int:
        return len(self._lessons)

    @property
    def lesson_ids(self) -> list[str]:
        return [lesson.id for lesson in self._lessons]

class CourseStatus(Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

@dataclass
class Course:
    """코스 애그리거트 루트"""
    id: str
    instructor_id: str  # 강사를 ID로 참조 (규칙 3)
    title: str
    description: str
    _sections: list[Section] = field(default_factory=list)
    _status: CourseStatus = CourseStatus.DRAFT
    _events: list = field(default_factory=list)

    def add_section(self, section: Section) -> None:
        if self._status == CourseStatus.PUBLISHED:
            raise ValueError("발행된 코스에는 섹션을 추가한 후 재검증이 필요합니다")
        self._sections.append(section)

    def publish(self) -> None:
        """발행 -- 불변식을 검증한다"""
        if not self._sections:
            raise ValueError("최소 1개의 섹션이 있어야 발행할 수 있습니다")
        for section in self._sections:
            if section.lesson_count == 0:
                raise ValueError(f"섹션 '{section.title}'에 최소 1개의 레슨이 필요합니다")
        self._status = CourseStatus.PUBLISHED
        self._events.append(CoursePublishedEvent(
            course_id=self.id,
            total_lesson_count=self.total_lesson_count,
        ))

    @property
    def total_lesson_count(self) -> int:
        return sum(s.lesson_count for s in self._sections)

    @property
    def all_lesson_ids(self) -> list[str]:
        result = []
        for section in self._sections:
            result.extend(section.lesson_ids)
        return result

    def collect_domain_events(self) -> list:
        events = list(self._events)
        self._events.clear()
        return events
```

---

#### 애그리거트 2: Enrollment (학습 컨텍스트)

| 구성요소 | 유형 | 설명 |
|---------|------|------|
| `Enrollment` | 애그리거트 루트 (엔티티) | 수강 등록과 진도 추적의 생명주기 |
| `LessonCompletion` | 값 객체 | 완료된 개별 레슨 기록 (레슨ID + 완료 시각) |
| `Progress` | 값 객체 | 진도율 (완료 레슨 수 / 전체 레슨 수) |

**불변식:**
- 같은 레슨을 중복 완료 처리할 수 없다.
- 진도율은 레슨 완료 시 즉시 정확하게 반영되어야 한다 (강한 일관성).

**Enrollment을 Course와 분리하는 이유:**
수강 이력은 코스 커리큘럼과 다른 생명주기를 가진다. 코스 하나에 수천 명이 등록할 수 있으므로 Course 안에 넣으면 Vernon 규칙 2를 위반한다. 또한 "수강 진도"와 "커리큘럼 편집"은 서로 다른 불변식이다.

**수료증 발급은 이 애그리거트에서 직접 처리하지 않는 이유:**
수료증 발급은 별도의 관심사(인쇄 가능한 문서 생성, 고유 번호 부여 등)이므로, 도메인 이벤트 `AllLessonsCompletedEvent`를 발행하고 결과적 일관성으로 처리한다 (규칙 4).

```python
@dataclass(frozen=True)
class LessonCompletion:
    """값 객체 -- 레슨 완료 기록"""
    lesson_id: str
    completed_at: datetime

@dataclass(frozen=True)
class Progress:
    """값 객체 -- 진도율"""
    completed_count: int
    total_count: int

    @property
    def percentage(self) -> float:
        if self.total_count == 0:
            return 0.0
        return (self.completed_count / self.total_count) * 100

    @property
    def is_all_completed(self) -> bool:
        return self.total_count > 0 and self.completed_count == self.total_count

@dataclass
class Enrollment:
    """수강 등록 애그리거트 루트"""
    id: str
    student_id: str     # 수강생을 ID로 참조 (규칙 3)
    course_id: str      # 코스를 ID로 참조 (규칙 3)
    _total_lesson_count: int
    _completions: list[LessonCompletion] = field(default_factory=list)
    _enrolled_at: datetime = field(default_factory=datetime.now)
    _events: list = field(default_factory=list)

    def complete_lesson(self, lesson_id: str) -> None:
        """레슨 완료 처리 -- 불변식(중복 방지)을 보호한다"""
        if self._is_already_completed(lesson_id):
            raise ValueError(f"레슨 {lesson_id}은 이미 완료되었습니다")
        self._completions.append(LessonCompletion(
            lesson_id=lesson_id,
            completed_at=datetime.now(),
        ))
        if self.progress.is_all_completed:
            self._events.append(AllLessonsCompletedEvent(
                enrollment_id=self.id,
                student_id=self.student_id,
                course_id=self.course_id,
            ))

    def _is_already_completed(self, lesson_id: str) -> bool:
        return any(c.lesson_id == lesson_id for c in self._completions)

    @property
    def progress(self) -> Progress:
        return Progress(
            completed_count=len(self._completions),
            total_count=self._total_lesson_count,
        )

    def collect_domain_events(self) -> list:
        events = list(self._events)
        self._events.clear()
        return events
```

---

#### 애그리거트 3: Certificate (학습 컨텍스트)

| 구성요소 | 유형 | 설명 |
|---------|------|------|
| `Certificate` | 애그리거트 루트 (엔티티) | 수료증의 생명주기 |
| `CertificateNumber` | 값 객체 | 고유 수료증 번호 |

**별도 애그리거트로 분리하는 이유:**
수료증은 한 번 발급되면 변경되지 않는 별도의 생명주기를 가진다. Enrollment의 진도 추적과는 다른 관심사(번호 체계, 발급일, 검증)를 가진다. `AllLessonsCompletedEvent`를 구독하여 결과적 일관성으로 생성된다 (규칙 4).

```python
@dataclass(frozen=True)
class CertificateNumber:
    """값 객체 -- 수료증 고유 번호"""
    value: str

@dataclass
class Certificate:
    """수료증 애그리거트 루트"""
    id: str
    certificate_number: CertificateNumber
    student_id: str      # ID 참조 (규칙 3)
    course_id: str       # ID 참조 (규칙 3)
    enrollment_id: str   # ID 참조 (규칙 3)
    issued_at: datetime
```

---

#### 애그리거트 4: Question (Q&A 컨텍스트)

| 구성요소 | 유형 | 설명 |
|---------|------|------|
| `Question` | 애그리거트 루트 (엔티티) | 질문의 생명주기 |
| `Answer` | 엔티티 | Question 내부의 답변 |

**불변식:**
- 질문 하나에 강사의 답변이 달릴 수 있다.

**Question과 Answer를 하나의 애그리거트로 묶는 이유:**
하나의 질문에 대한 답변은 보통 1~수개 수준이며, 질문과 답변은 함께 조회되고 함께 의미를 가진다. 답변 수가 대량이 되지 않으므로 하나의 애그리거트로 묶어도 규칙 2를 위반하지 않는다.

**Question을 Course 안에 넣지 않는 이유:**
하나의 코스에 수백~수천 개의 질문이 달릴 수 있다. Course 애그리거트에 포함시키면 규칙 2를 위반한다. 또한 질문/답변은 커리큘럼 구조와 다른 불변식을 가진다.

```python
@dataclass
class Answer:
    """엔티티 -- 강사의 답변"""
    id: str
    instructor_id: str  # ID 참조 (규칙 3)
    content: str
    answered_at: datetime

@dataclass
class Question:
    """질문 애그리거트 루트"""
    id: str
    course_id: str      # ID 참조 (규칙 3)
    lesson_id: str      # ID 참조 (규칙 3)
    student_id: str     # ID 참조 (규칙 3)
    title: str
    content: str
    _answer: Answer | None = None
    _asked_at: datetime = field(default_factory=datetime.now)

    def add_answer(self, answer: Answer) -> None:
        """강사가 답변을 추가한다"""
        if self._answer is not None:
            raise ValueError("이미 답변이 등록되어 있습니다")
        self._answer = answer

    @property
    def is_answered(self) -> bool:
        return self._answer is not None
```

---

#### 애그리거트 5: Review (리뷰 컨텍스트)

| 구성요소 | 유형 | 설명 |
|---------|------|------|
| `Review` | 애그리거트 루트 (엔티티) | 수강 후기의 생명주기 |
| `Rating` | 값 객체 | 평점 (1~5) |

**별도 애그리거트로 분리하는 이유:**
리뷰는 Course나 Enrollment과 다른 생명주기를 가진다. 코스 하나에 수천 개의 리뷰가 달릴 수 있으므로 Course에 포함시키면 규칙 2를 위반한다. 이것은 reference의 `Product`와 `ProductReview` 분리 예시와 동일한 패턴이다.

```python
@dataclass(frozen=True)
class Rating:
    """값 객체 -- 평점"""
    value: int

    def __post_init__(self):
        if not 1 <= self.value <= 5:
            raise ValueError(f"평점은 1~5 사이여야 합니다: {self.value}")

@dataclass
class Review:
    """수강 후기 애그리거트 루트"""
    id: str
    course_id: str       # ID 참조 (규칙 3)
    student_id: str      # ID 참조 (규칙 3)
    enrollment_id: str   # ID 참조 (규칙 3)
    rating: Rating
    content: str
    _created_at: datetime = field(default_factory=datetime.now)
```

---

## 3. 도메인 이벤트와 애그리거트 간 연결

애그리거트 간의 연결은 도메인 이벤트를 통한 결과적 일관성으로 처리한다 (Vernon 규칙 4).

### 이벤트 흐름

```
[Course]                     [Enrollment]                  [Certificate]
   │                              │                             │
   ├─ CoursePublishedEvent        │                             │
   │  (수강 등록 가능 상태)         │                             │
   │                              │                             │
   │                              ├─ AllLessonsCompletedEvent   │
   │                              │  ───────────────────────> 수료증 생성
   │                              │                             │
```

### 이벤트 정의

```python
@dataclass(frozen=True)
class CoursePublishedEvent:
    """코스가 발행되었을 때 발생"""
    course_id: str
    total_lesson_count: int
    occurred_at: datetime = field(default_factory=datetime.now)

@dataclass(frozen=True)
class AllLessonsCompletedEvent:
    """수강생이 모든 레슨을 완료했을 때 발생"""
    enrollment_id: str
    student_id: str
    course_id: str
    occurred_at: datetime = field(default_factory=datetime.now)
```

---

## 4. 애그리거트 설계 요약

| 애그리거트 | 바운디드 컨텍스트 | 루트 엔티티 | 내부 엔티티 | 값 객체 | 리포지토리 |
|-----------|-----------------|-----------|-----------|--------|-----------|
| Course | 코스 관리 | Course | Section, Lesson | CourseStatus | CourseRepository |
| Enrollment | 학습 | Enrollment | -- | LessonCompletion, Progress | EnrollmentRepository |
| Certificate | 학습 | Certificate | -- | CertificateNumber | CertificateRepository |
| Question | Q&A | Question | Answer | -- | QuestionRepository |
| Review | 리뷰 | Review | -- | Rating | ReviewRepository |

### ID 참조 관계 (Vernon 규칙 3)

```
Course.instructor_id ─────────────> (사용자 컨텍스트)
Enrollment.student_id ────────────> (사용자 컨텍스트)
Enrollment.course_id ─────────────> Course
Certificate.student_id ───────────> (사용자 컨텍스트)
Certificate.course_id ────────────> Course
Certificate.enrollment_id ────────> Enrollment
Question.course_id ───────────────> Course
Question.lesson_id ───────────────> (Course 내부의 Lesson)
Question.student_id ──────────────> (사용자 컨텍스트)
Review.course_id ─────────────────> Course
Review.student_id ────────────────> (사용자 컨텍스트)
Review.enrollment_id ─────────────> Enrollment
```

### 설계 판단 근거 요약

| 판단 | 근거 |
|------|------|
| Section/Lesson을 Course 안에 포함 | 발행 불변식("최소 1섹션, 각 섹션에 최소 1레슨")은 진정한 불변식이다 (규칙 1). 섹션/레슨 수가 수십~수백 수준으로 소규모이다 (규칙 2 준수) |
| Enrollment을 Course와 분리 | 수강생 수는 수천 명까지 가능하므로 Course에 포함 시 규칙 2 위반. 커리큘럼 편집과 수강 진도는 서로 다른 불변식 |
| Certificate를 Enrollment과 분리 | 수료증은 발급 후 불변이며, 진도 추적과 다른 생명주기. 결과적 일관성으로 생성 (규칙 4) |
| Question을 별도 애그리거트로 분리 | 코스당 수백~수천 질문 가능하므로 Course에 포함 시 규칙 2 위반. Q&A는 별도 바운디드 컨텍스트 |
| Review를 별도 애그리거트로 분리 | Product-ProductReview 분리 패턴과 동일. 코스당 리뷰 수가 대량 가능 (규칙 2) |
| 수료증 발급을 결과적 일관성으로 처리 | "모든 레슨 완료"와 "수료증 생성"은 서로 다른 애그리거트의 관심사이므로 도메인 이벤트로 연결 (규칙 4) |
