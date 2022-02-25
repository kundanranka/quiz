from django.conf.urls import url
from django.urls import path
from . import views
from django.contrib import admin

admin.autodiscover()
admin.site.enable_nav_sidebar = False
app_name = 'quiz'

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^user-home$', views.user_home, name='user_home'),
    url(r'^instructor$', views.instructor_home, name='instructor'),
    url(r'^login/', views.login_view, name='login'),
    url(r'^logout/', views.logout_view, name='logout'),
    url(r'^register/', views.register_student, name='register'),
    url(r'^register-instructor/', views.register_instructor, name='register-instructor'),
    path('enroll/<slug:quiz>/',views.RegQuizenrollURL),
    path('quiz/<slug:quiz>/start/',views.quiz),
    path('quiz/<slug:quiz>/mock/',views.mock),
    path('quiz/<slug:quiz>/answer-key/',views.answer_key),
    url(r'^enroll/', views.RegQuizenroll, name='enroll'),
]