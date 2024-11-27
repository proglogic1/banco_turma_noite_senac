from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from decimal import Decimal
from django.db import models

from django.utils.timezone import now

# Gerenciador de usuários personalizado
class CustomUserManager(BaseUserManager):
    def create_user(self, cpf, email, nome, telefone, password=None):
        """
        Cria e retorna um usuário com CPF, email e senha.
        """
        if not cpf:
            raise ValueError("O CPF é obrigatório")
        if not email:
            raise ValueError("O email é obrigatório")
        
        # Cria o usuário com o CPF como identificador
        user = self.model(
            cpf=cpf,
            email=self.normalize_email(email),
            nome=nome,
            telefone=telefone,
        )
        
        user.set_password(password)
        user.save(using=self._db)
        return user

class Cliente(AbstractBaseUser):
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=256)
    telefone = models.CharField(max_length=15)
    cpf = models.CharField(max_length=14, unique=True)
    email = models.EmailField(unique=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    
    
 # Campos de autenticação
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Para indicar se o usuário é um administrador
    is_superuser = models.BooleanField(default=False)  # Para indicar se o usuário é superadministrador

    # Campos obrigatórios para autenticação
    USERNAME_FIELD = 'cpf'
    REQUIRED_FIELDS = ['email','telefone']

    objects = CustomUserManager()

    def __str__(self):
        return self.nome

    def has_perm(self, perm, obj=None):
        return self.is_active

    def has_module_perms(self, app_label):
        return self.is_active

#==================================================#

class Conta(models.Model):
    id_conta = models.AutoField(primary_key=True)
    id_cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    nr_conta = models.CharField(max_length=5)
    nr_agencia = models.CharField(max_length=3)
    dt_cadastro = models.DateTimeField(auto_now_add=True)
    tipo_conta = models.CharField(max_length=10, choices=[('Corrente', 'Corrente'), ('Poupanca', 'Poupanca')])
    saldo = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        return self.nr_conta
    
    #Metodo para verificar o saldo
    def verificar_saldo(self, quant):
        return self.saldo >= quant
    
    #Método para atualizar o saldo
    def atualizar_saldo(self, quant, is_credito=True):
        if is_credito:
            self.saldo += quant
        else:
            self.saldo -= quant
        self.save()

# #==================================================#

class Movimento(models.Model):
    id_movimento = models.AutoField(primary_key=True)
    id_conta = models.ForeignKey(Conta, on_delete=models.CASCADE, related_name='movimentos')
    tipo_movimento = models.CharField(max_length=13, choices=[
        ('Credito', 'Credito'),
        ('Debito', 'Debito'),
        ('Transferencia', 'Transferência')
    ])
    valor = models.FloatField()
    saldo_movimento = models.FloatField()  # Saldo atualizado após o movimento
    data = models.DateTimeField(auto_now_add=True)
    conta_destinatario = models.ForeignKey(
        Conta, on_delete=models.SET_NULL, null=True, blank=True, related_name='transferencias_recebidas'
    )

    def __str__(self):
        return f"{self.tipo_movimento} - {self.valor} ({self.data})"
    
    def transferencia(self, conta_destinatario, valor):
        if not self.verificar_saldo(valor):
            raise ValueError("Saldo insuficiente para a transferência.")
    
        #Atualiza saldos
        self.atualizar_saldo(valor, is_credito=False)
        conta_destinatario.atualizar_saldo(valor, is_credito=True)
        
        #Registrar Movimento
        Movimento.objects.create(
            id_conta=self,
            tipo_movimento='Transferencia',
            valor=valor,
            saldo_movimento=self.saldo,
            conta_destinatario=conta_destinatario,
        )
        Movimento.objects.create(
            id_conta=conta_destinatario,
            tipo_movimento= 'Credito',
            valor=valor,
            saldo_movimento=conta_destinatario.saldo,
        )












