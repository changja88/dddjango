from django.apps import AppConfig


class OrbitConfig(AppConfig):
    name: str = "application.orbit.driven_layer.django_orbit"
    label: str = "orbit"

    def ready(self) -> None:
        from application.orbit.composition_root import event_wiring  # noqa: F401
