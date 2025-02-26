from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from .models import CustomUser
from .forms import SignupForm, LoginForm, VerifyEmailForm

# Create your views here.

# Generate and send OTP
def send_otp_email(user):
    otp = get_random_string(length=6, allowed_chars="0123456789")
    user.email_otp = otp
    user.save()
    
    subject = "Email Verification OTP"
    message = f"Your OTP for email verification is: {otp}"
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
    
    
# Signup View
def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            print("Form is valid")
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            print(f"User {user.email} saved, sending OTP...")
            send_otp_email(user)
            request.session['user_email'] = user.email
            print("Redirecting to verify email page")
            return redirect('verify_email') # Redirect to OTP verification page
        else:
            print("Form is not valid:", form.errors)
    else:
        form = SignupForm()
    return render(request, 'authentication/signup.html', {'form': form})


# Email OTP Verification View
def verify_email_view(request):
    email = request.session.get('user_email')
    if not email:
        messages.error(request, "No email found in session. Please sign up again.")
        return redirect('signup')
    
    user = CustomUser.objects.filter(email=email).first()
    if not user:
        messages.error(request, "User not found. Please sign up again.")
        return redirect('signup')
    
    if request.method == "POST":
        form = VerifyEmailForm(request.POST)
        if form.is_valid():
            entered_otp = form.cleaned_data['otp']
            user.email_verified = True
            user.is_active = True
            user.email_otp = None
            user.save()
            messages.success(request, "Email verified successfully. You can now log in.")
            return redirect('login')
        else:
            messages.error(request, "Invalid OTP. Please try again.")
    else:
        form = VerifyEmailForm()
    return render(request, 'authentication/verify_email.html', {'form': form})


# Resend OTP View
def resend_otp_view(request):
    email = request.session.get('user_email')
    if email:
        user = CustomUser.objects.filter(email=email).first()
        if user:
            send_otp_email(user)
            messages.success(request, "A new OTP has been sent to your email.")
        else:
            messages.error(request, "User not found")
    else:
        messages.error(request, "No email found in session. Please sign up again.")
    return redirect('verify_email')


# Login View
def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user:
                login(request, user)
                messages.success(request, "Login successful.")
                return redirect('home')
            else:
                messages.error(request, "Invalid credentials.")
    else:
        form = LoginForm()
    return render(request, 'authentication/login.html', {'form': form})


# Logout View
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')