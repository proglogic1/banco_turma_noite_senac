from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cliente, Conta, Movimento
from .forms import ClienteForm, ContaForm,ClienteAlterarForm,TransferenciaForm
from .utils import gerar_numero_conta, calcular_saldo_total, verificar_tipo_conta_existe, verificar_conta_existe
from .serializers import ClienteSerializer, ContaSerializer
from rest_framework import generics,response,status
from rest_framework.views import APIView

#@login_required
from django.http import JsonResponse
from .models import Cliente, Conta

@login_required
def consulta_cliente_view(request):
    cpf_destino = request.GET.get('cpf_destino', '').strip()
    if cpf_destino:
        try:
            cliente_destino = Cliente.objects.get(cpf=cpf_destino)
            contas = Conta.objects.filter(id_cliente=cliente_destino)
            contas_list = [{'id_conta': conta.id_conta, 'nr_conta': conta.nr_conta, 'nr_agencia': conta.nr_agencia} for conta in contas]

            return JsonResponse({
                'success': True,
                'cliente_nome': cliente_destino.nome,
                'contas': contas_list
            })
        except Cliente.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Cliente não encontrado.'})
    return JsonResponse({'success': False, 'error': 'CPF inválido.'})

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
                tipo_conta=form.cleaned_data['tipo_conta']  # Você pode ajustar para um valor padrão ou capturar do formulário
            )
            
            return redirect('menu')  # Redireciona após o cadastro
        
        else:
            print('Formulário inválido:', form.errors)  # Exibe erros para debug

    else:
        form = ClienteForm()  # Cria um formulário vazio para GET
    
    return render(request, 'clientes/cadastro.html', {'form': form})

@login_required
def cadastrar_conta(request):
    cliente = Cliente.objects.get(id=request.user.id)
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
    saldo_total = calcular_saldo_total(cliente) if cliente else 0.0   
    context = {
        'form': form,
        'saldo': saldo_total
    }
    

    return render(request, 'clientes/cadastrar_conta.html', context)

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
        
    saldo_total = calcular_saldo_total(cliente) if cliente else 0.0
    context = {
        'form': form,
        'saldo': saldo_total
    }
    return render(request, 'clientes/atualizar_cadastro.html',context)

@login_required
def listar_clientes_contas(request):
    # Filtra as contas com base no cliente autenticado
    cliente = Cliente.objects.get(id=request.user.id)
    contas = Conta.objects.filter(id_cliente=request.user) 
    saldo_total = calcular_saldo_total(cliente) if cliente else 0.0

    #contas = Conta.objects.filter(id_cliente=cliente) if cliente else []

    context = {
        'contas': contas,
        'saldo': saldo_total
    }
    return render(request, 'clientes/listar_clientes_contas.html', context)
    #return render(request, 'clientes/listar_clientes_contas.html', {'contas': contas})



@login_required
def atualizar_saldo(request):
    cliente = Cliente.objects.get(id=request.user.id)
    if request.method == 'POST':
        conta_id = request.POST.get('conta')  # ID da conta selecionada
        valor = float(request.POST.get('valor'))  # Valor inserido
        tipo = request.POST.get('tipo')  # Tipo de movimento: Crédito ou Débito

        # Validação básica
        conta = get_object_or_404(Conta, id_conta=conta_id)
        #conta = Conta.objects.filter(id_cliente=request.user)
        if tipo == 'Debito' and valor > conta.saldo:
            messages.error(request, 'Saldo insuficiente para débito.')
            return redirect('atualizar_saldo')
        
        # Atualização do saldo
        if tipo == 'Credito':
            conta.saldo += valor
        elif tipo == 'Debito':
            conta.saldo -= valor

        conta.save()

        # Registrar a movimentação
        Movimento.objects.create(
            id_conta=conta,
            tipo_movimento=tipo,
            valor=valor
        )

        messages.success(request, 'Saldo atualizado com sucesso.')
        return redirect('menu')
    saldo_total = calcular_saldo_total(cliente) if cliente else 0.0
    contas = Conta.objects.filter(id_cliente=request.user)
    context = {
               'contas': contas,
               'saldo':saldo_total
              }
    return render(request, 'clientes/atualizar_saldo.html', context)

