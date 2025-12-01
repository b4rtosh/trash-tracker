from django import forms
from .models import Route, Address


class RouteForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = ["name"]
        widgets = {"name": forms.TextInput(attrs={"class": "form-control"})}


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ["street", "city", "state", "postal_code", "country"]
        widgets = {
            "street": forms.TextInput(attrs={"class": "form-control"}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "state": forms.TextInput(attrs={"class": "form-control"}),
            "postal_code": forms.TextInput(attrs={"class": "form-control"}),
            "country": forms.TextInput(attrs={"class": "form-control"}),
        }
