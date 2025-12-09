from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import CustomUser
from instructor.models import Course

def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('login')

    pending_instructors = CustomUser.objects.filter(role='instructor', is_approved=False)
    approved_instructors = CustomUser.objects.filter(role='instructor', is_approved=True)

    pending_courses = Course.objects.filter(approval_status='pending')
    approved_courses = Course.objects.filter(approval_status='approved')

    return render(request, 'admin/admin_dashboard.html', {
        'pending_instructors': pending_instructors,
        'approved_instructors': approved_instructors,
        'pending_courses': pending_courses,
        'approved_courses': approved_courses,
    })


def approve_instructor(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id, role='instructor')
    user.is_approved = True
    user.save()
    return redirect('admin_dashboard')

def reject_instructor(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id, role='instructor')
    user.delete()
    return redirect('admin_dashboard')

def approve_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    course.approval_status = 'approved'
    course.save()
    return redirect('admin_dashboard')

def reject_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    course.approval_status = 'rejected'
    course.save()
    return redirect('admin_dashboard')

