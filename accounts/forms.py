from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import password_validation
from .models import Mentor


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    apply_mentor = forms.BooleanField(required=False, label='Apply to be a mentor')

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
        apply_mentor = self.cleaned_data.get('apply_mentor')
        if commit:
            user.save()
            # create Mentor placeholder if user applied; approved=False by default
            if apply_mentor:
                Mentor.objects.create(user=user, approved=False)
        return user


class MentorApplicationForm(forms.ModelForm):
    class Meta:
        model = Mentor
        fields = ('bio', 'subjects', 'avatar')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # bootstrap classes
        for f in self.fields.values():
            css = f.widget.attrs.get('class', '')
            f.widget.attrs['class'] = (css + ' form-control').strip()
