from django.db import models
from client.models import client
class Conta_bancaria(models.Model):
    Número_conta = models.CharField(max_length=6)
    Titular = models.ForeignKey(client, on_delete=models.CASCADE)
    Saldo = models.DecimalField(max_digits=10, decimal_places=2)
    Data_criaçao = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.Número_conta