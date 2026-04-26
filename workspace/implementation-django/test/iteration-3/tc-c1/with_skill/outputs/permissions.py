from rest_framework import permissions


class IsAuthorOrAdmin(permissions.BasePermission):
    """작성자 본인 또는 관리자만 수정/삭제 가능."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user or request.user.is_staff
