from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth import logout, authenticate, login as auth_login
from django.contrib import messages
from django.core.cache import cache
from django.http import HttpResponse


# Configurações de limite
MAX_ATTEMPTS = 5  # Número máximo de tentativas
LOCKOUT_TIME = 60  # Tempo de bloqueio em segundos (1 minuto)



def login_view(request):
    if request.method == 'POST':
        cpf = request.POST['cpf']
        password = request.POST['password']

        #verificar se o cpf ou senha foram preenchidos
        if not cpf or not password:
            messages.error(request, "Por favor, preencha o CPF e a senha")
        

        #verificar tentativas erradas de inserir a senha no cache
        tentativas_senha = f"tentativas_login_{cpf}"
        bloqueio_senha = f'bloqueio_{cpf}'

        #verifica se o usuario esta bloqueado e envia uma mensagem de erro
        if cache.get(bloqueio_senha):
            messages.error(request, 'muitas tentativas incorretas de login. você está bloqueado tente novamente mais tarde ')
            return render(request, 'accounts/login.html', {'cpf':cpf})

        #obtendo o numero de tentativas de login
        tentativas = cache.get(tentativas_senha, 0)


        user = authenticate(request, cpf=cpf, password=password)
        if user is not None:
            auth_login(request, user)
            cache.delete(tentativas_senha)  # Resetar tentativas
            messages.success(request, "Login realizado com sucesso!")
            return redirect('menu')
        
        else:
            #incrementar tentativas
            tentativas += 1
            cache.set(tentativas_senha, tentativas, timeout=LOCKOUT_TIME)
            
            if tentativas >= MAX_ATTEMPTS:
                #bloquear usuario
                cache.set(bloqueio_senha, True, timeout=LOCKOUT_TIME)
                messages.error(request, f"Muitas tentativas falhas. Você está bloqueado por {LOCKOUT_TIME // 60} minuto(s).")

            else:
                tentativas_restantes = MAX_ATTEMPTS - tentativas
                messages.error(request, f'Usuário ou senha inválidos. Você tem {tentativas_restantes} tentativa(s) restantes')

            return render(request, 'accounts/login.html', {'cpf': cpf})
    else:
        return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')