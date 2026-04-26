import factory
from factory.django import DjangoModelFactory

from .models import Course, Enrollment, Instructor, Review


class InstructorFactory(DjangoModelFactory):
    class Meta:
        model = Instructor

    name = factory.Sequence(lambda n: f"Instructor {n}")
    bio = factory.Faker("paragraph")


class CourseFactory(DjangoModelFactory):
    class Meta:
        model = Course

    title = factory.Sequence(lambda n: f"Course {n}")
    description = factory.Faker("paragraph")
    instructor = factory.SubFactory(InstructorFactory)
    status = Course.Status.DRAFT

    class Params:
        published = factory.Trait(status=Course.Status.PUBLISHED)


class EnrollmentFactory(DjangoModelFactory):
    class Meta:
        model = Enrollment

    student_name = factory.Sequence(lambda n: f"student{n}")
    course = factory.SubFactory(CourseFactory, published=True)


class ReviewFactory(DjangoModelFactory):
    class Meta:
        model = Review

    course = factory.SubFactory(CourseFactory, published=True)
    reviewer_name = factory.Sequence(lambda n: f"reviewer{n}")
    rating = factory.Faker("random_int", min=1, max=5)
    comment = factory.Faker("sentence")
