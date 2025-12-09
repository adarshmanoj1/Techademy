from django.urls import path
from . import views

urlpatterns = [
    # Dashboard & Profile
    path('dashboard/', views.instructor_dashboard, name='instructor_dashboard'),
    path('register/', views.register_instructor, name='register_instructor'),
    path('profile/', views.instructor_profile, name='instructor_profile'),

    # Course
    path('add-course/', views.add_course, name='add_course'),
    path('my-courses/', views.instructor_course_list, name='instructor_course_list'),
    path('course/<int:course_id>/details/', views.course_detail, name='course_detail'),
    path('course/<int:course_id>/edit/', views.edit_course, name='edit_course'),

    # Lesson
    path('select-course-for-lessons/', views.select_course_for_lessons, name='select_course_for_lessons'),
    path('course/<int:course_id>/lessons/', views.manage_lessons, name='manage_lessons'),
    path('lesson/<int:course_id>/add/', views.add_lesson, name='add_lesson'),
    path('lesson/<int:lesson_id>/edit/', views.edit_lesson, name='edit_lesson'),
    path('lesson/<int:lesson_id>/delete/', views.delete_lesson, name='delete_lesson'),

    # Quiz
    path('lesson/<int:lesson_id>/add-question/', views.add_question_with_choices, name='add_question'),
    path('lesson/<int:lesson_id>/quizzes/', views.view_quizzes, name='view_quizzes'),
    path('lesson/<int:question_id>/edit-question/', views.edit_question, name='edit_question'),
    path('lesson/<int:question_id>/delete-question/', views.delete_question, name='delete_question'),

    # Enrollments
    path('enrollments/', views.instructor_enrollments, name='instructor_enrollments'),
]
