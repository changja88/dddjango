from rest_framework import serializers

from .models import Post


class PostListSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "author_name",
            "category",
            "view_count",
            "created_at",
        ]


class PostDetailSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "content",
            "author_name",
            "category",
            "has_attachment",
            "view_count",
            "created_at",
            "updated_at",
        ]


class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["title", "content", "category", "has_attachment"]

    def validate_category(self, value):
        request = self.context["request"]
        if value == Post.Category.NOTICE and not request.user.is_staff:
            raise serializers.ValidationError(
                "공지 카테고리는 관리자만 작성할 수 있습니다."
            )
        return value


class PostUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["title", "content", "category", "has_attachment"]

    def validate_category(self, value):
        request = self.context["request"]
        if value == Post.Category.NOTICE and not request.user.is_staff:
            raise serializers.ValidationError(
                "공지 카테고리는 관리자만 작성할 수 있습니다."
            )
        return value
