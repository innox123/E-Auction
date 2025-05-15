from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', include('auctions.urls')),
    path('account/', include('account.urls')),
    path('admin/dashboard/', include('admin_site.urls')),

    path("resetpassword/", auth_views.PasswordResetView.as_view(template_name='users/password_reset.html'), name="password_reset"),
    path("resetpasswordsent/", auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_sent.html'), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'), name="password_reset_confirm"),
    path("resetpasswordcomplete/", auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), name="password_reset_complete")
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)