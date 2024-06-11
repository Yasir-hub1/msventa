# Generated by Django 5.0.6 on 2024-05-25 04:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('venta_app', '0002_ordendespacho'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ingreso',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField()),
                ('fecha_registro', models.DateField()),
                ('concepto', models.CharField(max_length=255)),
                ('monto_total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('tipo_registro', models.CharField(max_length=255)),
                ('estado', models.BooleanField(default=True)),
                ('usuario', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='TipoIngresoEgreso',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.TextField()),
                ('tipo', models.CharField(max_length=10)),
                ('estado', models.SmallIntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='IngresoVenta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ingreso', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='venta_app.ingreso')),
                ('venta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='venta_app.venta')),
            ],
        ),
        migrations.CreateModel(
            name='Pago',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nro_recibo', models.IntegerField()),
                ('fecha_pago', models.DateField()),
                ('monto_total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('monto_pagado', models.DecimalField(decimal_places=2, max_digits=10)),
                ('monto_saldo', models.DecimalField(decimal_places=2, max_digits=10)),
                ('observacion', models.TextField()),
                ('venta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='venta_app.venta')),
            ],
        ),
        migrations.AddField(
            model_name='ingreso',
            name='tipo_ingreso',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='venta_app.tipoingresoegreso'),
        ),
    ]