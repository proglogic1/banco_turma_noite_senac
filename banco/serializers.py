from rest_framework import serializers
from .models import Cliente, Conta
from django.core.exceptions import ValidationError
import random

def gerar_numero_conta():
        while True:
            numero_conta = str(random.randint(10000, 99999))
            if not Conta.objects.filter(nr_conta=numero_conta).exists():
                return numero_conta
            
class ClienteSerializer(serializers.ModelSerializer):
    senha = serializers.CharField(write_only=True, style={'input_type': 'password'}, label='Senha')
    confirmar_senha = serializers.CharField(write_only=True, style={'input_type': 'password'}, label='Confirmar Senha')
    tipo_conta = serializers.ChoiceField(choices=[('Corrente', 'Corrente'), ('Poupanca', 'Poupança')], write_only=True)

    class Meta:
        model = Cliente
        fields = ['nome', 'cpf', 'telefone', 'email', 'senha', 'confirmar_senha', 'tipo_conta']

    def validate(self, data):
        senha = data.get('senha')
        confirmar_senha = data.get('confirmar_senha')

        if senha != confirmar_senha:
            raise serializers.ValidationError({'confirmar_senha': 'As senhas não coincidem.'})

        return data


    def create(self, validated_data):
        # Remove os campos de senha antes de criar o cliente
        senha = validated_data.pop('senha')
        validated_data.pop('confirmar_senha')
        tipo_conta = validated_data.pop('tipo_conta')

        cliente = Cliente(**validated_data)
        cliente.set_password(senha)  # Define a senha criptografada
        cliente.save()

        # Cria a conta associada ao cliente
        Conta.objects.create(
            id_cliente=cliente,
            nr_conta=gerar_numero_conta(),
            nr_agencia="0001",
            tipo_conta=tipo_conta
        )

        return cliente

class ContaSerializer(serializers.ModelSerializer):
    cliente = ClienteSerializer(source='id_cliente', read_only=True)  # Inclui o cliente como um campo aninhado

    class Meta:
        model = Conta
        fields = ['id_conta', 'cliente', 'nr_conta', 'nr_agencia', 'tipo_conta']