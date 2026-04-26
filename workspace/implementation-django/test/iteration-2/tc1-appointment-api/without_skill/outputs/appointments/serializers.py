from django.db import IntegrityError
from rest_framework import serializers

from .models import Appointment, AppointmentStatus, Doctor, Patient


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ["id", "name", "date_of_birth", "phone"]
        read_only_fields = ["id"]


class DoctorSerializer(serializers.ModelSerializer):
    department_display = serializers.CharField(
        source="get_department_display",
        read_only=True,
    )

    class Meta:
        model = Doctor
        fields = ["id", "name", "department", "department_display", "license_number"]
        read_only_fields = ["id"]


class AppointmentListSerializer(serializers.ModelSerializer):
    """예약 목록 조회용 시리얼라이저 (읽기 전용, 간략 정보)."""

    patient_name = serializers.CharField(source="patient.name", read_only=True)
    doctor_name = serializers.CharField(source="doctor.name", read_only=True)
    department_display = serializers.CharField(
        source="get_department_display",
        read_only=True,
    )
    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    class Meta:
        model = Appointment
        fields = [
            "id",
            "patient",
            "patient_name",
            "doctor",
            "doctor_name",
            "datetime",
            "department",
            "department_display",
            "status",
            "status_display",
            "created_at",
        ]
        read_only_fields = fields


class AppointmentDetailSerializer(serializers.ModelSerializer):
    """예약 상세 조회용 시리얼라이저 (읽기 전용, 전체 정보)."""

    patient_detail = PatientSerializer(source="patient", read_only=True)
    doctor_detail = DoctorSerializer(source="doctor", read_only=True)
    department_display = serializers.CharField(
        source="get_department_display",
        read_only=True,
    )
    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    class Meta:
        model = Appointment
        fields = [
            "id",
            "patient",
            "patient_detail",
            "doctor",
            "doctor_detail",
            "datetime",
            "department",
            "department_display",
            "status",
            "status_display",
            "note",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class AppointmentCreateSerializer(serializers.ModelSerializer):
    """예약 생성용 시리얼라이저."""

    class Meta:
        model = Appointment
        fields = ["id", "doctor", "datetime", "department", "note"]
        read_only_fields = ["id"]

    def validate(self, attrs):
        """진료과 일치 여부와 중복 예약을 검증한다."""
        doctor = attrs.get("doctor")
        department = attrs.get("department")
        appointment_datetime = attrs.get("datetime")

        # 진료과 일치 여부 검증
        if doctor and department and doctor.department != department:
            raise serializers.ValidationError(
                {
                    "department": (
                        f"선택한 진료과가 의사의 진료과"
                        f"({doctor.get_department_display()})와 일치하지 않습니다."
                    )
                }
            )

        # 같은 의사, 같은 시간대 중복 예약 검증
        if doctor and appointment_datetime:
            conflicting = Appointment.objects.filter(
                doctor=doctor,
                datetime=appointment_datetime,
            ).exclude(
                status=AppointmentStatus.CANCELLED,
            )

            # 수정 시 자기 자신 제외
            if self.instance:
                conflicting = conflicting.exclude(pk=self.instance.pk)

            if conflicting.exists():
                raise serializers.ValidationError(
                    {
                        "datetime": "해당 의사에게 같은 시간대에 이미 예약이 존재합니다.",
                    }
                )

        return attrs

    def create(self, validated_data):
        """환자 정보를 자동으로 설정하여 예약을 생성한다."""
        request = self.context.get("request")
        if request and hasattr(request.user, "patient_profile"):
            validated_data["patient"] = request.user.patient_profile

        validated_data["status"] = AppointmentStatus.PENDING

        try:
            return super().create(validated_data)
        except IntegrityError:
            raise serializers.ValidationError(
                "해당 의사에게 같은 시간대에 이미 예약이 존재합니다."
            )


class AppointmentUpdateSerializer(serializers.ModelSerializer):
    """예약 수정용 시리얼라이저 (대기 상태에서만 일부 필드 수정 가능)."""

    class Meta:
        model = Appointment
        fields = ["datetime", "note"]

    def validate(self, attrs):
        """대기 상태인지, 중복 예약인지 검증한다."""
        if self.instance and self.instance.status != AppointmentStatus.PENDING:
            raise serializers.ValidationError(
                "대기 상태인 예약만 수정할 수 있습니다."
            )

        appointment_datetime = attrs.get("datetime")
        if appointment_datetime and self.instance:
            conflicting = Appointment.objects.filter(
                doctor=self.instance.doctor,
                datetime=appointment_datetime,
            ).exclude(
                status=AppointmentStatus.CANCELLED,
            ).exclude(
                pk=self.instance.pk,
            )

            if conflicting.exists():
                raise serializers.ValidationError(
                    {
                        "datetime": "해당 의사에게 같은 시간대에 이미 예약이 존재합니다.",
                    }
                )

        return attrs


class StatusTransitionSerializer(serializers.Serializer):
    """상태 전이 액션에서 사용하는 시리얼라이저."""

    # 액션별로 target_status를 뷰에서 주입한다.
    # 이 시리얼라이저는 응답 반환 형태만 정의한다.
    pass
