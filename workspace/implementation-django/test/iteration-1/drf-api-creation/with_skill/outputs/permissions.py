from rest_framework.permissions import BasePermission


class IsOrderOwner(BasePermission):
    """Only the order owner can access the order."""

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
