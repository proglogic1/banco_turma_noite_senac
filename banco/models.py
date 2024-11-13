from django.db import models

class Cliente(models.Model):
    id = models.AutoField(primary_key=True)
    Nome = models.CharField(max_length=256)
    Telefone = models.CharField(max_length=11)
    CPF = models.CharField(max_length=11)
    Email = models.EmailField()
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.Nome

#==================================================#

class Conta(models.Model):
    id_conta = models.AutoField(primary_key=True)
    id_cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    NR_conta = models.CharField(max_length=5)
    NR_agencia = models.CharField(max_length=3)
    DT_cadastro = models.DateTimeField(auto_now_add=True)
    tipo_conta = models.CharField(max_length=10, choices=[('Corrente', 'Corrente'), ('Poupanca', 'Poupanca')])

    def __str__(self):
        return self.NR_conta

# #==================================================#

class Movimento(models.Model):
    id_movimento = models.AutoField(primary_key=True)
    id_conta = models.ForeignKey(Conta, on_delete=models.CASCADE)
    tipo_movimento = models.CharField(max_length=10, choices=[('Credito', 'Credito'), ('Debito', 'Debito')])
    valor = models.FloatField()
    data = models.DateTimeField(auto_now_add=True)