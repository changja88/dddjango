# 학원 관리 대시보드 리팩토링

## 변경 1: N+1 쿼리 제거 -- select_related / prefetch_related 적용

```
[Before]
students = Student.objects.all()
data = []
for student in students:
    enrollments = Enrollment.objects.filter(student=student)
    courses = [e.course.name for e in enrollments]
    total_fee = sum(e.course.fee for e in enrollments)
    data.append({
        'name': student.name,
        'classroom': student.classroom.name,
        'teacher': student.classroom.teacher.username,
        'courses': courses,
        'total_fee': total_fee,
    })

[After]
students = (
    Student.objects
    .select_related("classroom__teacher")
    .prefetch_related(
        Prefetch(
            "enrollment_set",
            queryset=Enrollment.objects.select_related("course"),
        )
    )
)

[Reason] QuerySet 최적화 필수 패턴 -- 원본 코드는 학생 N명에 대해 (1) student.classroom 접근 시 Classroom 쿼리 N회, (2) student.classroom.teacher 접근 시 User 쿼리 N회, (3) Enrollment.objects.filter(student=student) 쿼리 N회, (4) e.course 접근 시 Course 쿼리가 수강 건마다 발생한다. 학생 1,000명이 평균 3개 수강이면 약 1 + 1000 + 1000 + 1000 + 3000 = 6,001회 쿼리가 발생한다. select_related("classroom__teacher")로 FK 체인을 JOIN 1회로 해결하고, prefetch_related + Prefetch 객체로 enrollment와 course를 2회 쿼리로 해결하여 총 3회로 줄인다.
```

## 변경 2: 루프 내 개별 쿼리 제거 -- annotate()로 DB 레벨 집계

```
[Before]
for student in students:
    enrollments = Enrollment.objects.filter(student=student)
    total_fee = sum(e.course.fee for e in enrollments)

[After]
from django.db.models import Sum

students = (
    Student.objects
    .select_related("classroom__teacher")
    .prefetch_related(
        Prefetch(
            "enrollment_set",
            queryset=Enrollment.objects.select_related("course"),
        )
    )
    .annotate(total_fee=Sum("enrollment__course__fee"))
)

[Reason] annotate()와 aggregate() -- Python 레벨에서 sum()으로 합산하면 모든 Enrollment와 Course 객체를 메모리에 올려야 한다. annotate(total_fee=Sum(...))를 사용하면 DB가 집계를 수행하므로 네트워크 전송량과 Python 처리 비용이 모두 줄어든다.
```

## 변경 3: FloatField를 DecimalField로 변경 -- 금액 정밀도 보장

```
[Before]
class Course(models.Model):
    name = models.CharField(max_length=100)
    fee = models.FloatField()

[After]
class Course(models.Model):
    name = models.CharField(max_length=100)
    fee = models.DecimalField(max_digits=10, decimal_places=2)

[Reason] 필드 선택 가이드 -- FloatField는 IEEE 754 부동소수점으로 저장되어 금액 계산 시 정밀도 오류가 발생한다 (예: 0.1 + 0.2 != 0.3). 수강료처럼 금전 데이터에는 반드시 DecimalField를 사용한다.
```

## 변경 4: Fat View를 Thin View로 -- 조회 로직을 셀렉터로 추출

```
[Before]
class DashboardView(View):
    def get(self, request):
        students = Student.objects.all()
        data = []
        for student in students:
            enrollments = Enrollment.objects.filter(student=student)
            courses = [e.course.name for e in enrollments]
            total_fee = sum(e.course.fee for e in enrollments)
            data.append({
                'name': student.name,
                'classroom': student.classroom.name,
                'teacher': student.classroom.teacher.username,
                'courses': courses,
                'total_fee': total_fee,
            })
        return JsonResponse({'students': data})

[After]
# selectors.py
def student_dashboard_list():
    """대시보드용 학생 목록을 반환한다."""
    return (
        Student.objects
        .select_related("classroom__teacher")
        .prefetch_related(
            Prefetch(
                "enrollment_set",
                queryset=Enrollment.objects.select_related("course"),
            )
        )
        .annotate(total_fee=Sum("enrollment__course__fee"))
    )

# views.py
class DashboardView(View):
    def get(self, request):
        students = student_dashboard_list()
        data = [
            {
                "name": student.name,
                "classroom": student.classroom.name,
                "teacher": student.classroom.teacher.username,
                "courses": [e.course.name for e in student.enrollment_set.all()],
                "total_fee": student.total_fee or 0,
            }
            for student in students
        ]
        return JsonResponse({"students": data})

[Reason] Fat Model, Thin View + 서비스/셀렉터 패턴 -- 뷰에 쿼리 구성 로직이 포함되면 재사용이 불가능하고 테스트가 어렵다. 읽기 전용 쿼리 로직은 selectors.py에 <entity>_<action> 네이밍으로 분리하여, 뷰는 데이터 직렬화와 응답 구성만 담당하게 한다.
```

