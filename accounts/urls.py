from django.urls import path
from . import views

urlpatterns = [
    path('student/', views.register_student, name='register_student'),
    path('instructor/', views.register_instructor, name='register_instructor'),
    path('logout/', views.logout_view, name='logout'),
]
