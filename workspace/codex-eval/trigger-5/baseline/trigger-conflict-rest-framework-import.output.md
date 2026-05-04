현재 `/private/tmp/dddjango-codex-eval` 디렉터리가 비어 있고 세션이 읽기 전용이라 파일 생성은 못 했습니다. 아래 예제를 그대로 추가하면 됩니다.

`serializers.py`

```python
from rest_framework import serializers

class BookSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=100)
    author = serializers.CharField(max_length=100)
    published_year = serializers.IntegerField(required=False)
```

`views.py`

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import BookSerializer


BOOKS = [
    {"id": 1, "title": "Django for APIs", "author": "William S. Vincent", "published_year": 2022},
]


class BookListAPIView(APIView):
    def get(self, request):
        serializer = BookSerializer(BOOKS, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BookSerializer(data=request.data)

        if serializer.is_valid():
            book = {
                "id": len(BOOKS) + 1,
                **serializer.validated_data,
            }
            BOOKS.append(book)
            return Response(book, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

`urls.py`

```python
from django.urls import path

from .views import BookListAPIView

urlpatterns = [
    path("books/", BookListAPIView.as_view(), name="book-list"),
]
```

요청 예시:

```json
{
  "title": "Two Scoops of Django",
  "author": "Daniel Roy Greenfeld",
  "published_year": 2021
}
```