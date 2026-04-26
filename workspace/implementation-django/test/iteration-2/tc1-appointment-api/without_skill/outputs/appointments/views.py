from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Appointment, AppointmentStatus, Doctor, Patient
from .permissions import IsAppointmentOwner, IsDoctor, IsPatient
from .serializers import (
    AppointmentCreateSerializer,
    AppointmentDetailSerializer,
    AppointmentListSerializer,
    AppointmentUpdateSerializer,
    DoctorSerializer,
    PatientSerializer,
)


# ---------------------------------------------------------------------------
# Patient / Doctor 조회
# ---------------------------------------------------------------------------


class PatientListView(generics.ListAPIView):
    """환자 목록 조회."""

    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]


class DoctorListView(generics.ListAPIView):
    """의사 목록 조회. 진료과 필터링 지원."""

    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        department = self.request.query_params.get("department")
        if department:
            qs = qs.filter(department=department)
        return qs


# ---------------------------------------------------------------------------
# Appointment CRUD
# ---------------------------------------------------------------------------


class AppointmentListCreateView(generics.ListCreateAPIView):
    """
    예약 목록 조회 및 생성.

    GET  - 환자: 본인 예약만 / 의사: 본인에게 배정된 예약만
    POST - 환자만 생성 가능
    """

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AppointmentCreateSerializer
        return AppointmentListSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Appointment.objects.select_related("patient", "doctor")

        if hasattr(user, "patient_profile"):
            return qs.filter(patient=user.patient_profile)

        if hasattr(user, "doctor_profile"):
            return qs.filter(doctor=user.doctor_profile)

        # 환자도 의사도 아닌 사용자(관리자 등)에게는 빈 쿼리셋 반환
        return qs.none()

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsPatient()]
        return [IsAuthenticated()]

    def get_queryset_filtered(self):
        """상태/진료과 필터링을 적용한 쿼리셋."""
        qs = self.get_queryset()

        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)

        department = self.request.query_params.get("department")
        if department:
            qs = qs.filter(department=department)

        return qs

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset_filtered())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class AppointmentDetailView(generics.RetrieveUpdateAPIView):
    """
    예약 상세 조회 및 수정.

    GET   - 본인 예약만 조회 가능
    PATCH - 대기 상태인 본인 예약만 수정 가능
    """

    permission_classes = [IsAuthenticated, IsAppointmentOwner]
    queryset = Appointment.objects.select_related("patient", "doctor")

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return AppointmentUpdateSerializer
        return AppointmentDetailSerializer


# ---------------------------------------------------------------------------
# 상태 전이 액션
# ---------------------------------------------------------------------------


class AppointmentConfirmView(APIView):
    """
    예약 확정 (의사 전용).

    POST /api/appointments/{id}/confirm/
    대기 -> 확정 전이만 허용.
    """

    permission_classes = [IsAuthenticated, IsDoctor]

    def post(self, request, pk):
        try:
            appointment = Appointment.objects.select_related(
                "patient", "doctor"
            ).get(pk=pk)
        except Appointment.DoesNotExist:
            return Response(
                {"detail": "예약을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 본인에게 배정된 예약인지 확인
        if appointment.doctor != request.user.doctor_profile:
            raise PermissionDenied("본인에게 배정된 예약만 확정할 수 있습니다.")

        try:
            appointment.transition_to(AppointmentStatus.CONFIRMED)
        except DjangoValidationError as e:
            raise ValidationError({"detail": e.message})

        appointment.save()

        serializer = AppointmentDetailSerializer(appointment)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AppointmentCompleteView(APIView):
    """
    진료 완료 (의사 전용).

    POST /api/appointments/{id}/complete/
    확정 -> 완료 전이만 허용.
    """

    permission_classes = [IsAuthenticated, IsDoctor]

    def post(self, request, pk):
        try:
            appointment = Appointment.objects.select_related(
                "patient", "doctor"
            ).get(pk=pk)
        except Appointment.DoesNotExist:
            return Response(
                {"detail": "예약을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if appointment.doctor != request.user.doctor_profile:
            raise PermissionDenied("본인에게 배정된 예약만 완료 처리할 수 있습니다.")

        try:
            appointment.transition_to(AppointmentStatus.COMPLETED)
        except DjangoValidationError as e:
            raise ValidationError({"detail": e.message})

        appointment.save()

        serializer = AppointmentDetailSerializer(appointment)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AppointmentCancelView(APIView):
    """
    예약 취소.

    POST /api/appointments/{id}/cancel/
    대기 또는 확정 상태에서만 취소 가능.
    환자 본인 또는 배정된 의사만 취소할 수 있다.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            appointment = Appointment.objects.select_related(
                "patient", "doctor"
            ).get(pk=pk)
        except Appointment.DoesNotExist:
            return Response(
                {"detail": "예약을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 환자 본인이거나 배정된 의사인지 확인
        user = request.user
        is_owner = (
            (hasattr(user, "patient_profile") and appointment.patient == user.patient_profile)
            or (hasattr(user, "doctor_profile") and appointment.doctor == user.doctor_profile)
        )
        if not is_owner:
            raise PermissionDenied("본인의 예약만 취소할 수 있습니다.")

        try:
            appointment.transition_to(AppointmentStatus.CANCELLED)
        except DjangoValidationError as e:
            raise ValidationError({"detail": e.message})

        appointment.save()

        serializer = AppointmentDetailSerializer(appointment)
        return Response(serializer.data, status=status.HTTP_200_OK)
