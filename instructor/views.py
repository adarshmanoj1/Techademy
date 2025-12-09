from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import InstructorRegistrationForm, LessonForm, InstructorProfileForm, CourseForm, QuestionForm, ChoiceFormSet
from .models import Course, Lesson, Question, Choice
from student.models import Enrollment
from django.forms import inlineformset_factory

@login_required
def instructor_dashboard(request):
    if request.user.role != 'instructor':
        return redirect('login')

    approved_courses = Course.objects.filter(instructor=request.user, approval_status='approved')
    pending_courses = Course.objects.filter(instructor=request.user, approval_status='pending')
    rejected_courses = Course.objects.filter(instructor=request.user, approval_status='rejected')

    return render(request, 'instructor/instructor_dashboard.html', {
        'approved_courses': approved_courses,
        'pending_courses': pending_courses,
        'rejected_courses': rejected_courses,
    })

def register_instructor(request):
    if request.method == 'POST':
        form = InstructorRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Instructor registered. Awaiting admin approval.")
            return redirect('login')
    else:
        form = InstructorRegistrationForm()

    return render(request, 'instructor/register_instructor.html', {'form': form})

@login_required
def instructor_profile(request):
    if request.user.role != 'instructor':
        return redirect('login')

    if request.method == 'POST':
        form = InstructorProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('instructor_profile')
    else:
        form = InstructorProfileForm(instance=request.user)

    return render(request, 'instructor/instructor_profile.html', {'form': form})

@login_required
def add_course(request):
    if request.user.role != 'instructor':
        return redirect('login')

    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            messages.success(request, 'Course added successfully. Awaiting admin approval.')
            return redirect('instructor_dashboard')
    else:
        form = CourseForm()

    return render(request, 'instructor/add_course.html', {'form': form})

@login_required
def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)

    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated successfully.')
            return redirect('course_detail', course_id=course.id)
    else:
        form = CourseForm(instance=course)

    return render(request, 'instructor/edit_course.html', {
        'form': form,
        'course': course
    })

@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    lessons = course.lessons.all()
    return render(request, 'instructor/course_detail.html', {
        'course': course,
        'lessons': lessons
    })

@login_required
def instructor_course_list(request):
    if request.user.role != 'instructor':
        return redirect('login')

    approved_courses = Course.objects.filter(instructor=request.user, approval_status='approved')
    pending_courses = Course.objects.filter(instructor=request.user, approval_status='pending')
    rejected_courses = Course.objects.filter(instructor=request.user, approval_status='rejected')

    return render(request, 'instructor/courses_overview.html', {
        'approved_courses': approved_courses,
        'pending_courses': pending_courses,
        'rejected_courses': rejected_courses,
    })

@login_required
def add_lesson(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user, approval_status='approved')
    lesson_added = None

    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.course = course
            lesson.save()
            lesson_added = lesson
            form = LessonForm()
    else:
        form = LessonForm()

    return render(request, 'instructor/add_lesson.html', {
        'form': form,
        'course': course,
        'lesson_added': lesson_added
    })

@login_required
def edit_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id, course__instructor=request.user)
    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lesson updated successfully.')
            return redirect('course_detail', course_id=lesson.course.id)
    else:
        form = LessonForm(instance=lesson)

    return render(request, 'instructor/edit_lesson.html', {
        'form': form,
        'lesson': lesson,
        'course': lesson.course,
    })

@login_required
def manage_lessons(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user, approval_status='approved')
    lessons = Lesson.objects.filter(course=course)
    return render(request, 'instructor/add_lesson.html', {'course': course, 'lessons': lessons})

@login_required
def select_course_for_lessons(request):
    if request.user.role != 'instructor':
        return redirect('login')

    courses = Course.objects.filter(instructor=request.user, approval_status='approved')
    return render(request, 'instructor/select_course_for_lessons.html', {'courses': courses})

@login_required
def delete_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id, course__instructor=request.user)
    course_id = lesson.course.id
    lesson.delete()
    messages.success(request, 'Lesson deleted successfully.')
    return redirect('course_detail', course_id=course_id)

@login_required
def add_question_with_choices(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id, course__instructor=request.user)

    if request.method == 'POST':
        q_form = QuestionForm(request.POST)
        c_formset = ChoiceFormSet(request.POST)

        if q_form.is_valid() and c_formset.is_valid():
            question = q_form.save(commit=False)
            question.lesson = lesson
            question.save()

            choices = c_formset.save(commit=False)
            for choice in choices:
                choice.question = question
                choice.save()

            messages.success(request, "Question and choices added successfully.")
            return redirect('course_detail', course_id=lesson.course.id)

    else:
        q_form = QuestionForm()
        c_formset = ChoiceFormSet()

    return render(request, 'instructor/add_question_with_choices.html', {
        'lesson': lesson,
        'q_form': q_form,
        'c_formset': c_formset
    })

@login_required
def view_quizzes(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id, course__instructor=request.user)
    questions = Question.objects.filter(lesson=lesson).prefetch_related('choices')

    return render(request, 'instructor/lesson_quiz_list.html', {
        'lesson': lesson,
        'questions': questions
    })

@login_required
def edit_question(request, question_id):
    question = get_object_or_404(Question, id=question_id, lesson__course__instructor=request.user)
    ChoiceFormSet = inlineformset_factory(Question, Choice, fields=('text', 'is_correct'), extra=0, can_delete=True)

    if request.method == 'POST':
        q_form = QuestionForm(request.POST, instance=question)
        c_formset = ChoiceFormSet(request.POST, instance=question)

        if q_form.is_valid() and c_formset.is_valid():
            q_form.save()
            c_formset.save()
            messages.success(request, "Quiz updated successfully.")
            return redirect('manage_lessons', course_id=question.lesson.course.id)
    else:
        q_form = QuestionForm(instance=question)
        c_formset = ChoiceFormSet(instance=question)

    return render(request, 'instructor/edit_question.html', {
        'q_form': q_form,
        'c_formset': c_formset,
        'question': question,
    })

@login_required
def delete_question(request, question_id):
    question = get_object_or_404(Question, id=question_id, lesson__course__instructor=request.user)
    course_id = question.lesson.course.id
    question.delete()
    messages.success(request, "Quiz deleted successfully.")
    return redirect('course_detail', course_id=course_id)

@login_required
def instructor_enrollments(request):
    if request.user.role != 'instructor':
        return redirect('login')

    courses = Course.objects.filter(instructor=request.user, approval_status='approved')

    course_data = []
    for course in courses:
        enrollments = Enrollment.objects.filter(course=course)
        students = [enrollment.student for enrollment in enrollments]
        course_data.append({
            'course': course,
            'enrollments': enrollments,
            'students': students,
            'count': enrollments.count()
        })

    return render(request, 'instructor/instructor_enrollments.html', {
        'course_data': course_data
    })


