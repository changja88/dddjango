현재 작업 디렉터리는 비어 있고 읽기 전용이라 파일 생성은 못 했습니다. 대신 바로 붙여 넣을 수 있는 예제를 준비했습니다.

`serializers.py`

```python
from rest_framework import serializers


class PostSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=100)
    content = serializers.CharField()
    author = serializers.CharField(max_length=50)
```

`views.py`

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import PostSerializer


class PostAPIView(APIView):
    def get(self, request):
        data = [
            {
                "id": 1,
                "title": "첫 번째 글",
                "content": "APIView 예제입니다.",
                "author": "admin",
            }
        ]

        serializer = PostSerializer(data, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PostSerializer(data=request.data)

        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

`urls.py`에 연결할 때는 이렇게 쓰면 됩니다.

```python
from django.urls import path

from .views import PostAPIView

urlpatterns = [
    path("posts/", PostAPIView.as_view(), name="post-list"),
]
```