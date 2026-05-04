현재 디렉터리에 `config.toml`이나 Django 파일이 없고, 세션이 읽기 전용이라 파일 생성은 할 수 없습니다. 대신 바로 붙여 넣을 수 있는 예제를 제공합니다.

`serializers.py`

```python
from rest_framework import serializers


class ArticleSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=200)
    content = serializers.CharField()
    author = serializers.CharField(max_length=100)
    created_at = serializers.DateTimeField(read_only=True)

    def validate_title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("제목은 3자 이상이어야 합니다.")
        return value
```

`views.py`

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import ArticleSerializer


ARTICLES = []


class ArticleListAPIView(APIView):
    def get(self, request):
        serializer = ArticleSerializer(ARTICLES, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ArticleSerializer(data=request.data)

        if serializer.is_valid():
            article = {
                "id": len(ARTICLES) + 1,
                **serializer.validated_data,
            }
            ARTICLES.append(article)

            return Response(
                ArticleSerializer(article).data,
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

`urls.py`

```python
from django.urls import path

from .views import ArticleListAPIView


urlpatterns = [
    path("articles/", ArticleListAPIView.as_view(), name="article-list"),
]
```

이 예제는 DB 모델 없이 DRF `Serializer`와 `APIView` 흐름을 보여주는 최소 예제입니다. 실제 프로젝트에서는 `ARTICLES` 리스트 대신 Django 모델과 `ModelSerializer`를 쓰는 쪽이 일반적입니다.