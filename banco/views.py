from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Cliente, Conta
from .forms import ClienteForm, ContaForm,ClienteAlterarForm
from .utils import gerar_numero_conta, calcular_saldo_total, verificar_tipo_conta_existe, verificar_conta_existe, verificar_cpf_existente, verificar_email
from .serializers import ClienteSerializer, ContaSerializer
from rest_framework import generics,response,status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib import messages

 
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
            
            messages.success(request, 'Conta criada com sucesso!')

            return redirect('two_factor:login')  
            # Cria a conta associada ao cliente
        
        else:
            print('Formulário inválido:', form.errors)  # Exibe erros para debug

    else:
        form = ClienteForm()  # Cria um formulário vazio para GET
    
    return render(request, 'clientes/cadastro.html', {'form': form})

def transferir_dinheiro(request):
    if request.method == 'POST':
        conta_origem_id = request.POST.get('conta_origem_id')
        conta_destino_id = request.POST.get('conta_destino_id')
        valor = request.POST.get('valor')

        try:
            conta_origem = Conta.objects.get(id_conta=conta_origem_id)
            conta_destino = Conta.objects.get(id_conta=conta_destino_id
                                              
                        )

            if conta_origem.saldo >= float(valor):
                conta_origem.saldo -= float(valor)
                conta_destino.saldo += float(valor)
                conta_origem.save()
                conta_destino.save()
                messages.success(request, "Transferência realizada com sucesso!")
                return redirect('listar_clientes_contas')  # Redireciona para a listagem de contas
            else:
                messages.error(request, "Saldo insuficiente na conta de origem.")
        except Conta.DoesNotExist:
            messages.error(request, "Conta não encontrada.")

    contas = Conta.objects.filter(id_cliente=request.user)
    return render(request, 'clientes/transferir_dinheiro.html', {'contas': contas})


@login_required
def cadastrar_conta(request):
    if request.method == 'POST':
        form = ContaForm(request.POST)
        if form.is_valid():
            # numero_conta = gerar_numero_conta()  # Gera um número único de conta
            # nova_conta = form.save(commit=False)  # Não salva ainda no banco
            # nova_conta.id_cliente = request.user  # Associa a conta ao cliente autenticado
            # nova_conta.save()  # Salva a nova conta com o número gerado automaticamente
            tipo_conta=form.cleaned_data['tipo_conta']
                      
            numero_conta = gerar_numero_conta()  # Gera um número único de conta
            if verificar_conta_existe(numero_conta):
                 form.add_error('numero_conta', "Essa conta ja existe")
            elif verificar_tipo_conta_existe(request.user,tipo_conta):
                 form.add_error('tipo_conta', 'Você já possui uma conta desse tipo.')
                 #INSERIR POPUP NA TELA INFORMANDO QUE JA EXISTE UMA CONTA DESSE TIPO
                 
            else:      
                conta = Conta.objects.create(
                        id_cliente=request.user,
                        nr_conta=numero_conta,
                        nr_agencia="001",  # Defina um valor padrão ou gere dinamicamente
                        tipo_conta=tipo_conta  # Você pode ajustar para um valor padrão ou capturar do formulário
                    )
            return redirect('listar_clientes_contas')  # Redireciona para a página de listagem das contas
    else:
        form = ContaForm()
      
    return render(request, 'clientes/cadastrar_conta.html', {'form': form})

@login_required
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

@login_required
def listar_clientes_contas(request):
    # Filtra as contas com base no cliente autenticado
    cliente = Cliente.objects.get(id=request.user.id)
    contas = Conta.objects.filter(id_cliente=request.user) 
    saldo_total = calcular_saldo_total(cliente) if cliente else 0.0

    contas = Conta.objects.filter(id_cliente=cliente) if cliente else []

    context = {
        
        'contas': contas,
        'saldo': saldo_total
    }
    return render(request, 'clientes/listar_clientes_contas.html', context)
    #return render(request, 'clientes/listar_clientes_contas.html', {'contas': contas})



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

@login_required
def menu(request):
    if not request.user.is_authenticated:
        return redirect('two_factor:login')  # Redireciona para a página de login se necessário

    try:
        # Ajuste aqui para relacionar Cliente ao User, se necessário
        cliente = Cliente.objects.get(id=request.user.id)
    except Cliente.DoesNotExist:
        cliente = None

    saldo_total = calcular_saldo_total(cliente) if cliente else 0.0
    contas = Conta.objects.filter(id_cliente=cliente) if cliente else []

    # Passa os dados ao template
    context = {
        'cliente': cliente,
        'contas': contas,
        'saldo': saldo_total
    }
    return render(request, 'clientes/menu.html', context)

# def menu(request):
#     cliente = Cliente.objects.filter(id=request.user.id)
#     selected_conta_id = request.GET.get('conta_id')
#     if request.method == 'POST':
#         conta_id = request.POST.get('conta_id')
#         if conta_id:
#             request.session['selected_conta_id'] = conta_id  # Salva a conta selecionada na sessão

#     # Verifica se há uma conta selecionada na sessão
#     conta_selecionada = None
#     if 'selected_conta_id' in request.session:
#         selected_conta_id = Conta.objects.get(id=request.session['selected_conta_id'])

#     # Pega todas as contas do cliente
#     contas = Conta.objects.filter(id_cliente=request.user)
    
#     # Pega o saldo da conta selecionada
#     saldo = selected_conta_id.saldo if selected_conta_id else 0.00

#     context = {
#         'cliente': cliente,
#         'contas': contas,
#         'selected_conta_id': selected_conta_id,
#         'saldo': saldo
    
#     }
#     return render(request, 'clientes/menu.html',context)

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