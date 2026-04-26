from rest_framework.permissions import BasePermission


class IsPatient(BasePermission):
    """요청자가 환자 프로필을 가지고 있는지 확인한다."""

    def has_permission(self, request, view):
        return hasattr(request.user, "patient_profile")


class IsDoctor(BasePermission):
    """요청자가 의사 프로필을 가지고 있는지 확인한다."""

    def has_permission(self, request, view):
        return hasattr(request.user, "doctor_profile")


class IsAppointmentParticipant(BasePermission):
    """예약의 환자 또는 담당 의사만 접근 가능하다."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        if hasattr(user, "patient_profile"):
            return obj.patient == user.patient_profile
        if hasattr(user, "doctor_profile"):
            return obj.doctor == user.doctor_profile
        return False


class IsAppointmentDoctor(BasePermission):
    """예약의 담당 의사만 상태 변경이 가능하다."""

    def has_object_permission(self, request, view, obj):
        return (
            hasattr(request.user, "doctor_profile")
            and obj.doctor == request.user.doctor_profile
        )
