from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import password_validation


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap form-control classes to widgets for cleaner UI
        for field_name in ("username", "email", "password1", "password2"):
            field = self.fields.get(field_name)
            if field:
                field.widget.attrs.update({"class": "form-control"})

        # Try to gather password validator help texts and expose them as a list
        try:
            default_validators = password_validation.get_default_password_validators()
            self.password_help_list = password_validation.password_validators_help_texts(default_validators)
        except Exception:
            # Fall back to the built-in help_text if validators aren't configured
            self.password_help_list = []

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
