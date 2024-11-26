from django import forms
from .models import Cliente, Conta


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

class ContaForm(forms.ModelForm):
    #tipo_conta = forms.ChoiceField(choices=[('Corrente', 'Corrente'), ('Poupanca', 'Poupança')])
    class Meta:
        model = Conta
        fields = ['tipo_conta']  # Apenas o tipo de conta será selecionado pelo cliente
        widgets = {
            'tipo_conta': forms.Select(attrs={'class': 'form-control'}),
        }

class SaldoForm(forms.Form):
    saldo = forms.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        label="Novo Saldo", 
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

class ClienteAlterarForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [ 'telefone', 'email']
        
class TransferenciaForm(forms.Form):
    conta_origem = forms.ModelChoiceField(queryset=Conta.objects.all(), label="Conta de Origem", widget=forms.Select(attrs={'class': 'form-control'}))
    conta_destino = forms.ModelChoiceField(queryset=Conta.objects.all(), label="Conta de Destino", widget=forms.Select(attrs={'class': 'form-control'}))
    valor = forms.DecimalField(max_digits=10, decimal_places=2, label="Valor a Transferir", widget=forms.NumberInput(attrs={'class': 'form-control'}))

    # Validação de valor positivo
    def clean_valor(self):
        valor = self.cleaned_data.get('valor')
        if valor <= 0:
            raise forms.ValidationError("O valor da transferência deve ser positivo.")
        return valor