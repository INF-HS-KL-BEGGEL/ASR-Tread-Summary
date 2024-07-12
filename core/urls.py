"""core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from admin_datta import views as admin_datta_views
from django.contrib.auth import views as auth_views

import home.views

urlpatterns = [
    path('', include('home.urls')),
    path('', admin_datta_views.index, name='index'),
    path('admin/logout/', admin_datta_views.logout_view, name='logout'),
    path('admin/login/', admin_datta_views.UserLoginView.as_view(), name='login'),

    # Authentication
    path('accounts/login/', admin_datta_views.UserLoginView.as_view(), name='login'),
    path('accounts/logout/', admin_datta_views.logout_view, name='logout'),

    path("admin/", admin.site.urls),

    # path('accounts/register/', admin_datta_views.UserRegistrationView.as_view(), name='register'),
    path('accounts/register/', admin_datta_views.UserLoginView.as_view(), name='register'),

    path('accounts/password-change/', admin_datta_views.UserPasswordChangeView.as_view(), name='password_change'),
    path('accounts/password-change-done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='accounts/auth-password-change-done.html'
    ), name="password_change_done"),

    path('accounts/password-reset/', admin_datta_views.UserPasswordResetView.as_view(), name='password_reset'),
    path('accounts/password-reset-confirm/<uidb64>/<token>/',
         admin_datta_views.UserPasswrodResetConfirmView.as_view(), name="password_reset_confirm"
         ),
    path('accounts/password-reset-done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/auth-password-reset-done.html'
    ), name='password_reset_done'),
    path('accounts/password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/auth-password-reset-complete.html'
    ), name='password_reset_complete'),

    path('profile/', admin_datta_views.profile, name='profile')
]
