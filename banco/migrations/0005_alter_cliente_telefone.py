# Generated by Django 5.1.3 on 2024-11-19 22:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banco', '0004_alter_cliente_cpf'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cliente',
            name='telefone',
            field=models.CharField(max_length=14),
        ),
    ]
