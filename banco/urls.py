from django.urls import path,include
from django.contrib.auth import views as auth_views
from .views import * 


urlpatterns = [
    path('',listar_clientes_contas,name='listar_clientes_contas'),
    path('cadastro/', cadastrar_cliente , name ='cadastro' ),
    path('menu/', menu, name='menu'),
    path('cadastrar_conta/', cadastrar_conta , name ='cadastrar_conta' ),
    path('atualizar_cadastro/<int:id>/', atualizar_cadastro, name='atualizar_cadastro'),
    path('atualizar_saldo/', atualizar_saldo, name='atualizar_saldo'),
    path('extrato/', extrato_conta, name='extrato_conta'),
    path('transferencia/',transferencia,name='transferencia'),
    path('consulta_cliente/', consulta_cliente_view, name='consulta_cliente'),

    path('accounts/', include('accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),

    path('api/clientes/', ClienteListCreateView.as_view(), name='api-clientes'),
    path('api/contas/', ContaListCreateView.as_view(), name='api-contas'),
]
