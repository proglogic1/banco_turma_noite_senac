from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth import logout as auth_logout, authenticate, login as auth_login
from django.views import View
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm


# Create your views here.

def login_view(request):
    if request.method == 'POST':
        cpf = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, cpf=cpf, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('/')
        else:
            messages.error(request, 'Usuário ou senha inválidos.')
            return render(request, 'accounts/login.html', {'cpf': cpf})
    else:
        return render(request, 'accounts/login.html')

def cadastro(request):
    return render(request, 'accounts/cadastro.html')

def logout(request):
    logout(request)
    return redirect('login')