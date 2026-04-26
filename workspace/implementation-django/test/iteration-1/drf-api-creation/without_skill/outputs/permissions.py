from rest_framework.permissions import BasePermission


class IsOrderOwner(BasePermission):
    """주문자 본인만 자기 주문에 접근할 수 있도록 제한한다."""

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
