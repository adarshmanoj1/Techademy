from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from accounts.models import CustomUser

# Student Registration

def register_student(request):
    if request.method == 'POST':
        full_name = request.POST['full_name']
        email = request.POST['email']
        phone = request.POST['phone']
        place = request.POST.get('place', '')
        education = request.POST.get('education', '')
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('register_student')

        if CustomUser.objects.filter(username=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('register_student')

        user = CustomUser.objects.create_user(
            username=email,
            email=email,
            first_name=full_name,
            phone=phone,
            place=place,
            education=education,
            role='student',
            password=password1,
            is_approved=True  # auto-approved
        )
        messages.success(request, "Registration successful. Please login.")
        return redirect('login')

    return render(request, 'student/register_student.html')

# instructor Registration

def register_instructor(request):
    if request.method == 'POST':
        full_name = request.POST['full_name']
        email = request.POST['email']
        phone = request.POST['phone']
        place = request.POST.get('place', '')
        qualification = request.POST.get('qualification', '')
        profile_image = request.FILES.get('profile_image')
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('register_instructor')

        if CustomUser.objects.filter(username=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, 'instructor/register_instructor.html')


        user = CustomUser.objects.create_user(
            username=email,
            email=email,
            first_name=full_name,
            phone=phone,
            place=place,
            qualification=qualification,
            profile_image=profile_image,
            role='instructor',
            password=password1,
            is_approved=False  # admin approval needed
        )
        messages.success(request, "Registration successful. Awaiting admin approval.")
        return redirect('login')

    return render(request, 'instructor/register_instructor.html')


# Login View
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            if user.role == 'instructor' and not user.is_approved:
                messages.warning(request, "Instructor account not approved yet.")
                return redirect('login')

            login(request, user)

            if user.role == 'admin':
                return redirect('admin_dashboard')
            elif user.role == 'instructor':
                return redirect('instructor_dashboard')
            elif user.role == 'student':
                return redirect('student_dashboard')
        else:
            messages.error(request, "Invalid credentials.")
            return redirect('login')

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')