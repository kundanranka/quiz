from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from .forms import RegistrationFormInstructor, UserLoginForm, RegistrationFormStudent
from django.contrib.auth.decorators import user_passes_test

def home(request):
    context = {}
    return redirect('/login')


@login_required()
def user_home(request):
    context = {}
    return render(request, 'quiz/home.html', context=context)

def is_auth(user):
    return not user.is_authenticated

@user_passes_test(is_auth,login_url='/user-home')
def login_view(request):
    title = "Login"
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(email=email, password=password)
        login(request, user)
        return redirect('/user-home')
    return render(request, 'quiz/login.html', {"form": form, "title": title})


def register_student(request):
    title = "Create account"
    if request.method == 'POST':
        form = RegistrationFormStudent(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/login')
    else:
        form = RegistrationFormStudent()

    context = {'form': form, 'title': title}
    return render(request, 'quiz/registration.html', context=context)

def register_instructor(request):
    title = "Create account - Instructor"
    if request.method == 'POST':
        form = RegistrationFormInstructor(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/login')
    else:
        form = RegistrationFormInstructor()
    context = {'form': form, 'title': title}
    return render(request, 'quiz/registration.html', context=context)

def logout_view(request):
    logout(request)
    return redirect('/')
