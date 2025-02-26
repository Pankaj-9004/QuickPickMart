from django.urls import path
from .views import signup_view, login_view, logout_view, verify_email_view

urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('verify-email/', verify_email_view, name='verify_email'),
]