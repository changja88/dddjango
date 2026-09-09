from django.http import HttpResponse
from django.urls import include, path
def favicon(request):
    return HttpResponse(status=204)
urlpatterns = [path("favicon.ico", favicon), path("", include("web.urls"))]
