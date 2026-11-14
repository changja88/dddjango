from django.views.generic import TemplateView


class SuspensionPanel(TemplateView):
    template_name: str = "admin/backoffice/suspension.html"
