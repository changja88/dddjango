from rest_framework import serializers

from .models import Post


class PostListSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Post
        fields = ["id", "title", "author", "category", "view_count"]


class PostDetailSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "content",
            "author",
            "category",
            "has_attachment",
            "view_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["view_count"]

    def validate_category(self, value):
        request = self.context.get("request")
        if value == Post.Category.NOTICE and not request.user.is_staff:
            raise serializers.ValidationError(
                "공지 카테고리는 관리자만 작성할 수 있습니다."
            )
        return value
