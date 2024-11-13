from django.contrib import admin
from .models import Conta_bancaria, Conta_Corrente, Conta_Poupanca

admin.site.register(Conta_bancaria)
admin.site.register(Conta_Corrente)
admin.site.register(Conta_Poupanca)