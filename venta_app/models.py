# models.py

from django.db import models

class Venta(models.Model):
    tipo_venta = models.CharField(max_length=50)
    tipo_transaccion = models.CharField(max_length=255)
    fecha = models.DateTimeField()
    a_plazos = models.SmallIntegerField(default=0)
    subtotal = models.DecimalField(max_digits=20, decimal_places=2)
    descuento = models.DecimalField(max_digits=20, decimal_places=2)
    total = models.DecimalField(max_digits=20, decimal_places=2)
    observacion_proforma = models.TextField(null=True, blank=True)
    estado = models.SmallIntegerField(default=1)
    reingreso = models.SmallIntegerField(default=0)
    cliente = models.CharField(max_length=255)
    usuario = models.CharField(max_length=255)


    def __str__(self):
        return f'Venta - {self.pk}- {self.tipo_venta} - {self.fecha}'

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalle')
    espesor = models.FloatField(null=True, blank=True)
    ancho = models.FloatField(null=True, blank=True)
    largo = models.FloatField(null=True, blank=True)
    largo_mt = models.FloatField(null=True, blank=True)
    detalle = models.TextField(null=True, blank=True)
    estado_inventario = models.TextField(null=True, blank=True)
    cantidad = models.IntegerField()
    precio_venta = models.FloatField()
    subtotal = models.FloatField(null=True, blank=True)
    total_pie = models.FloatField(null=True, blank=True)
    reingreso = models.SmallIntegerField(default=0)
    especie =models.CharField(max_length=50)
    

    def __str__(self):
        return f'Detalle de Venta {self.venta} - {self.detalle} - {self.cantidad}'
    
class OrdenDespacho(models.Model):
    nro_despacho = models.IntegerField()
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)

    def __str__(self):
        return f'OrdenDespacho {self.nro_despacho}'


class Pago(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='pago')
    nro_recibo = models.IntegerField()
    fecha_pago = models.DateTimeField()
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2)
    monto_saldo = models.DecimalField(max_digits=10, decimal_places=2)
    observacion = models.TextField(blank=True, null=True)
    tipo_pago = models.IntegerField(choices=[(1, 'Efectivo'), (2, 'Gift Card'), (3, 'Tarjeta'), (4, 'Otros')])
    monto_gift_card = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    numero_tarjeta = models.CharField(max_length=19, blank=True, null=True)

    def __str__(self):
        return f"Pago -{self.venta}-{self.nro_recibo}"

class TipoIngresoEgreso(models.Model):
    descripcion = models.TextField()
    tipo = models.CharField(max_length=10)
    estado = models.SmallIntegerField(default=1)

    def __str__(self):
        return self.descripcion
     
class Ingreso(models.Model):
    fecha = models.DateField()
    fecha_registro = models.DateField()
    concepto = models.CharField(max_length=255)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
    tipo_registro = models.CharField(max_length=255)
    estado = models.BooleanField(default=True)
    usuario = models.CharField(max_length=50)
   
    tipo_ingreso = models.ForeignKey(TipoIngresoEgreso, on_delete=models.CASCADE)

    def __str__(self):
        return f"Ingreso - {self.concepto}"

class IngresoVenta(models.Model):
    ingreso = models.ForeignKey(Ingreso, on_delete=models.CASCADE)
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)

    def __str__(self):
        return f"TipoIngreso  - Ingreso {self.ingreso} - Venta {self.venta}"


class NotaVenta(models.Model):
    nro_nota = models.IntegerField()
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
   

    def __str__(self):
        return f'Nota {self.nro_nota} - Venta {self.venta}'
    

class Proforma(models.Model):
    nro_proforma = models.IntegerField()
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    puesto_obra = models.CharField(max_length=50)
    tipo_cambio = models.CharField(max_length=50)
    condiciones_entrega = models.CharField(max_length=50)
    tiempo_entrega = models.CharField(max_length=50)
    forma_entrega = models.CharField(max_length=50)
    forma_pago = models.CharField(max_length=50)
    nombre_dirigido = models.CharField(max_length=50)

    def __str__(self):
        return f'Proforma {self.nro_proforma} - Venta {self.venta} '