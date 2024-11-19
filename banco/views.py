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
            # Aqui o form já é válido, então podemos criar e salvar o cliente
            cliente = form.save(commit=False)  # Não salva imediatamente, ainda podemos manipular
            cliente.set_password(form.cleaned_data['senha'])  # Define a senha criptografada
            cliente.save()  # Agora sim, salva o cliente no banco de dados
            
            return redirect('login')  # Redireciona para uma página de listagem de clientes
            
        else:
            print('Formulário inválido:', form.errors)  # Exibe os erros no console para debug

    else:
        form = ClienteForm()  # Formulário vazio na requisição GET
    
    return render(request, 'clientes/cadastro.html', {'form': form})

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