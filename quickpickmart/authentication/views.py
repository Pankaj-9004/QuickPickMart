from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from .models import CustomUser, Profile, Address
from .forms import SignupForm, LoginForm, VerifyEmailForm, ProfileForm, AddressForm
from django.contrib.auth.decorators import login_required

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
    """View to display and update user profile, ensuring username uniqueness."""
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == "POST":
        if "update_photo" in request.POST:
            # If updating only profile picture
            profile.profile_picture = request.FILES.get("profile_picture", profile.profile_picture)
            profile.save()
            messages.success(request, "Profile picture updated successfully.")
            return redirect("profile")

        else:  # Updating other fields
            new_username = request.POST.get("username", "").strip()

            # Ensure the username is unique (excluding the current user's username)
            if CustomUser.objects.exclude(id=user.id).filter(username=new_username).exists():
                messages.error(request, "This username is already taken. Please choose another.")
            else:
                user.username = new_username  # Update username
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
    return render(request, "authentication/address_form.html", {"form": form})


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
    """View to delete an address."""
    address = get_object_or_404(Address, id=address_id, user=request.user)
    if request.method == "POST":
        address.delete()
        messages.success(request, "Address deleted successfully.")
        return redirect("address_list")
    return render(request, "authentication/address_delete.html", {"address": address})