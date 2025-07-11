# Generated by Django 5.0.6 on 2025-06-19 18:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SportFit_app', '0002_detallepedido'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='detallepedido',
            options={'managed': False},
        ),
        migrations.CreateModel(
            name='ComentarioPlan',
            fields=[
                ('id_comentario', models.AutoField(primary_key=True, serialize=False)),
                ('comentario', models.TextField(max_length=500)),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('plan', models.ForeignKey(db_column='id_plan', on_delete=django.db.models.deletion.CASCADE, to='SportFit_app.planentrenamiento')),
                ('usuario', models.ForeignKey(db_column='id_usuario', on_delete=django.db.models.deletion.CASCADE, to='SportFit_app.usuario')),
            ],
            options={
                'db_table': 'comentario_plan',
                'unique_together': {('usuario', 'plan')},
            },
        ),
    ]
