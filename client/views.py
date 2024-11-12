from django.shortcuts import render, redirect, get_list_or_404
from .models import client

def client_list(request):
    clients = client.objects.all() #Puxar todos os dados da tabela de clients

