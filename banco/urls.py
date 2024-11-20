from django.urls import path,include
from .views import * 

urlpatterns = [
    path('',listar_clientes_contas,name='listar_clientes_contas'),
    path('cadastro/', cadastrar_cliente , name ='cadastro' ),
    path('menu/', menu, name='menu'),
    path('cadastrar_conta/', cadastrar_conta , name ='cadastrar_conta' ),
    path('editar_saldo/', editar_saldo, name='editar_saldo'),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),

    path('api/clientes/', ClienteListCreateView.as_view(), name='api-clientes'),
    path('api/contas/', ContaListCreateView.as_view(), name='api-contas'),
]
