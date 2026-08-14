from .controller import LessonController

def register_lesson_api(api):
    api.register_controllers(LessonController)
