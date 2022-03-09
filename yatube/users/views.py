from django.urls import reverse_lazy
from .forms import CreationForm
from django.views.generic import CreateView
from django.contrib.auth.views import (
    PasswordChangeView,
    PasswordResetView,
    PasswordResetConfirmView
)


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


class MyPasswordChange(PasswordChangeView):
    success_url = reverse_lazy('users:password_change_done')


class MyPasswordResetView(PasswordResetView):
    success_url = reverse_lazy('users:password_reset_done')


class MyPasswordResetConfirmView(PasswordResetConfirmView):
    success_url = reverse_lazy('users:password_reset_complete')
