from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.login_page, name='scheduler-login'),
    path('home/', views.home_page, name='scheduler-home'),
    path('courses/', views.course_page, name='scheduler-courses'),
    path('add-course/', views.add_course, name='scheduler-add-course'),
    path('delete-course/<str:name>', views.delete_course, name='scheduler-delete-course'),
    path('update-course/<str:name>', views.update_course, name='scheduler-update-course'),
    path('users/', views.user_page, name='scheduler-users'),
    path('user-info/<str:email>', views.user_info, name='scheduler-user'),
    path('add-user/', views.add_user, name='scheduler-add-user'),
    path('delete-user/<str:email>', views.delete_user, name='scheduler-delete-user'),
    path('logout_user/', views.logout_user, name="scheduler-logout-user"),
]
