from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from datetime import datetime
from .models import Questions, Quiz, QuizEnroll
from .forms import RegQuizenrolls, RegistrationFormInstructor, UserLoginForm, RegistrationFormStudent
from django.contrib.auth.decorators import user_passes_test

def home(request):
    return redirect('/login')


@login_required()
def user_home(request):
    if request.user.is_instructor:
        return redirect('/instructor')
    return render(request, 'quiz/home.html')

@login_required()
@user_passes_test(lambda user: user.is_instructor,login_url='/user-home')
def instructor_home(request):
    now = datetime.now()
    now_time = datetime.time(now)
    queryset = Quiz.objects.filter(createdBy=request.user,is_active=True)
    contex = {
        "completed" : queryset.filter(end_date__lt=now).count(),
        "running" :queryset.filter(end_date__gte=now,start_date__lte=now).count(),
        "upcoming" :queryset.filter(start_date__gt=now).count(),
    }
    return render(request, 'quiz/instructor_home.html',context=contex)


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
        if request.GET['next']:
            return redirect(request.GET['next'])
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

@login_required()
def RegQuizenroll(request):
    title = "Enroll Quiz"
    if request.method == 'POST':
        form = RegQuizenrolls(request.user,request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = RegQuizenrolls(request.user)
    context = {'form': form, 'title': title}
    return render(request, 'quiz/enroll.html', context=context)

@login_required()
def RegQuizenrollURL(request,quiz):
    if request.user.is_instructor == True:
        return redirect('/')
    QuizEnroll.objects.get_or_create(quiz_id=Quiz(id=quiz),student_id=request.user)
    return redirect('/')