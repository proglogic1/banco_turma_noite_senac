from django import forms
from .models import Cliente


class ClienteForm(forms.ModelForm):
    tipo_conta = forms.ChoiceField(choices=[('Corrente', 'Corrente'), ('Poupanca', 'Poupança')])
    senha = forms.CharField(widget=forms.PasswordInput, max_length=128, required=True,label='Senha')
    confirmar_senha = forms.CharField(widget=forms.PasswordInput,max_length=128,required=True,label='Confirmar Senha')
    class Meta:
        model = Cliente
        fields = ['nome', 'cpf', 'telefone', 'email','tipo_conta']
        
    def clean(self):
        cleaned_data = super().clean()
        senha = cleaned_data.get('senha')
        confirmar_senha = cleaned_data.get('confirmar_senha')

        if senha != confirmar_senha:
            raise forms.ValidationError('As senhas não coincidem.')
        
        return cleaned_data