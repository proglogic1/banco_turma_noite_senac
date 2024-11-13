from django.db import models

class client(models.Model):
    Nome = models.CharField(max_length=100)
    Telefone = models.IntegerField()
    CPF = models.CharField(max_length=11)
    email = models.EmailField()

    def __str__(self):
        return self.Nome

#==============================================#

class Endereco(models.Model):
    CEP = models.CharField(max_length=8)
    logradouro = models.CharField(max_length=150)
    cidade = models.CharField(max_length=50)
    UF = models.CharField(max_length=2)
    Pais =models.CharField(max_length=35)

    def __str__(self):
        return self.CEP

#==============================================#
class Conta_bancaria(models.Model):
    numero_conta = models.CharField(max_length=6)
    titular = models.ForeignKey(client, on_delete=models.CASCADE)
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return  f"Número da conta: {self.numero_conta} - Titular: {self.titular}"
  
  
#==============================================#
class Conta_Corrente(Conta_bancaria):
    limite_credito = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    
    def __str__(self):
        return f"Conta corrente: {self.numero_conta} - Titular: {self.titular}"
    

#==============================================#
class Conta_Poupanca(Conta_bancaria):
    taxa_juros = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    
    def __str__(self):
        return f"Conta poupança: {self.numero_conta} - Titular: {self.titular}"             