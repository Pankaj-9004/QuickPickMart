from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, SetPasswordForm
from .models import CustomUser, Profile, Address
from django_countries.widgets import CountrySelectWidget


# User Registeration Form
class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}))
    
    class Meta:
        model = CustomUser
        fields = ['firstname', 'lastname', 'username', 'email', 'password']
        widgets = {
            'firstname': forms.TextInput(attrs={'placeholder': 'First Name'}),
            'lastname': forms.TextInput(attrs={'placeholder': 'Last Name'}),
            'username': forms.TextInput(attrs={'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
        }
        
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data
    
    
# User Login Form(Using email instead of username)
class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Enter your email', 'class': 'form-control'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password', 'class': 'form-control'})
    )
    
    
# Email OTP Verification Form
class VerifyEmailForm(forms.Form):
    otp = forms.CharField(max_length=6, required=True)
    

# User Profile Form
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_picture', 'mobile_number', 'date_of_birth', 'gender']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter mobile number'}),
        }
        

# User Address Form
class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            'full_name', 'mobile_number', 'pincode', 'street_address', 'area', 'landmark', 'city', 'state', 'country', 'is_default'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Number'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'PIN Code'}),
            'street_address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Street Address', 'rows': 2}),
            'area': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Area Details', 'rows': 2}),
            'landmark': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Landmark (Optional)'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'state': forms.Select(attrs={'class': 'form-control'}),
            'country': CountrySelectWidget(attrs={'class': 'form-control'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        

# User Password Change Form
class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Current Password', 'class': 'form-control'})
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'New Password', 'class': 'form-control'})
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm New Password', 'class': 'form-control'})
    )
    
    class Meta:
        fields = ['old_password', 'new_password1', 'new_password2']
        

# User Password Request Form
class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label="Enter your email", widget=forms.EmailInput(attrs={"class": "form-control"}))


# User Set NewPassword Form
class SetNewPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(label="New Password", widget=forms.PasswordInput(attrs={"class": "form-control"}))
    new_password2 = forms.CharField(label="Confirm New Password", widget=forms.PasswordInput(attrs={"class": "form-control"}))