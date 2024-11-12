from django.db import models

class client(models.Model):
    Nome = models.CharField(max_length=100)
    Data_Nascimento = models.DateField()
    Telefone = models.IntegerField()
    CPF = models.IntegerField(max_length=11)
    email = models.EmailField()
    CEP = models.IntegerField()
    Genero = models.CharField()
    senha_1 = models.CharField()
    senha_2 = models.CharField()

    def __str__(self):
        return self.Nome
