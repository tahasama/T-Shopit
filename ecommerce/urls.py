
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from shop import views


urlpatterns = [
    path('register/',views.CustomerRegistrationView.as_view(),name='registration'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='customer/login.html'),name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(),name='logout'),
    # change password urls
    path('accounts/password_change/',auth_views.PasswordChangeView.as_view(template_name='customer/password_change_form.html'),name='password_change'),
    path('accounts/password_change/done/',auth_views.PasswordChangeDoneView.as_view(template_name='customer/password_change_done.html'),name='password_change_done'),
    # reset password urls
    path('accounts/password_reset/',auth_views.PasswordResetView.as_view(template_name='customer/password_reset_form.html' ),name='password_reset'),
    path('accounts/password_reset/done/',auth_views.PasswordResetDoneView.as_view(template_name='customer/password_reset_done.html' ),name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name='customer/password_reset_confirm.html'),name='password_reset_confirm'),
    path('accounts/reset/done/',auth_views.PasswordResetCompleteView.as_view(template_name='customer/password_reset_complete.html'),name='password_reset_complete'),
    path('accounts/', include('django.contrib.auth.urls')),

    path('admin/', admin.site.urls),
    path('', include('shop.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)