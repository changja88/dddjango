from rest_framework.permissions import BasePermission


class IsPatient(BasePermission):
    """요청 사용자가 환자(Patient) 프로필을 보유하고 있는지 확인한다."""

    message = "환자 권한이 필요합니다."

    def has_permission(self, request, view) -> bool:
        return (
            request.user.is_authenticated
            and hasattr(request.user, "patient_profile")
        )


class IsDoctor(BasePermission):
    """요청 사용자가 의사(Doctor) 프로필을 보유하고 있는지 확인한다."""

    message = "의사 권한이 필요합니다."

    def has_permission(self, request, view) -> bool:
        return (
            request.user.is_authenticated
            and hasattr(request.user, "doctor_profile")
        )


class IsAppointmentOwner(BasePermission):
    """
    예약의 소유자(환자 본인 또는 배정된 의사)만 접근 가능하다.

    - 환자: 자신의 예약만 접근 가능
    - 의사: 자신에게 배정된 예약만 접근 가능
    """

    message = "본인의 예약에만 접근할 수 있습니다."

    def has_object_permission(self, request, view, obj) -> bool:
        user = request.user

        if hasattr(user, "patient_profile"):
            return obj.patient == user.patient_profile

        if hasattr(user, "doctor_profile"):
            return obj.doctor == user.doctor_profile

        return False
