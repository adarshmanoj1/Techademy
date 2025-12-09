from io import BytesIO

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db.models import Q
from django.http import FileResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.timezone import now, timezone

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors

from instructor.models import Course, Lesson, Question, Choice
from .models import Enrollment, LessonProgress, Certificate, QuizScore
from .forms import StudentProfileForm


# Dashboard & Profile

@login_required
def student_dashboard(request):
    enrollments = Enrollment.objects.filter(student=request.user).select_related('course')
    dashboard_data = []

    for enrollment in enrollments:
        course = enrollment.course
        lessons = course.lessons.all()
        total_lessons = lessons.count()

        completed_ids = LessonProgress.objects.filter(
            student=request.user, lesson__in=lessons, is_completed=True
        ).values_list('lesson_id', flat=True)

        completed_count = len(completed_ids)
        progress = int((completed_count / total_lessons) * 100) if total_lessons else 0
        next_lesson = lessons.exclude(id__in=completed_ids).order_by('id').first() or lessons.first()

        dashboard_data.append({
            'course': course,
            'progress': progress,
            'next_lesson': next_lesson
        })

    return render(request, 'student/student_dashboard.html', {'enrollments': dashboard_data})


@login_required
def edit_student_profile(request):
    if request.method == 'POST':
        form = StudentProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('student_dashboard')
    else:
        form = StudentProfileForm(instance=request.user)

    return render(request, 'student/edit_profile.html', {'form': form})


# Course Browsing & Enrollment

def browse_courses(request):
    query = request.GET.get('q', '')
    courses = Course.objects.filter(approval_status='approved')

    if query:
        courses = courses.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(category__icontains=query)
        )

    return render(request, 'student/browse_courses.html', {'courses': courses, 'query': query})


def course_detail_student(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    is_enrolled = Enrollment.objects.filter(course=course, student=request.user).exists()
    lessons = Lesson.objects.filter(course=course)

    completed = LessonProgress.objects.filter(
        student=request.user, lesson__in=lessons, is_completed=True
    ).values_list('lesson_id', flat=True)

    return render(request, 'student/course_detail.html', {
        'course': course,
        'is_enrolled': is_enrolled,
        'lessons': lessons,
        'completed_lessons': completed,
    })


@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, approval_status='approved')
    if not Enrollment.objects.filter(student=request.user, course=course).exists():
        Enrollment.objects.create(student=request.user, course=course)
        messages.success(request, 'Successfully enrolled in the course!')
    else:
        messages.info(request, 'You are already enrolled in this course.')

    return redirect('course_detail_student', course_id=course.id)


# Lesson & Quiz

@login_required
def view_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course = lesson.course

    if not Enrollment.objects.filter(student=request.user, course=course).exists():
        messages.error(request, "You are not enrolled in this course.")
        return redirect('student_dashboard')

    LessonProgress.objects.update_or_create(
        student=request.user,
        lesson=lesson,
        defaults={'is_completed': True, 'watched_on': timezone.now()}
    )

    questions = Question.objects.filter(lesson=lesson).prefetch_related('choices')

    return render(request, 'student/view_lesson.html', {
        'lesson': lesson,
        'course': course,
        'questions': questions,
        'youtube_link': lesson.youtube_link
    })


@login_required
def take_quiz(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    questions = Question.objects.filter(lesson=lesson).prefetch_related('choices')
    total = questions.count()
    correct = 0
    incorrect_answers = []

    if request.method == 'POST':
        for question in questions:
            selected_id = request.POST.get(f'question_{question.id}')
            selected_choice = Choice.objects.filter(id=selected_id).first() if selected_id else None
            correct_choice = question.choices.filter(is_correct=True).first()

            if selected_choice and selected_choice.is_correct:
                correct += 1
            else:
                incorrect_answers.append({
                    'question': question.text,
                    'your_answer': selected_choice.text if selected_choice else "No answer",
                    'correct_answer': correct_choice.text if correct_choice else "N/A"
                })

        QuizScore.objects.update_or_create(
            student=request.user,
            lesson=lesson,
            defaults={'score': correct, 'total': total, 'is_perfect': correct == total}
        )

        return render(request, 'student/quiz_result.html', {
            'score': correct,
            'total': total,
            'incorrect_answers': incorrect_answers,
            'is_perfect': correct == total,
            'course': lesson.course
        })

    return render(request, 'student/take_quiz.html', {'lesson': lesson, 'questions': questions})


# Certificate

@login_required
def student_certificates(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    lessons = Lesson.objects.filter(course=course)
    total_lessons = lessons.count()

    completed = LessonProgress.objects.filter(
        student=request.user, lesson__in=lessons, is_completed=True
    ).count()

    if completed < total_lessons:
        messages.error(request, "Please complete all lessons before requesting a certificate.")
        return redirect('student_dashboard')

    for lesson in lessons:
        total_qs = Question.objects.filter(lesson=lesson).count()
        score_obj = QuizScore.objects.filter(student=request.user, lesson=lesson).first()

        if not score_obj or score_obj.score < total_qs:
            messages.error(request, f"You must score full marks in the quiz for: {lesson.title}")
            return redirect('student_dashboard')

    cert, created = Certificate.objects.get_or_create(student=request.user, course=course)

    if not cert.certificate_file:
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=landscape(A4))
        width, height = landscape(A4)

        # Certificate Design
        p.setStrokeColor(colors.HexColor("#00C6FF"))
        p.setLineWidth(6)
        p.rect(40, 40, width - 80, height - 80)

        p.setFont("Helvetica-Bold", 36)
        p.setFillColor(colors.HexColor("#00C6FF"))
        p.drawCentredString(width / 2, height - 100, "Certificate of Completion")

        p.setFont("Helvetica", 18)
        p.setFillColor(colors.black)
        p.drawCentredString(width / 2, height - 160, "This is to certify that")

        p.setFont("Helvetica-Bold", 26)
        p.setFillColor(colors.darkblue)
        p.drawCentredString(width / 2, height - 210, request.user.get_full_name())

        p.setFont("Helvetica", 18)
        p.setFillColor(colors.black)
        p.drawCentredString(width / 2, height - 260, "has successfully completed the course")

        p.setFont("Helvetica-Bold", 24)
        p.setFillColor(colors.HexColor("#0072ff"))
        p.drawCentredString(width / 2, height - 310, course.title)

        p.setFont("Helvetica", 14)
        p.setFillColor(colors.gray)
        p.drawCentredString(width / 2, height - 370, f"Issued on: {now().strftime('%d %B %Y')}")

        p.setFont("Helvetica-Oblique", 12)
        p.setFillColor(colors.gray)
        p.drawString(100, 80, "Signature:")
        p.line(160, 82, 300, 82)

        p.showPage()
        p.save()
        buffer.seek(0)

        cert.certificate_file.save(
            f'{request.user.username}_{course.title}_certificate.pdf',
            ContentFile(buffer.read())
        )
        cert.save()

    cert_url = default_storage.url(cert.certificate_file.name)

    return render(request, 'student/certificate_success.html', {
        'course': course,
        'certificate_url': cert_url
    })

@login_required
def start_payment(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if course.price == 0:
        return redirect('enroll_course', course_id=course.id)

    if request.method == "POST":
        Enrollment.objects.get_or_create(student=request.user, course=course)
        messages.success(request, "Payment successful! You're now enrolled.")
        return redirect('student_dashboard')

    return render(request, 'student/payment.html', {'course': course})


def logout_student(request):
    logout(request)
    return redirect('login')
