from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Cliente, Conta
from .forms import ClienteForm
import random
from .serializers import ClienteSerializer, ContaSerializer
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
import requests  # type: ignore

#@login_required
def gerar_numero_conta():
        while True:
            numero_conta = str(random.randint(10000, 99999))
            if not Conta.objects.filter(nr_conta=numero_conta).exists():
                return numero_conta

#==================================================#

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

#==================================================#

#@login_required
def listar_clientes_contas(request):
    clientes = Cliente.objects.all()
    contas = Conta.objects.select_related('id_cliente').all()
    context = {
        'clientes': clientes,
        'contas': contas
    }
    return render(request, 'clientes/listar_clientes_contas.html', context)

#==================================================#
#API
# View para listar e criar clientes
class ClienteListCreateView(generics.ListCreateAPIView):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer

#==================================================#

# View para listar e criar contas
class ContaListCreateView(generics.ListCreateAPIView):
    queryset = Conta.objects.select_related('id_cliente')  # Otimiza a consulta para incluir dados do cliente
    serializer_class = ContaSerializer

#==================================================#
class ClienteCreateAPIView(APIView):
    def post(self, request):
        serializer = ClienteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED) # type: ignore
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) # type: ignore

#==================================================#

@api_view(['GET'])
def Buscar_Cep(request):
    CEP = request.query_params.get('cep')
    
    if not CEP:
        return Response({"error": "CEP não informado"}, status=400)
#---------------------------------------------------#
    #Validando o formato do CEP, se ele contém 8 digitos
    if not CEP.isdigit() or len(CEP) !=8: 
        return Response({"error" : "CEP inválido"}, status=400)
#---------------------------------------------------#
    #Cunsultando o CEP
    url = f'https://viacep.com.br/ws/{CEP}/json/'
    response = requests.get(url)
#---------------------------------------------------#
    #Verificando se o serviço retornou com sucesso
    if response.status_code !=200:
        return Response({"error": "erro ao consultar o CEP"}, status=500)

    data = response.json()
#---------------------------------------------------#
    #Caso o CEP não seja encontrado ou esteja inválido
    if 'erro' in data:
        return Response({"error":"CEP não encontrado"}, status=404)
    return Response(data)


def endereco(request):
    return render(request, 'localizacao/localizacao.html')