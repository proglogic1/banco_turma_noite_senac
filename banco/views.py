from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Cliente, Conta
from .forms import ClienteForm, ContaForm,ClienteAlterarForm, TransacaoForm
from .utils import gerar_numero_conta, calcular_saldo_total, verificar_tipo_conta_existe, verificar_conta_existe, verificar_cpf_existente, verificar_email
from .models import Cliente, Conta, Movimento
from .forms import ClienteForm, ContaForm,ClienteAlterarForm
import random
from .serializers import ClienteSerializer, ContaSerializer
from rest_framework import generics,response,status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
import requests  # type: ignore
from datetime import time
from django.contrib import messages


#@login_required
def gerar_numero_conta():
        while True:
            numero_conta = str(random.randint(10000, 99999))
            if not Conta.objects.filter(nr_conta=numero_conta).exists():
                return numero_conta

from django.contrib import messages
from decimal import Decimal
from django.http import Http404





 
def cadastrar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)

        

        cpf =  request.POST.get('cpf')
        email = request.POST.get('email')

        if verificar_cpf_existente(request,cpf):
            return render(request, 'clientes/cadastro.html', {'form': form})

        if verificar_email(request,email):
            return render(request, 'clientes/cadastro.html', {'form': form})

        if form.is_valid():
             # Aqui o form já é válido, então podemos criar e salvar o cliente
            cliente = form.save(commit=False)  # Não salva imediatamente, ainda podemos manipular
            cliente.set_password(form.cleaned_data['senha'])  # Define a senha criptografada
            cliente.save()  # Agora sim, salva o cliente no banco de dados
            
                
            
            numero_conta = gerar_numero_conta()  # Gera um número único de conta
            conta = Conta.objects.create(
                id_cliente=cliente,
                nr_conta=numero_conta,
                nr_agencia="001",  # Defina um valor padrão ou gere dinamicamente
                tipo_conta=form.cleaned_data['tipo_conta']  # Você pode ajustar para um valor padrão ou capturar do formulário
            )
            

            return redirect('login')  # Redireciona para uma página de listagem de clientes

            messages.success(request, 'Conta criada com sucesso!')

            return redirect('two_factor:login')  

            # Cria a conta associada ao cliente
        
        else:
            print('Formulário inválido:', form.errors)  # Exibe erros para debug

    else:
        form = ClienteForm()  # Cria um formulário vazio para GET
    
    return render(request, 'clientes/cadastro.html', {'form': form})

from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import ContaForm

@login_required
def cadastrar_conta(request):
    if request.method == 'POST':
        form = ContaForm(request.POST)
        if form.is_valid():
            tipo_conta = form.cleaned_data['tipo_conta']
            numero_conta = gerar_numero_conta()  # Gera um número único de conta

            try:
                # Tenta salvar a conta
                conta = Conta.objects.create(
                    id_cliente=request.user,
                    nr_conta=numero_conta,
                    nr_agencia="001",  # Defina um valor padrão ou gere dinamicamente
                    tipo_conta=tipo_conta
                )
                messages.success(request, f"Conta {tipo_conta} criada com sucesso!")
                return redirect('listar_clientes_contas')  # Redireciona para a página de listagem das contas
            except ValueError as e:
                # Se houver um ValueError (ex: contas conflitantes), mostra uma mensagem de erro
                messages.error(request, str(e))
        else:
            messages.error(request, "O formulário contém erros.")
    else:
        form = ContaForm()

    return render(request, 'clientes/cadastrar_conta.html', {'form': form})

