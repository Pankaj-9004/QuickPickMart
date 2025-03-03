from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, get_user_model, update_session_auth_hash
from django.contrib import messages
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.utils.crypto import get_random_string
from .models import CustomUser, Profile, Address, INDIAN_STATES
from .forms import SignupForm, LoginForm, VerifyEmailForm, ProfileForm, AddressForm, CustomPasswordChangeForm, PasswordResetRequestForm, SetNewPasswordForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.utils.html import strip_tags

# Create your views here.

# Generate and send OTP
def send_otp_email(user):
    otp = get_random_string(length=6, allowed_chars="0123456789")
    user.email_otp = otp
    user.save()
    
    subject = "QuickPickMart: Email Verification OTP"
    html_message = render_to_string("authentication/email_otp_template.html", {"otp": otp, "user": user})
    plain_message = strip_tags(html_message)  # Fallback for email clients that don’t support HTML
    
    email = EmailMultiAlternatives(subject, plain_message, settings.DEFAULT_FROM_EMAIL, [user.email])
    email.attach_alternative(html_message, "text/html")
    email.send()
    
    
# Signup View
def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)  # Create user instance but don't save yet
            user.set_password(form.cleaned_data['password'])  # Hash the password
            user.is_active = False  # Inactive until email is verified
            user.save()  # Save user with hashed password
            send_otp_email(user)  # Send OTP for email verification
            request.session['user_email'] = user.email  # Store email in session
            return redirect('verify_email')  # Redirect to OTP verification page
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
            email = form.cleaned_data['username']  # Using email as username
            password = form.cleaned_data['password']
            # Check if user exists
            User = get_user_model()
            user = User.objects.filter(email=email).first()
            if user and not user.is_active:
                messages.error(request, "Your account is not activated. Please verify your email.")
                return render(request, 'authentication/login.html', {'form': form})
            # Authenticate user
            user = authenticate(request, email=email, password=password)
            if user:
                login(request, user)
                messages.success(request, "Login successful.")
                return redirect('home')
            else:
                messages.error(request, "Invalid email or password.")
    else:
        form = LoginForm()
    return render(request, 'authentication/login.html', {'form': form})


# Logout View
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')


# Profile View
@login_required
def profile_view(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)
    if request.method == "POST":
        if "update_photo" in request.POST:
            # If updating only profile picture
            profile.profile_picture = request.FILES.get("profile_picture", profile.profile_picture)
            profile.save()
            messages.success(request, "Profile picture updated successfully.")
            return redirect("profile")
        else: 
            new_username = request.POST.get("username", "").strip()
            # Ensure the username is unique (excluding the current user's username)
            if CustomUser.objects.exclude(id=user.id).filter(username=new_username).exists():
                messages.error(request, "This username is already taken. Please choose another.")
            else:
                user.username = new_username
                user.save()
                form = ProfileForm(request.POST, request.FILES, instance=profile)
                if form.is_valid():
                    form.save()
                    messages.success(request, "Profile updated successfully.")
                    return redirect("profile")
    else:
        form = ProfileForm(instance=profile)
    return render(request, "authentication/profile.html", {"form": form})

# Displays all saved addresses.
@login_required
def address_list_view(request):
    addresses = Address.objects.filter(user=request.user)
    return render(request, "authentication/address_list.html", {"addresses": addresses})


# Enables users to add a new address.
@login_required
def add_address_view(request):
    if request.method == "POST":
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user  # Assign the logged-in user
            address.save()
            messages.success(request, "New address added successfully.")
            return redirect("address_list")
    else:
        form = AddressForm()
    return render(request, "authentication/address_form.html", {"form": form, "INDIAN_STATES": INDIAN_STATES})


# Lets users update existing addresses
@login_required
def edit_address_view(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    if request.method == "POST":
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, "Address updated successfully.")
            return redirect("address_list")
    else:
        form = AddressForm(instance=address)
    return render(request, "authentication/address_form.html", {"form": form})


# Allows users to remove an address
@login_required
def delete_address_view(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    if request.method == "POST":
        address.delete()
        messages.success(request, "Address deleted successfully.")
        return redirect("address_list")
    return render(request, "authentication/address_delete.html", {"address": address})

# Allows users to use sections in your accounts
def your_account_view(request):
    return render(request, "authentication/your_account.html")


# Allows users to use security settings
@login_required
def security_settings_view(request):
    return render(request, "authentication/security_settings.html")


# Allows users to change password
@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep the user logged in after password change
            messages.success(request, "Your password has been changed successfully.")
            return redirect('security_settings')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomPasswordChangeForm(user=request.user)

    return render(request, 'authentication/change_password.html', {'form': form})


# Allows users to reset password
User = get_user_model()
def password_reset_request(request):
    if request.method == "POST":
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            user = User.objects.filter(email=email).first()
            if user:
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                reset_url = request.build_absolute_uri(reverse("password_reset_confirm", args=[uid, token]))
                
                # Send reset email
                subject = "QuickPickMArt: Password Reset Request"
                message = render_to_string("authentication/password_reset_email.html", {
                    "user": user,
                    "reset_url": reset_url
                })
                send_mail(subject, "", settings.DEFAULT_FROM_EMAIL, [user.email], html_message=message)
            
            messages.success(request, "If an account with this email exists, you will receive a reset link shortly.")
            return redirect("password_reset")
    else:
        form = PasswordResetRequestForm()
    
    return render(request, "authentication/password_reset.html", {"form": form})


# Password reset confirmation
def password_reset_confirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError):
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == "POST":
            form = SetNewPasswordForm(user, request.POST)  # Pass `user` here
            if form.is_valid():
                new_password = form.cleaned_data["new_password1"]
                user.set_password(new_password)
                user.save()
                messages.success(request, "Your password has been successfully reset.")
                return redirect("login")
        else:
            form = SetNewPasswordForm(user)  # Pass `user` here for GET request

        return render(request, "authentication/password_reset_confirm.html", {"form": form})

    messages.error(request, "Invalid or expired reset link.")
    return redirect("password_reset")