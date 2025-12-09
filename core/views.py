from django.shortcuts import render
from accounts.models import CustomUser
from instructor.models import Course

def homepage(request):
    courses = Course.objects.filter(approval_status='approved', instructor__is_approved=True)
    instructors = CustomUser.objects.filter(role='instructor', is_approved=True)
    return render(request, 'home.html', {
        'courses': courses,
        'instructors': instructors,
    })

