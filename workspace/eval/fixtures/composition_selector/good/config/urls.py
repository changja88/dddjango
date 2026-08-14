from config.api import api
from application.lesson.driving_layer.api.api_router import register_lesson_api
from application.catalog.driving_layer.api.api_router import register_catalog_api

register_lesson_api(api)
register_catalog_api(api)
urlpatterns = []
