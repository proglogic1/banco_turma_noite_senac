from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth import logout, authenticate, login as auth_login
from django.views import View
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm


# Create your views here.

def login_view(request):
    if request.method == 'POST':
        cpf = request.POST['cpf']
        password = request.POST['password']
        
        user = authenticate(request, cpf=cpf, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('menu')
        else:
            messages.error(request, 'Usuário ou senha inválidos.')
            return render(request, 'accounts/login.html', {'cpf': cpf})
    else:
        return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')