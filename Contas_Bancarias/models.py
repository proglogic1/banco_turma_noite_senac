from django.db import models

class Conta_bancaria(models.Model):
    Número_conta = models.CharField(max_length=6)
    