## 변경 5: 모델에 __str__ 및 related_name 추가

```
[Before]
class Student(models.Model):
    name = models.CharField(max_length=100)
    grade = models.IntegerField()
    classroom = models.ForeignKey('Classroom', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)

[After]
class Student(models.Model):
    name = models.CharField(max_length=100)
    grade = models.IntegerField()
    classroom = models.ForeignKey(
        "Classroom",
        on_delete=models.CASCADE,
        related_name="students",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

class Enrollment(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    course = models.ForeignKey(
        "Course",
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "course"],
                name="unique_student_course",
            ),
        ]

    def __str__(self):
        return f"{self.student.name} - {self.course.name}"

[Reason] 모델 코딩 스타일 + 모델 유효성 검증 -- (1) __str__은 admin, 디버깅, 로그에서 객체를 식별하는 기본 수단이므로 반드시 정의한다. (2) related_name을 명시하면 역참조 시 가독성이 높아진다 (student.enrollment_set보다 student.enrollments가 명확). (3) 동일 학생이 같은 과목에 중복 등록되는 것은 비즈니스 논리상 불가능하므로 UniqueConstraint로 DB 레벨에서 방어한다.
```

## 변경 6: db_default 적용 -- Django 5.x 기능 활용

```
[Before]
created_at = models.DateTimeField(auto_now_add=True)
enrolled_at = models.DateTimeField(auto_now_add=True)

[After]
from django.db.models.functions import Now

created_at = models.DateTimeField(db_default=Now())
enrolled_at = models.DateTimeField(db_default=Now())

[Reason] Django 5.x 새 기능 (db_default) -- auto_now_add는 Python 레벨에서 시간을 설정하여 bulk_create 시 동작하지 않을 수 있다. db_default=Now()는 DB DEFAULT 절에 포함되어 bulk_create에서도 올바르게 동작하며, DB 서버 시간을 사용하므로 앱 서버 시간 불일치 문제도 방지한다.
```

---

## 전체 리팩토링 결과

```python
# models.py
from django.db import models
from django.db.models.functions import Now


class Classroom(models.Model):
    name = models.CharField(max_length=50)
    teacher = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="classrooms",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Student(models.Model):
    name = models.CharField(max_length=100)
    grade = models.IntegerField()
    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.CASCADE,
        related_name="students",
    )
    created_at = models.DateTimeField(db_default=Now())

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Course(models.Model):
    name = models.CharField(max_length=100)
    fee = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Enrollment(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    enrolled_at = models.DateTimeField(db_default=Now())

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "course"],
                name="unique_student_course",
            ),
        ]

    def __str__(self):
        return f"{self.student.name} - {self.course.name}"
```

```python
# selectors.py
from django.db.models import Prefetch, Sum

from .models import Enrollment, Student


def student_dashboard_list():
    """대시보드용 학생 목록을 최적화된 쿼리로 반환한다."""
    return (
        Student.objects
        .select_related("classroom__teacher")
        .prefetch_related(
            Prefetch(
                "enrollments",
                queryset=Enrollment.objects.select_related("course"),
            )
        )
        .annotate(total_fee=Sum("enrollments__course__fee"))
    )
```

```python
# views.py
from django.http import JsonResponse
from django.views import View

from .selectors import student_dashboard_list


class DashboardView(View):
    def get(self, request):
        students = student_dashboard_list()
        data = [
            {
                "name": student.name,
                "classroom": student.classroom.name,
                "teacher": student.classroom.teacher.username,
                "courses": [
                    enrollment.course.name
                    for enrollment in student.enrollments.all()
                ],
                "total_fee": student.total_fee or 0,
            }
            for student in students
        ]
        return JsonResponse({"students": data})
```

```python
# tests.py
from django.test import TestCase

from .selectors import student_dashboard_list


class DashboardQueryTest(TestCase):
    def test_dashboard_query_count(self):
        """학생 수와 무관하게 쿼리 수가 일정한지 검증한다."""
        self._create_test_data(student_count=100, courses_per_student=3)
        # 3회: students+classroom+teacher JOIN / enrollments IN / courses IN
        with self.assertNumQueries(3):
            list(student_dashboard_list())
```
