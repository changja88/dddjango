from rest_framework import permissions, viewsets

from .models import Post
from .permissions import IsAuthorOrAdmin
from .serializers import (
    PostCreateSerializer,
    PostDetailSerializer,
    PostListSerializer,
    PostUpdateSerializer,
)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.select_related("author")
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrAdmin]

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        if self.action == "create":
            return PostCreateSerializer
        if self.action in ("update", "partial_update"):
            return PostUpdateSerializer
        return PostDetailSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == "list":
            qs = qs.list_fields()

            category = self.request.query_params.get("category")
            if category:
                qs = qs.by_category(category)
        return qs

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.increment_view_count()
        serializer = self.get_serializer(instance)
        return self.finalize_response(request, serializer.data)
