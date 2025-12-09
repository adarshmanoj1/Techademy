from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('approve/<int:user_id>/', views.approve_instructor, name='approve_instructor'),
    path('reject/<int:user_id>/', views.reject_instructor, name='reject_instructor'),
    path('course/approve/<int:course_id>/', views.approve_course, name='approve_course'),
    path('course/reject/<int:course_id>/', views.reject_course, name='reject_course'),
]