#@login_required
def atualizar_cadastro(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    if request.method == 'POST':
        form = ClienteAlterarForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            return redirect('menu')
    else:
        form = ClienteAlterarForm(instance=cliente)
    return render(request, 'clientes/atualizar_cadastro.html', {'form': form})

#@login_required
def listar_clientes_contas(request):
    # Filtra as contas com base no cliente autenticado
    contas = Conta.objects.filter(id_cliente=request.user)  # 'request.user' é o cliente autenticado
    return render(request, 'clientes/listar_clientes_contas.html', {'contas': contas})



#@login_required
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
#@login_required
def menu(request):

    cliente = Cliente.objects.filter(id=request.user.id)
    selected_conta_id = request.GET.get('conta_id')
    if request.method == 'POST':
        conta_id = request.POST.get('conta_id')
        if conta_id:
            request.session['selected_conta_id'] = conta_id  # Salva a conta selecionada na sessão

    if not request.user.is_authenticated:
        return redirect('two_factor:login')  # Redireciona para a página de login se necessário


    # Verifica se há uma conta selecionada na sessão
    conta_selecionada = None
    if 'selected_conta_id' in request.session:
        selected_conta_id = Conta.objects.get(id=request.session['selected_conta_id'])

    # Pega todas as contas do cliente
    contas = Conta.objects.filter(id_cliente=request.user)
    
    # Pega o saldo da conta selecionada
    saldo = selected_conta_id.saldo if selected_conta_id else 0.00

    context = {
        'cliente': cliente,
        'contas': contas,
        'selected_conta_id': selected_conta_id,
        'saldo': saldo
    
    }
    return render(request, 'clientes/menu.html',context)

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
            return response(serializer.data, status=status.HTTP_201_CREATED)
        return response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    




def transacao_poupanca(request):
    conta = Conta.objects.filter(tipo_conta='Poupanca').first() 
    print(conta)
    if conta is None:
        messages.error(request, "Nenhuma conta poupança encontrada. Por favor, crie uma antes de realizar transações.")
        return redirect('transacao_poupanca')  

    
    if request.method == "POST":
        form = TransacaoForm(request.POST)
        if form.is_valid():
            
            valor = Decimal(str(form.cleaned_data['valor']))
            
            if 'depositar' in request.POST:
                conta.saldo += valor 
                messages.success(request, f"Depósito de R$ {valor:.2f} realizado com sucesso!")
            elif 'sacar' in request.POST:
                if conta.saldo >= valor:
                    conta.saldo -= valor  
                    messages.success(request, f"Saque de R$ {valor:.2f} realizado com sucesso!")
                else:
                    messages.error(request, "Saldo insuficiente para realizar o saque.")
            
           
            conta.save()
            return redirect('menu')
    else:
        form = TransacaoForm()

    return render(request, 'clientes/poupanca.html', {'conta': conta, 'form': form})




def transacao_corrente(request):
    conta = Conta.objects.filter(tipo_conta='Corrente').first() 
    print(conta)
    if conta is None:
        messages.error(request, "Nenhuma conta poupança encontrada. Por favor, crie uma antes de realizar transações.")
        return redirect('transacao_corrente')
    
    if request.method == "POST":
        form = TransacaoForm(request.POST)
        if form.is_valid():
            # Converter valor para Decimal
            valor = Decimal(str(form.cleaned_data['valor']))
            if 'depositar' in request.POST:
                conta.saldo += valor
                messages.success(request, f"Depósito de R$ {valor:.2f} realizado com sucesso!")
            elif 'sacar' in request.POST:
                if conta.saldo >= valor:
                    conta.saldo -= valor
                    messages.success(request, f"Saque de R$ {valor:.2f} realizado com sucesso!")
                else:
                    messages.error(request, "Saldo insuficiente para realizar o saque.")
            conta.save()
            return redirect('menu')
    else:
        form = TransacaoForm()

    return render(request, 'clientes/corrente.html', {'conta': conta, 'form': form})



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
    response = request.get(url)
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

    return response(serializer.data, status=status.HTTP_201_CREATED)
    return response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

#==================================================================#
#@login_required
def realizar_transferencia(request):
    if request.method == 'POST':
        conta_origem_id = request.POST.get('conta_origem')
        conta_destino_id = request.POST.get('conta_destino')
        valor = float(request.POST.get('valor'))

        #Caso de erro
        conta_origem = get_object_or_404(Conta, id_conta = conta_origem_id, id_cliente=request.user)
        conta_destino = get_object_or_404(Conta, id_conta=conta_destino_id)

        #Verificando se a conta de origem ossui o saldo para realizar a transferência
        if not conta_origem.verificar_saldo(valor):
                messages.error(request, "Saldo insuficiente para a transferência.")
                return redirect('menu')

        #Realizando a transferência usando o metodo no models
        try:
            conta_origem.atualizar_saldo(valor, is_credito=False)
            conta_destino.atualizar_saldo(valor, is_credito=True)

            #Chamando o models
            movimento = Movimento(id_conta=conta_origem)
            movimento.transferencia(conta_destinatario=conta_destino_id)
            
            messages.success(request, "Transferência realizada com sucesso.")
            return redirect('menu')

        except ValueError as e:
            messages.error(request, f"Erro: {e}")
        except Exception as e:
            messages.error(request, f"Erro inesperado: {e}")
    
    contas = Conta.objects.filter(id_cliente=request.user)
    return render(request, 'clientes/transferencia.html', {'contas': contas})
#==================================================================#
def registro_transferencia(valor):
    hora_atual = time().now().time()
    hora_restrita = time(22,0) <+ hora_atual or hora_atual <=time(6,0)
    return not (hora_restrita and valor > 1000)
        
def historico_transacoes(request, id_conta):
    conta = Conta.objects.get(id=id_conta)
    movimentos = conta.movimentos.all().order_by('-data')
    return render(request, 'historico.html', {'movimentos':movimentos})

