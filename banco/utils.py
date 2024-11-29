from .models import Conta, Cliente
import random

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