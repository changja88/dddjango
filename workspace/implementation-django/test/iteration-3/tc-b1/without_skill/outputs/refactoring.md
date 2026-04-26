# 학원 관리 대시보드 리팩토링

## 성능 문제 분석

### 발견된 문제점

**1. N+1 쿼리 문제 (치명적)**

`Student.objects.all()`로 전체 학생을 가져온 후, 루프 안에서 학생마다 `Enrollment.objects.filter(student=student)`를 호출한다. 학생이 3,000명이면 최소 3,001번의 DB 쿼리가 발생한다.

**2. 중첩 N+1 쿼리**

`e.course.name`, `e.course.fee`에서 각 수강 등록마다 Course 테이블을 추가 조회한다. 학생당 평균 3개 수강이면 약 9,000번의 추가 쿼리가 발생한다.

**3. ForeignKey 역참조 N+1**

`student.classroom.name`, `student.classroom.teacher.username`에서 학생마다 Classroom과 User 테이블을 각각 조회한다. 이것만으로도 6,000번의 추가 쿼리가 발생한다.

**4. `FloatField` 사용**

금액(`fee`)에 `FloatField`를 사용하면 부동소수점 오차가 발생한다. 수강료 합산 시 정확하지 않은 결과가 나올 수 있다.

**총 쿼리 수 추산 (학생 3,000명, 학생당 수강 3개 기준):**
- 학생 전체 조회: 1
- 학생당 Enrollment 조회: 3,000
- 수강당 Course 조회: 9,000
- 학생당 Classroom 조회: 3,000
- 학생당 Teacher(User) 조회: 3,000
- **합계: 약 18,001 쿼리**

---

## 리팩토링 결과

### 모델 수정

```python
class Student(models.Model):
    name = models.CharField(max_length=100)
    grade = models.IntegerField()
    classroom = models.ForeignKey('Classroom', on_delete=models.CASCADE, related_name='students')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['classroom']),
            models.Index(fields=['grade']),
        ]

class Classroom(models.Model):
    name = models.CharField(max_length=50)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='classrooms')

class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['student']),
            models.Index(fields=['student', 'course']),
        ]

class Course(models.Model):
    name = models.CharField(max_length=100)
    fee = models.DecimalField(max_digits=10, decimal_places=2)
```

### 뷰 수정

```python
from django.db.models import Prefetch, Sum, F
from django.http import JsonResponse
from django.views import View


class DashboardView(View):
    def get(self, request):
        students = (
            Student.objects
            .select_related('classroom', 'classroom__teacher')
            .prefetch_related(
                Prefetch(
                    'enrollments',
                    queryset=Enrollment.objects.select_related('course'),
                )
            )
            .annotate(total_fee=Sum('enrollments__course__fee'))
        )

        data = []
        for student in students:
            courses = [e.course.name for e in student.enrollments.all()]
            data.append({
                'name': student.name,
                'classroom': student.classroom.name,
                'teacher': student.classroom.teacher.username,
                'courses': courses,
                'total_fee': float(student.total_fee or 0),
            })

        return JsonResponse({'students': data})
```

---

## 적용된 기법 설명

### 1. `select_related` -- FK 정참조 조인

```python
.select_related('classroom', 'classroom__teacher')
```

Student -> Classroom -> User(teacher) 관계를 SQL JOIN으로 한 번에 가져온다. 기존에 학생당 2번씩 발생하던 쿼리(Classroom 1회 + User 1회)가 완전히 제거된다.

### 2. `prefetch_related` + `Prefetch` -- 역참조 일괄 조회

```python
.prefetch_related(
    Prefetch(
        'enrollments',
        queryset=Enrollment.objects.select_related('course'),
    )
)
```

학생별로 개별 실행되던 Enrollment 조회를 `WHERE student_id IN (...)` 단일 쿼리로 변환한다. `Prefetch` 객체 내부에서 `select_related('course')`를 걸어 Course 조회도 동일 쿼리에 조인시킨다.

### 3. `annotate` + `Sum` -- DB 레벨 집계

```python
.annotate(total_fee=Sum('enrollments__course__fee'))
```

파이썬 루프에서 `sum()`으로 계산하던 수강료 합산을 SQL `SUM()`으로 대체한다. DB 엔진이 직접 계산하므로 데이터 전송량도 줄어든다.

### 4. `related_name` 명시

```python
classroom = models.ForeignKey('Classroom', on_delete=models.CASCADE, related_name='students')
```

역참조 이름을 명시적으로 지정하여 코드 가독성을 높이고, `prefetch_related`에서 사용할 관계명을 명확히 한다.

### 5. `DecimalField` 전환

```python
fee = models.DecimalField(max_digits=10, decimal_places=2)
```

금액 필드를 `FloatField`에서 `DecimalField`로 변경하여 부동소수점 오차를 방지한다.

### 6. DB 인덱스 추가

```python
class Meta:
    indexes = [
        models.Index(fields=['student', 'course']),
    ]
```

자주 조회되는 FK 컬럼에 인덱스를 추가하여 JOIN과 필터링 성능을 개선한다.

---

## 쿼리 수 비교

| 항목 | 리팩토링 전 | 리팩토링 후 |
|------|------------|------------|
| 학생 조회 | 1 | 1 |
| Classroom 조회 | N | 0 (JOIN) |
| Teacher 조회 | N | 0 (JOIN) |
| Enrollment 조회 | N | 1 (IN 절) |
| Course 조회 | N * M | 0 (JOIN) |
| 수강료 합산 | Python 루프 | 0 (SQL SUM) |
| **총 쿼리 수 (N=3000, M=3)** | **~18,001** | **2** |
