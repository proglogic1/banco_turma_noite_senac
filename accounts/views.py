from django.shortcuts import render, redirect
from django.contrib.auth import logout, authenticate, login as auth_login
from django.contrib import messages
from django.core.cache import cache
from rest_framework_simplejwt.tokens import RefreshToken


# Configurações de limite
MAX_ATTEMPTS = 5  # Número máximo de tentativas
LOCKOUT_TIME = 60  # Tempo de bloqueio em segundos (1 minuto)


def login_view(request):
    if request.method == 'POST':
        cpf = request.POST['cpf']
        password = request.POST['password']

        if not cpf or not password:
            messages.error(request, "Por favor, preencha o CPF e a senha")
            return render(request, 'accounts/login.html')

        # Definindo as variáveis de tentativas e de bloqueio
        tentativas_senha = f"tentativas_login_{cpf}"
        bloqueio_senha = f'bloqueio_{cpf}'

        # Verifica se o usuário está bloqueado e envia uma mensagem de erro
        if cache.get(bloqueio_senha):
            messages.error(request, 'Muitas tentativas incorretas de login. Você está bloqueado. Tente novamente mais tarde.')
            return render(request, 'accounts/login.html', {'cpf': cpf})

        # Obtendo o número de tentativas de login
        tentativas = cache.get(tentativas_senha, 0)

        # Tenta autenticar o usuário
        user = authenticate(request, cpf=cpf, password=password)
        if user is not None:
            # Login bem-sucedido
            auth_login(request, user)

            # Gerar tokens JWT
            refresh = RefreshToken.for_user(user)  # Gerar o refresh token
            access_token = refresh.access_token  # Gerar o access token
            print(access_token)
            # Limpar as tentativas de login após sucesso
            cache.delete(tentativas_senha)

            return render(request, 'clientes/menu.html', {
                'refresh': str(refresh),
                'access': str(access_token)
            })

        else:
            # Incrementar as tentativas de login
            messages.error(request, 'Usuário ou senha inválidos.')
            tentativas += 1
            cache.set(tentativas_senha, tentativas, timeout=LOCKOUT_TIME)

            # Se o número de tentativas ultrapassar o limite, bloquear o usuário
            if tentativas >= MAX_ATTEMPTS:
                cache.set(bloqueio_senha, True, timeout=LOCKOUT_TIME)
                messages.error(request, f"Muitas tentativas falhas. Você está bloqueado por {LOCKOUT_TIME // 60} minuto(s).")
            else:
                tentativas_restantes = MAX_ATTEMPTS - tentativas
                messages.error(request, f'Você tem {tentativas_restantes} tentativa(s) restantes.')

            return render(request, 'accounts/login.html', {'cpf': cpf})
    else:
        return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')