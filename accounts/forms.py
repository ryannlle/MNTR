from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import password_validation
from .models import Mentor, Profile
from django.contrib.auth.models import User
from django import forms
from .constants import CLASSES


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    apply_mentor = forms.BooleanField(required=False, label='Apply to be a mentor')
    major = forms.CharField(required=False, label='Major')
    year = forms.ChoiceField(required=False, label='Year', choices=Profile.YEAR_CHOICES)

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

        # style our extra fields
        self.fields['major'].widget.attrs.update({"class": "form-control"})
        self.fields['year'].widget.attrs.update({"class": "form-select"})

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
        major = self.cleaned_data.get('major')
        year = self.cleaned_data.get('year')
        if commit:
            user.save()
            # create Mentor placeholder if user applied; approved=False by default
            if apply_mentor:
                Mentor.objects.create(user=user, approved=False)
            # create profile with major/year
            try:
                Profile.objects.create(user=user, major=major or '', year=year or '')
            except Exception:
                # if profile already exists or there is an issue, ignore (profile can be edited later)
                pass
        return user


class MentorApplicationForm(forms.ModelForm):
    # allow mentors to pick one or more classes they can mentor (choices come from accounts.constants.CLASSES)
    class_codes = forms.MultipleChoiceField(
        choices=CLASSES,
        required=False,
        # render as a list of checkboxes so users can click any combination without Ctrl/Cmd
        widget=forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}),
        help_text="Select the classes you can mentor (use Ctrl/Cmd+click to select multiple).",
    )

    class Meta:
        model = Mentor
        fields = ('bio', 'subjects', 'avatar', 'class_codes')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # bootstrap classes
        # If editing an existing Mentor instance, populate initial selected classes
        instance = kwargs.get('instance')
        if instance and getattr(instance, 'class_codes', None):
            self.initial['class_codes'] = instance.class_codes.split(',') if instance.class_codes else []

        # Apply Bootstrap classes based on widget type
        for name, f in self.fields.items():
            w = f.widget
            # Checkbox lists: inputs should use form-check-input, but the container will be handled by template
            if isinstance(w, forms.CheckboxSelectMultiple):
                w.attrs.setdefault('class', 'form-check-input')
            # Select boxes
            elif isinstance(w, forms.Select) or isinstance(w, forms.SelectMultiple):
                w.attrs.setdefault('class', 'form-select')
            else:
                w.attrs.setdefault('class', 'form-control')

    def save(self, commit=True):
        # store selected class codes as a comma-separated string on the model
        instance = super().save(commit=False)
        selected = self.cleaned_data.get('class_codes')
        if isinstance(selected, (list, tuple)):
            instance.class_codes = ",".join(selected)
        if commit:
            instance.save()
        return instance


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username", "email")


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("bio", "avatar", "major", "year")
