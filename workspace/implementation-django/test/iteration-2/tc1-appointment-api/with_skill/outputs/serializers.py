from rest_framework import serializers

from apps.appointments.models import Appointment
from apps.doctors.models import Doctor
from apps.patients.models import Patient


class PatientSummarySerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="user.get_full_name", read_only=True)

    class Meta:
        model = Patient
        fields = ["id", "name", "phone_number"]


class DoctorSummarySerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="user.get_full_name", read_only=True)
    department_display = serializers.CharField(
        source="get_department_display", read_only=True
    )

    class Meta:
        model = Doctor
        fields = ["id", "name", "department", "department_display"]


class AppointmentListSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(
        source="patient.user.get_full_name", read_only=True
    )
    doctor_name = serializers.CharField(
        source="doctor.user.get_full_name", read_only=True
    )
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )
    department_display = serializers.CharField(
        source="get_department_display", read_only=True
    )

    class Meta:
        model = Appointment
        fields = [
            "id",
            "patient_name",
            "doctor_name",
            "scheduled_at",
            "department",
            "department_display",
            "status",
            "status_display",
        ]


class AppointmentDetailSerializer(serializers.ModelSerializer):
    patient = PatientSummarySerializer(read_only=True)
    doctor = DoctorSummarySerializer(read_only=True)
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )
    department_display = serializers.CharField(
        source="get_department_display", read_only=True
    )

    class Meta:
        model = Appointment
        fields = [
            "id",
            "patient",
            "doctor",
            "scheduled_at",
            "department",
            "department_display",
            "status",
            "status_display",
            "note",
            "created_at",
            "updated_at",
        ]


class AppointmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ["doctor", "scheduled_at", "department", "note"]

    def validate(self, attrs):
        doctor = attrs["doctor"]
        scheduled_at = attrs["scheduled_at"]

        conflicting = Appointment.objects.filter(
            doctor=doctor,
            scheduled_at=scheduled_at,
        ).exclude(status=Appointment.Status.CANCELLED)

        if conflicting.exists():
            raise serializers.ValidationError(
                {"scheduled_at": "해당 의사는 이 시간에 이미 예약이 있습니다."}
            )

        return attrs


class AppointmentStatusSerializer(serializers.Serializer):
    action = serializers.ChoiceField(
        choices=["confirm", "complete", "cancel"],
    )
