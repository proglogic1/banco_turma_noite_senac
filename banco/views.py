from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Cliente, Conta
from .forms import ClienteForm, ContaForm,SaldoForm
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

# @login_required  # Descomente se necessário
def cadastrar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        
        if form.is_valid():
            # Salva o cliente
            cliente = form.save(commit=False)
            cliente.set_password(form.cleaned_data['senha'])  # Define a senha criptografada
            cliente.save()
            
            # Cria a conta associada ao cliente
            numero_conta = gerar_numero_conta()  # Gera um número único de conta
            conta = Conta.objects.create(
                id_cliente=cliente,
                nr_conta=numero_conta,
                nr_agencia="001",  # Defina um valor padrão ou gere dinamicamente
                tipo_conta="Corrente"  # Você pode ajustar para um valor padrão ou capturar do formulário
            )
            
            return redirect('menu')  # Redireciona após o cadastro
        
        else:
            print('Formulário inválido:', form.errors)  # Exibe erros para debug

    else:
        form = ClienteForm()  # Cria um formulário vazio para GET
    
    return render(request, 'clientes/cadastro.html', {'form': form})

def cadastrar_conta(request):
    if request.method == 'POST':
        form = ContaForm(request.POST)
        if form.is_valid():
            # numero_conta = gerar_numero_conta()  # Gera um número único de conta
            # nova_conta = form.save(commit=False)  # Não salva ainda no banco
            # nova_conta.id_cliente = request.user  # Associa a conta ao cliente autenticado
            # nova_conta.save()  # Salva a nova conta com o número gerado automaticamente
            numero_conta = gerar_numero_conta()  # Gera um número único de conta
            conta = Conta.objects.create(
                id_cliente=request.user,
                nr_conta=numero_conta,
                nr_agencia="001",  # Defina um valor padrão ou gere dinamicamente
                tipo_conta=form.cleaned_data['tipo_conta']  # Você pode ajustar para um valor padrão ou capturar do formulário
            )
            return redirect('listar_clientes_contas')  # Redireciona para a página de listagem das contas
    else:
        form = ContaForm()

    return render(request, 'clientes/cadastrar_conta.html', {'form': form})

@login_required
def listar_clientes_contas(request):
    # Filtra as contas com base no cliente autenticado
    contas = Conta.objects.filter(id_cliente=request.user)  # 'request.user' é o cliente autenticado
    return render(request, 'clientes/listar_clientes_contas.html', {'contas': contas})



@login_required
def editar_saldo(request, conta_id):
    # Recupera todas as contas do cliente autenticado
    contas = Conta.objects.filter(id_cliente=request.user)

    if request.method == 'POST':
        # Recupera o ID da conta e o novo saldo do formulário
        conta_id = request.POST.get('conta_id')
        novo_saldo = request.POST.get('novo_saldo')

        # Verifica se a conta foi selecionada e o saldo foi informado
        if conta_id and novo_saldo:
            conta = Conta.objects.get(id_conta=conta_id)
            conta.saldo = novo_saldo
            conta.save()
            return redirect('menu')  # Redireciona para o menu após a atualização

    return render(request, 'clientes/editar_saldo.html', {'contas': contas})

def menu(request):
   # Verifica se a conta foi selecionada e salva na sessão
    if request.method == 'POST':
        conta_id = request.POST.get('conta_id')
        if conta_id:
            request.session['conta_selecionada'] = conta_id  # Salva a conta selecionada na sessão

    # Verifica se há uma conta selecionada na sessão
    conta_selecionada = None
    if 'conta_selecionada' in request.session:
        conta_selecionada = Conta.objects.get(id=request.session['conta_selecionada'])

    # Pega todas as contas do cliente
    contas = Conta.objects.filter(id_cliente=request.user)

    # Pega o saldo da conta selecionada
    saldo = conta_selecionada.saldo if conta_selecionada else 0.00

    return render(request, 'clientes/menu.html', {
        'contas': contas,
        'conta_selecionada': conta_selecionada,
        'saldo': saldo
    })

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