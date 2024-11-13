from django.db import models
from client.models import client

class Conta_bancaria(models.Model):
    numero_conta = models.CharField(max_length=6)
    titular = models.ForeignKey(client, on_delete=models.CASCADE)
    saldo = models.DecimalField(max_digits=10, decimal_places=2)
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return  f"Conta {self.numero_conta} - Titular: {self.titular}"
    
    

class Conta_Corrente(Conta_bancaria):
    limite_credito = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    
    def __str__(self):
        return f"Conta corrente {self.numero_conta} - Titular: {self.titular}"
    
    
class Conta_Poupanca(Conta_bancaria):
    taxa_juros = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    
    def __str__(self):
        return f"Conta poupança: {self.numero_conta} - Titular: {self.titular}"