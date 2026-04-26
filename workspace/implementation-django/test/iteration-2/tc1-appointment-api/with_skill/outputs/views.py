from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.appointments.models import Appointment
from apps.appointments.permissions import (
    IsAppointmentDoctor,
    IsAppointmentParticipant,
    IsPatient,
)
from apps.appointments.serializers import (
    AppointmentCreateSerializer,
    AppointmentDetailSerializer,
    AppointmentListSerializer,
    AppointmentStatusSerializer,
)


class AppointmentViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "delete", "head", "options"]

    def get_queryset(self):
        user = self.request.user
        base_qs = Appointment.objects.select_related(
            "patient__user",
            "doctor__user",
        )

        if hasattr(user, "patient_profile"):
            return base_qs.for_patient(user.patient_profile)
        if hasattr(user, "doctor_profile"):
            return base_qs.for_doctor(user.doctor_profile)

        return Appointment.objects.none()

    def get_serializer_class(self):
        if self.action == "list":
            return AppointmentListSerializer
        if self.action == "create":
            return AppointmentCreateSerializer
        if self.action == "change_status":
            return AppointmentStatusSerializer
        return AppointmentDetailSerializer

    def get_permissions(self):
        if self.action == "create":
            return [permissions.IsAuthenticated(), IsPatient()]
        if self.action in ("retrieve", "destroy"):
            return [permissions.IsAuthenticated(), IsAppointmentParticipant()]
        if self.action == "change_status":
            return [permissions.IsAuthenticated(), IsAppointmentDoctor()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user.patient_profile)

    def perform_destroy(self, instance):
        try:
            instance.cancel()
        except DjangoValidationError as exc:
            raise DjangoValidationError(exc.message)

    @action(
        detail=True,
        methods=["post"],
        url_path="status",
        url_name="change-status",
    )
    def change_status(self, request, pk=None):
        appointment = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action_name = serializer.validated_data["action"]
        action_map = {
            "confirm": appointment.confirm,
            "complete": appointment.complete,
            "cancel": appointment.cancel,
        }

        try:
            action_map[action_name]()
        except DjangoValidationError as exc:
            return Response(
                {"detail": exc.message},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            AppointmentDetailSerializer(appointment).data,
            status=status.HTTP_200_OK,
        )
