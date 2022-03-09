from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView
from userapp.forms import UserLoginForm


# Create your views here.
class LoginUserView(LoginView):
    template_name = 'userapp/login.html'
    form_class = UserLoginForm
