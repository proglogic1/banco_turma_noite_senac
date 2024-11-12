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
