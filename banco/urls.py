from django.urls import path,include
from django.contrib.auth import views as auth_views
from .views import * 
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import routers

router = routers.DefaultRouter()

router.register(r'cliente', ClienteViewSet) 
router.register(r'conta', ContaViewSet)


urlpatterns = [
    path('lista/',listar_clientes_contas,name='listar_clientes_contas'),
    path('cadastro/', cadastrar_cliente , name ='cadastro' ),
    path('', menu, name='menu'),
    path('cadastrar_conta/', cadastrar_conta , name ='cadastrar_conta' ),
    path('atualizar_cadastro/<int:id>/', atualizar_cadastro, name='atualizar_cadastro'),

    path('accounts/', include('accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Gera token de acesso e refresh
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Atualiza o token de acesso
    path('api/', include(router.urls)),
    
    path('endereco/', endereco, name='Endereco'), # Renderiza a página inicial com o formulário
    path('CEP/', Buscar_Cep, name='CEP'),# Rota para buscar o CEP

    path('poupanca/', transacao_poupanca, name='transacao_poupanca'),
    path('corrente/', transacao_corrente, name='transacao_corrente'),
    
    path('transferencia/', realizar_transferencia, name='realizar_transferencia'),
   
]
