from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Cliente, Conta
from .forms import ClienteForm
import random
from .serializers import ClienteSerializer, ContaSerializer
from rest_framework import generics
from rest_framework.views import APIView

#@login_required
def gerar_numero_conta():
        while True:
            numero_conta = str(random.randint(10000, 99999))
            if not Conta.objects.filter(nr_conta=numero_conta).exists():
                return numero_conta

#@login_required
def cadastrar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save(commit=False)
            cliente.set_password(form.cleaned_data['senha'])  # Define a senha
            cliente.save()  # Agora sim, salva o cliente no banco de dados
            tipo_conta = form.cleaned_data['tipo_conta']
            
            # Criar automaticamente uma conta associada ao cliente
            Conta.objects.create(
                id_cliente=cliente,
                nr_conta=gerar_numero_conta(),
                nr_agencia="0001",
                tipo_conta=tipo_conta  # ou 'Poupanca', conforme necessário
            )
            
            return redirect('listar_clientes_contas')  # Redireciona para uma página de listagem de clientes
    else:
        form = ClienteForm()
    
    return render(request, 'clientes/cadastrar_cliente.html', {'form': form})

#@login_required
def listar_clientes_contas(request):
    clientes = Cliente.objects.all()
    contas = Conta.objects.select_related('id_cliente').all()
    context = {
        'clientes': clientes,
        'contas': contas
    }
    return render(request, 'clientes/listar_clientes_contas.html', context)

#API
# View para listar e criar clientes
class ClienteListCreateView(generics.ListCreateAPIView):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer

# View para listar e criar contas
class ContaListCreateView(generics.ListCreateAPIView):
    queryset = Conta.objects.select_related('id_cliente')  # Otimiza a consulta para incluir dados do cliente
    serializer_class = ContaSerializer

class ClienteCreateAPIView(APIView):
    def post(self, request):
        serializer = ClienteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)