from django.urls import path,include
from .views import cadastrar_cliente,listar_clientes_contas,ClienteListCreateView, ContaListCreateView
from .views import Buscar_Cep, endereco

urlpatterns = [
    path('',listar_clientes_contas,name='listar_clientes_contas'),
    path('cadastrar/', cadastrar_cliente, name='cadastrar_cliente'),
    path('lista/',listar_clientes_contas,name='listar_clientes_contas'),#
    path('cadastro/', cadastrar_cliente , name ='cadastro' ),
    path('', menu, name='menu'),
    path('cadastrar_conta/', cadastrar_conta , name ='cadastrar_conta' ),
    path('atualizar_cadastro/<int:id>/', atualizar_cadastro, name='atualizar_cadastro'),

    path('accounts/', include('accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('api/clientes/', ClienteListCreateView.as_view(), name='api-clientes'),
    path('api/contas/', ContaListCreateView.as_view(), name='api-contas'),
    path('endereco/', endereco, name='Endereco'), # Renderiza a página inicial com o formulário
    
    
    
    path('CEP/', Buscar_Cep, name='CEP'),# Rota para buscar o CEP
    path('transferencia/', realizar_transferencia, name='realizar_transferencia'),
    path('historico/<int:id_conta>/', historico_transacoes, name='historico_transacoes'),
]

