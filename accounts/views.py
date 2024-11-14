from django.shortcuts import render

# Create your views here.

def login(request):
    return render(request, 'accounts/login.html')

def cadastro(request):
    return render(request, 'accounts/cadastro.html')