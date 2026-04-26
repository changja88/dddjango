from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthorOrAdminOrReadOnly(BasePermission):
    """
    - 읽기: 모든 인증된 사용자
    - 수정/삭제: 작성자 본인 또는 관리자(is_staff)
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author == request.user or request.user.is_staff
