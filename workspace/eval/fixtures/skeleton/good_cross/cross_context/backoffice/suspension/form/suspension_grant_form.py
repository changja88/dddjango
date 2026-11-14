from django import forms


class SuspensionGrantForm(forms.Form):
    nickname: forms.CharField = forms.CharField()