@login_required
def transferencia(request):
    usuario = request.user
    contas_usuario = Conta.objects.filter(id_cliente=usuario)
    saldo_total = calcular_saldo_total(usuario) if usuario else 0.0
    contas_destino = []
    cliente_destino = ""
    cpf_destino = ""

    if request.method == 'POST':
        cpf_destino = request.POST.get('cpf_destino', '').strip()
        if cpf_destino:
            try:
                cliente_destino = Cliente.objects.get(cpf=cpf_destino)
                contas_destino = Conta.objects.filter(id_cliente=cliente_destino)
            except Cliente.DoesNotExist:
                cliente_destino = None
                contas_destino = []

        conta_origem_id = request.POST.get('conta_origem')
        conta_destino_id = request.POST.get('conta_destino')
        valor_transferencia = float(request.POST.get('valor', 0))

        if conta_origem_id and conta_destino_id and valor_transferencia > 0:
            conta_origem = get_object_or_404(Conta, id_conta=conta_origem_id)
            conta_destino = get_object_or_404(Conta, id_conta=conta_destino_id)

            # Verifica se a conta de origem pertence ao usuário logado
            if conta_origem.id_cliente != usuario:
                return render(request, 'clientes/transferencia.html', {
                    'error': 'Conta de origem inválida.',
                    'contas_usuario': contas_usuario,
                    'contas_destino': contas_destino,
                })

            # Verifica se há saldo suficiente
            if conta_origem.saldo < valor_transferencia:
                return render(request, 'transferencia.html', {
                    'error': 'Saldo insuficiente.',
                    'contas_usuario': contas_usuario,
                    'contas_destino': contas_destino,
                })

            # Realiza a transferência
            conta_origem.saldo -= valor_transferencia
            conta_destino.saldo += valor_transferencia
            conta_origem.save()
            conta_destino.save()

            # Registra os movimentos
            Movimento.objects.create(id_conta=conta_origem, tipo_movimento='Debito', valor=valor_transferencia)
            Movimento.objects.create(id_conta=conta_destino, tipo_movimento='Credito', valor=valor_transferencia)

            return render(request, 'clientes/transferencia.html', {
                'success': 'Transferência realizada com sucesso.',
                'contas_usuario': contas_usuario,
                'contas_destino': [],
            })
    context ={
        'contas_usuario': contas_usuario,
        'contas_destino': contas_destino,
        'cliente_destino': cliente_destino,
        'cpf_destino': cpf_destino,
        'saldo': saldo_total
    }

    return render(request, 'clientes/transferencia.html', context)
@login_required
def menu(request):
    if not request.user.is_authenticated:
        return redirect('login')  # Redireciona para a página de login se necessário

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

def extrato_conta(request):
    cliente = request.user  # Cliente logado
    contas = Conta.objects.filter(id_cliente=cliente)  # Contas do cliente
    
    if not contas.exists():
        return render(request, 'clientes/movimentacoes.html', {'error': 'Você não possui contas cadastradas.'})

    # Conta padrão (primeira conta do cliente)
    conta_id = request.GET.get('conta')  # ID da conta selecionada via combo box
    if conta_id:
        conta = get_object_or_404(Conta, id_conta=conta_id, id_cliente=cliente)
    else:
        conta = contas.first()  # Conta padrão

    # Movimentações da conta selecionada
    movimentacoes = Movimento.objects.filter(id_conta=conta).order_by('-data')
    saldo_total = calcular_saldo_total(cliente) if cliente else 0.0
    context = {
        'contas': contas,
        'conta_selecionada': conta,
        'movimentacoes': movimentacoes,
        'saldo': saldo_total
    }
    
    return render(request, 'clientes/extrato.html',context )
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