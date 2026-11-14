from django import forms


class SuspensionGrantForm(forms.Form):
    order_id: forms.CharField = forms.CharField()

    class Meta:
        fields: tuple[str, ...] = ("order_id",)
