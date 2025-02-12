# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)
    name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()
    first_name = models.CharField(max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    action_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class VentaAppDetalleventa(models.Model):
    espesor = models.FloatField(blank=True, null=True)
    ancho = models.FloatField(blank=True, null=True)
    largo = models.FloatField(blank=True, null=True)
    largo_mt = models.FloatField(blank=True, null=True)
    detalle = models.TextField(blank=True, null=True)
    estado_inventario = models.TextField(blank=True, null=True)
    cantidad = models.IntegerField()
    precio_venta = models.FloatField()
    subtotal = models.FloatField(blank=True, null=True)
    total_pie = models.FloatField(blank=True, null=True)
    reingreso = models.SmallIntegerField()
    especie = models.CharField(max_length=50)
    venta = models.ForeignKey('VentaAppVenta', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'venta_app_detalleventa'


class VentaAppIngreso(models.Model):
    fecha = models.DateField()
    fecha_registro = models.DateField()
    concepto = models.CharField(max_length=255)
    monto_total = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    tipo_registro = models.CharField(max_length=255)
    estado = models.BooleanField()
    usuario = models.CharField(max_length=50)
    tipo_ingreso = models.ForeignKey('VentaAppTipoingresoegreso', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'venta_app_ingreso'


class VentaAppIngresoventa(models.Model):
    ingreso = models.ForeignKey(VentaAppIngreso, models.DO_NOTHING)
    venta = models.ForeignKey('VentaAppVenta', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'venta_app_ingresoventa'


class VentaAppNotaventa(models.Model):
    nro_nota = models.IntegerField()
    venta = models.ForeignKey('VentaAppVenta', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'venta_app_notaventa'


class VentaAppOrdendespacho(models.Model):
    nro_despacho = models.IntegerField()
    venta = models.ForeignKey('VentaAppVenta', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'venta_app_ordendespacho'


class VentaAppPago(models.Model):
    nro_recibo = models.IntegerField()
    fecha_pago = models.DateTimeField()
    monto_total = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    monto_saldo = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    observacion = models.TextField(blank=True, null=True)
    venta = models.ForeignKey('VentaAppVenta', models.DO_NOTHING)
    monto_gift_card = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    numero_tarjeta = models.CharField(max_length=19, blank=True, null=True)
    tipo_pago = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'venta_app_pago'


class VentaAppProforma(models.Model):
    nro_proforma = models.IntegerField()
    puesto_obra = models.CharField(max_length=50)
    condiciones_entrega = models.CharField(max_length=50)
    tiempo_entrega = models.CharField(max_length=50)
    forma_entrega = models.CharField(max_length=50)
    forma_pago = models.CharField(max_length=50)
    nombre_dirigido = models.CharField(max_length=50)
    venta = models.ForeignKey('VentaAppVenta', models.DO_NOTHING)
    tipo_cambio = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'venta_app_proforma'


class VentaAppTipoingresoegreso(models.Model):
    descripcion = models.TextField()
    tipo = models.CharField(max_length=10)
    estado = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'venta_app_tipoingresoegreso'


class VentaAppVenta(models.Model):
    tipo_venta = models.CharField(max_length=50)
    tipo_transaccion = models.CharField(max_length=255)
    a_plazos = models.SmallIntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    descuento = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    total = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    observacion_proforma = models.TextField(blank=True, null=True)
    estado = models.SmallIntegerField()
    reingreso = models.SmallIntegerField()
    cliente = models.CharField(max_length=255)
    usuario = models.CharField(max_length=255)
    fecha = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'venta_app_venta'
