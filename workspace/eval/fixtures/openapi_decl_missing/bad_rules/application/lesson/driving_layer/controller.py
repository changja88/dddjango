from ninja import Router, Status
from application.lesson.driving_layer.api.bc_error_schema import LessonConflictError, LessonErrorSchema, LessonNotFoundError

router = Router()


@router.get("/{lesson_id}", response={200: dict, 404: LessonNotFoundError})
def get_lesson(request, lesson_id: int):
    if lesson_id == 0:
        error = LessonNotFoundError()
        return Status(error.status, error)
    if lesson_id < 0:
        error = LessonConflictError()
        return Status(error.status, error)
    return {"id": lesson_id}
