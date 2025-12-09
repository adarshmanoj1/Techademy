from django.urls import path
from . import views

urlpatterns = [
    path('', views.student_dashboard, name='student_dashboard'),
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('edit-profile/', views.edit_student_profile, name='edit_student_profile'),
    path('logout/', views.logout_student, name='logout_student'),

    # Course Views
    path('courses/browse/', views.browse_courses, name='browse_course'),
    path('courses/<int:course_id>/', views.course_detail_student, name='course_detail_student'),
    path('courses/<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    path('course/<int:course_id>/pay/', views.start_payment, name='start_payment'),

    # Lessons & Quizzes
    path('lesson/<int:lesson_id>/view/', views.view_lesson, name='view_lesson'),
    path('lesson/<int:lesson_id>/quiz/', views.take_quiz, name='take_quiz'),

    # Certificates
    path('certificates/<int:course_id>/', views.student_certificates, name='student_certificates'),
]
