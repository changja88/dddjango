class LessonMissing(Exception):
    pass


def get_lesson(lesson_id: int):
    return {"id": lesson_id}
