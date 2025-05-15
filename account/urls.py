from django.urls import path
from .views import *

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/',get_signup_page, name='register'),
    path('verify-code/', verify_code, name='verify_code'),
    path('dashboard/', dashboard, name='dashboard'),
    path('profile/', profile, name='profile'),
    path('bid_history/', bid_history, name='bid-history'),
    path('password-change/', change_password, name='password_change'),
    # path('password-reset/', ResetPasswordView.as_view(), name='password_reset'),
    path('notification/', get_notification, name='notification'),
    path('delete_notification/<int:notification_id>/', delete_notification, name='delete_notification'),
    path('payments/<str:transaction_id>', payments, name='payments'),
    path('settings/', get_settings, name='settings'),
    path('store/', store, name='store'),
  
]