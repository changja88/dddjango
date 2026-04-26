from rest_framework import viewsets, permissions
from rest_framework.response import Response

from .models import Post
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import PostDetailSerializer, PostListSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.select_related("author").all()
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrAdminOrReadOnly]

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        return PostDetailSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        Post.objects.filter(pk=instance.pk).update(view_count=instance.view_count + 1)
        instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
