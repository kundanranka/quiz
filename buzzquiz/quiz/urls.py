from django.conf.urls import url
from . import views

app_name = 'quiz'

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^user-home$', views.user_home, name='user_home'),
    url(r'^login/', views.login_view, name='login'),
    url(r'^logout/', views.logout_view, name='logout'),
    url(r'^register/', views.register_student, name='register'),
    url(r'^register-instructor/', views.register_instructor, name='register-instructor'),

]
