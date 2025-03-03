from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('verify-email/', views.verify_email_view, name='verify_email'),
    path("profile/", views.profile_view, name="profile"),
    path("addresses/", views.address_list_view, name="address_list"),
    path("addresses/add/", views.add_address_view, name="add_address"),
    path("addresses/edit/<int:address_id>/", views.edit_address_view, name="edit_address"),
    path("addresses/delete/<int:address_id>/", views.delete_address_view, name="delete_address"),
    path('youraccount/', views.your_account_view, name="youraccount"),
    path("security-settings/", views.security_settings_view, name="security_settings"),
    path('change-password/', views.change_password_view, name='change_password'),
    path('reset-password/', views.password_reset_request, name='password_reset'),
    path('reset-password-confirm/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
]