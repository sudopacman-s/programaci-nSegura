# Generated by Django 5.2 on 2025-05-06 04:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('servidores', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_usuario', models.CharField(max_length=150, unique=True)),
                ('contrasena_sha256', models.CharField(max_length=255)),
            ],
        ),
        migrations.AlterField(
            model_name='servidor',
            name='id',
            field=models.CharField(max_length=255, primary_key=True, serialize=False),
        ),
    ]
