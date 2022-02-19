from tkinter import CASCADE
from click import option
from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from .manager import UserManager
from tinymce.models import HTMLField


class Users(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=30, null=False,blank=False)
    last_name = models.CharField(_('last name'), max_length=30, null=False,blank=False)
    institute = models.CharField(_('institute name'), max_length=100,null=False,blank=False)
    is_instructor = models.BooleanField(_('is instructor'),default=False)
    is_staff = models.BooleanField(_('is staff'),default=False)
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name','last_name','institute']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.email

    def get_full_name(self):
        '''
        Returns the first_name plus the last_name, with a space in between.
        '''
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        '''
        Returns the short name for the user.
        '''
        return self.first_name
class Quiz(models.Model):
    createdBy = models.ForeignKey(Users, on_delete=models.CASCADE,related_name='quiz_createdBy')
    name = models.CharField(max_length=100,null=False,blank=False)
    id = models.CharField(max_length=100,null=False,blank=False,primary_key=True)
    description = models.CharField(max_length=500,null=False,blank=False)
    start_date = models.DateField()
    start_time = models.TimeField()
    end_date = models.DateField()
    end_time = models.TimeField()
    duration = models.IntegerField(null=False,blank=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return str(self.createdBy) + " - " + self.id

type = (
    ("Single Correct","SINGLE_CORRECT"),
    ("Multiple Correct","MULTIPLE_CORRECT"),
)
class Questions(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE,related_name='question_quiz')
    question = HTMLField(null=False,blank=False)
    duration = models.IntegerField(null=False,blank=False)
    type = models.CharField(max_length=100,null=False,blank=False,choices=type)
    mark = models.IntegerField(null=False,blank=False)
    negative_mark = models.IntegerField(null=False,blank=False,default=0)
    hint = models.CharField(max_length=500,null=False,default="")
    mock = models.BooleanField(default=False)

class Options(models.Model):
    question = models.ForeignKey(Questions, on_delete=models.CASCADE,related_name='option_question')
    option = models.CharField(max_length=100,null=False,blank=False)
    is_correct = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('option')
        verbose_name_plural = _('options')
        

class QuizEnroll(models.Model):
    quiz_id = models.ForeignKey(Quiz, on_delete=models.CASCADE,related_name='quiz_id')
    student_id = models.ForeignKey(Users, on_delete=models.CASCADE,related_name='student_id')
 
    class Meta:
        verbose_name = _('Enrollment')
        verbose_name_plural = _('Enrollments')

class Answers(models.Model):
    question = models.ForeignKey(Questions,on_delete=models.CASCADE)
    option = models.ForeignKey(Options,on_delete=models.CASCADE)
    user = models.ForeignKey(Users,on_delete=models.CASCADE)