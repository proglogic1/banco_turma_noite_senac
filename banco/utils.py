from .models import Conta, Cliente
import random
from django.contrib import messages

def gerar_numero_conta():
        while True:
            numero_conta = str(random.randint(10000, 99999))
            if not Conta.objects.filter(nr_conta=numero_conta).exists():
                return numero_conta

def calcular_saldo_total(cliente):
    
    contas = Conta.objects.filter(id_cliente=cliente)
    return sum(conta.saldo for conta in contas)

def verificar_tipo_conta_existe(cliente, tipo_conta):
 
    return Conta.objects.filter(id_cliente=cliente, tipo_conta=tipo_conta).exists()

def verificar_conta_existe(nr_conta):
 
    return Conta.objects.filter( nr_conta=nr_conta).exists()


def verificar_cpf_existente(request,cpf):
    if Cliente.objects.filter(cpf=cpf) .exists():
        messages.error(request, 'já existe uma conta com esse CPF.')
        return True # já existe uma conta com esse CPF
    return False # não existe nenhuma conta com esse CPF

def verificar_email(request,email):
    if Cliente.objects.filter(email=email) .exists():
        messages.error(request,'Já existe uma conta com esse E-mail')
        return True #existe outra conta com esse e-mail
    return False #não existe nenhuma conta com esse e-mail
        
