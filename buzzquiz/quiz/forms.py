from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import gettext as _
from django.contrib.auth.models import Group
from .models import Quiz, QuizEnroll


User = get_user_model()


class UserLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self, *args, **kwargs):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")

        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise forms.ValidationError("This user does not exists")
            if not user.check_password(password):
                raise forms.ValidationError("Incorrect password")
            if not user.is_active:
                raise forms.ValidationError("This user is not active")
        return super(UserLoginForm, self).clean(*args, **kwargs)


class RegistrationFormStudent(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    institute = forms.CharField(required=True)

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "institute",
            "password1",
            "password2",
        ]

    def save(self, commit=True):
        user = super(RegistrationFormStudent, self).save(commit=False)
        user.is_instructor = False
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]

        if commit:
            user.save()

        return user


class RegistrationFormInstructor(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "institute",
            "password1",
            "password2",
        ]

    def save(self, commit=True):
        user = super(RegistrationFormInstructor, self).save(commit=False)
        user.is_instructor = True
        user.is_staff = True
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        Group.objects.get_or_create(name ='instructors')
        if not user.groups.filter(name="instructors").exists():
            user.groups.add(Group.objects.get(name="instructors"))
        return user
       

class RegQuizenrolls(forms.Form):
    quiz_id = forms.CharField(required=True)
    
    class Meta:
        model = QuizEnroll
        fields = [
            "quiz_id",
        ]
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(RegQuizenrolls, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        enrollment = self.Meta.model(quiz_id=Quiz.objects.get(id=self.cleaned_data["quiz_id"]))
        enrollment.student_id = self.user

        if commit:
            enrollment.save()

        return enrollment
    def clean_quiz_id(self):
        if len(Quiz.objects.filter(id=self.cleaned_data["quiz_id"])) == 0:
            raise forms.ValidationError("Quiz id doesn't exists")
        return self.cleaned_data["quiz_id"]
