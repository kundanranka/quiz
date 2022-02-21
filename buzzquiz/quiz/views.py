from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from datetime import datetime
from .models import Answers, Options, Questions, Quiz, QuizEnroll
from .forms import (
    RegQuizenrolls,
    RegistrationFormInstructor,
    UserLoginForm,
    RegistrationFormStudent,
)
from django.contrib.auth.decorators import user_passes_test


def home(request):
    return redirect("/login")


@login_required()
def user_home(request):
    if request.user.is_instructor:
        return redirect("/instructor")
    now = datetime.now()
    now_time = datetime.time(now)
    quizs = list(
        map(lambda x: x.quiz_id.id, QuizEnroll.objects.filter(student_id=request.user))
    )
    queryset = Quiz.objects.filter(id__in=quizs, is_active=True)
    contex = {
        "completed": {
            "completedCount": queryset.filter(end_date__lt=now).count(),
        },
        "running": {
            "runningCount": queryset.filter(
                end_date__gte=now, start_date__lte=now
            ).count(),
        },
        "upcoming": {
            "upcomingCount": queryset.filter(start_date__gt=now).count(),
        },
    }
    filter = request.GET.get("filter", None)
    if filter is None:
        filter = "running"
    if filter == "running":
        contex["running"]["filter"] = True
        contex["selected"] = queryset.filter(
            end_date__gte=now, start_date__lte=now
        ).order_by("start_date", "start_time")
    if filter == "upcoming":
        contex["upcoming"]["filter"] = True
        contex["selected"] = queryset.filter(start_date__gt=now).order_by(
            "start_date", "start_time"
        )
    if filter == "completed":
        contex["completed"]["filter"] = True
        contex["selected"] = queryset.filter(end_date__lt=now).order_by(
            "start_date", "start_time"
        )
    return render(request, "quiz/home.html", context=contex)


@login_required()
@user_passes_test(lambda user: user.is_instructor, login_url="/user-home")
def instructor_home(request):
    now = datetime.now()
    now_time = datetime.time(now)
    queryset = Quiz.objects.filter(createdBy=request.user, is_active=True)
    contex = {
        "completed": {
            "completedCount": queryset.filter(end_date__lt=now).count(),
        },
        "running": {
            "runningCount": queryset.filter(
                end_date__gte=now, start_date__lte=now
            ).count(),
        },
        "upcoming": {
            "upcomingCount": queryset.filter(start_date__gt=now).count(),
        },
    }
    filter = request.GET.get("filter", None)
    if filter is None:
        filter = "running"
    if filter == "running":
        contex["running"]["filter"] = True
        contex["selected"] = queryset.filter(
            end_date__gte=now, start_date__lte=now
        ).order_by("start_date", "start_time")
    if filter == "upcoming":
        contex["upcoming"]["filter"] = True
        contex["selected"] = queryset.filter(start_date__gt=now).order_by(
            "start_date", "start_time"
        )
    if filter == "completed":
        contex["completed"]["filter"] = True
        contex["selected"] = queryset.filter(end_date__lt=now).order_by(
            "start_date", "start_time"
        )

    return render(request, "quiz/instructor_home.html", context=contex)


def is_auth(user):
    return not user.is_authenticated


@user_passes_test(is_auth, login_url="/user-home")
def login_view(request):
    title = "Login"
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(email=email, password=password)
        login(request, user)
        if request.GET.get("next", None):
            return redirect(request.GET["next"])
        return redirect("/user-home")
    return render(request, "quiz/login.html", {"form": form, "title": title})


def register_student(request):
    title = "Create account"
    if request.method == "POST":
        form = RegistrationFormStudent(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/login")
    else:
        form = RegistrationFormStudent()

    context = {"form": form, "title": title}
    return render(request, "quiz/registration.html", context=context)


def register_instructor(request):
    title = "Create account - Instructor"
    if request.method == "POST":
        form = RegistrationFormInstructor(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/login")
    else:
        form = RegistrationFormInstructor()
    context = {"form": form, "title": title}
    return render(request, "quiz/registration.html", context=context)


def logout_view(request):
    logout(request)
    return redirect("/")


@login_required()
def RegQuizenroll(request):
    title = "Enroll Quiz"
    if request.method == "POST":
        form = RegQuizenrolls(request.user, request.POST)
        if form.is_valid():
            form.save()
            return redirect("/")
    else:
        form = RegQuizenrolls(request.user)
    context = {"form": form, "title": title}
    return render(request, "quiz/enroll.html", context=context)


@login_required()
def RegQuizenrollURL(request, quiz):
    if request.user.is_instructor == True:
        return redirect("/")
    QuizEnroll.objects.get_or_create(quiz_id=Quiz(id=quiz), student_id=request.user)
    return redirect("/")


@login_required()
@user_passes_test(lambda user: not user.is_instructor, login_url="/user-home")
def quiz(request, quiz):
    if (
        QuizEnroll.objects.filter(quiz_id__id=quiz, student_id=request.user).count()
        == 0
    ):
        return  # TODO Failure of
    pass
    return redirect("/")


@login_required()
@user_passes_test(lambda user: not user.is_instructor, login_url="/user-home")
def mock(request, quiz):

    if request.method == "POST":
        question = Questions.objects.get(id=request.POST.get("questionid", None))
        if question.type == "Single Correct":
            keys = [request.POST.get("option", None)]
        else:
            keys = list(request.POST.keys())[2:]
        flag = 0
        for option in Options.objects.filter(id__in=keys):
            if len(Answers.objects.filter(question=option.question)) == 0:
                flag = 1
                Answers(
                    question=option.question, option=option, user=request.user
                ).save()
        if flag == 0:
            Answers(
                    question=question,option=None, user=request.user
                ).save()
    selected_quiz = Quiz.objects.get(id=quiz)
    answered = [
        x.question.id for x in Answers.objects.filter(question__quiz=selected_quiz)
    ]
    questions = Questions.objects.filter(quiz=selected_quiz, mock=True).exclude(
        id__in=answered
    )
    question_to_attend = questions.first()
    if question_to_attend == None:
        Answers.objects.filter(question__id__in=answered, user=request.user).delete()
        return redirect("/")
    options = Options.objects.filter(question=question_to_attend)
    return render(
        request,
        "quiz/attend_quiz.html",
        context={"question": question_to_attend, "options": options},
    )
