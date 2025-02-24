from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import CustomUser


# User Registeration Form
class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:
        model = CustomUser
        fields = ['firstname', 'lastname', 'username', 'email', 'mobile_number', 'password']
        
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data
    
    
# User Login Form(Using email instead of username)
class LoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email")
    
    
#  Mobile OTP Verification Form
class VerifyMobileForm(forms.Form):
    otp = forms.CharField(max_length=6, required=True)