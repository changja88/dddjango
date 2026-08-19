from ninja import Router, Status
from application.lesson.application_layer.use_cases import LessonMissing, get_lesson
from application.lesson.driving_layer.api.bc_error_schema import LessonNotFoundError

router = Router()


@router.get("/{lesson_id}", response={200: dict, 404: LessonNotFoundError})
def get_lesson_controller(request, lesson_id: int):
    try:
        lesson = get_lesson(lesson_id)
    except LessonMissing:
        error = LessonNotFoundError()
        return Status(error.status, error)
    return lesson
