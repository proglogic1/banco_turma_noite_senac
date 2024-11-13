from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .forms import EmailChangeForm
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator

@login_required
def change_email(request):
    if request.method == 'POST':
        form = EmailChangeForm(request.POST)
        if form.is_valid():
            new_email = form.cleaned_data['new_email']
        uid = str(request.user.pk) #ID do usuário convertido em string.
        uidb64 = urlsafe_base64_encode(uid.encode()).decode() #O uid será codificado para evitar problemas de segurança.
        token = default_token_generator.make_token(request.user) #Gera um código único e temporário para garantir que a pessoa clicou no link
        

        
        send_mail(
            'Verifique seu Novo E-mail',
            f'Por favor, clique no link para verificar seu novo e-mail: {email_verification_url}',
            settings.DEFAULT_FROM_EMAIL,
            [new_email],
            fail_silently=False,
)
        messages.success(request, "Enviamos um link de verificação para seu novo e-mail.")

    else:
        form = EmailChangeForm()

    return render(request, 'change_email.html', {'form': form})

