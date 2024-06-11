# admin.py

from django.contrib import admin
from .models import Venta, DetalleVenta,OrdenDespacho,Pago,TipoIngresoEgreso,Ingreso,IngresoVenta,NotaVenta,Proforma
@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ['id', 'tipo_venta', 'tipo_transaccion', 'fecha', 'subtotal', 'total', 'cliente']
    search_fields = ['tipo_venta']
    list_filter = ['fecha', 'tipo_venta', 'tipo_transaccion']

@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ['venta', 'cantidad', 'precio_venta', 'subtotal']
    search_fields = ['venta']
    list_filter = ['venta']
    
@admin.register(OrdenDespacho)
class OrdenDespachoAdmin(admin.ModelAdmin):
    list_display = ['nro_despacho','venta']
    search_fields = ['venta']
    list_filter = ['venta']
    
@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ['nro_recibo','fecha_pago','monto_total','monto_pagado','monto_saldo','observacion','venta',]
    search_fields = ['venta']
    list_filter = ['venta']
    
@admin.register(TipoIngresoEgreso)
class TipoIngresoEgresoAdmin(admin.ModelAdmin):
    list_display = ['descripcion','tipo','estado']
    search_fields = ['tipo']
    list_filter = ['tipo']
    
@admin.register(Ingreso)
class IngresoAdmin(admin.ModelAdmin):
    list_display = ['fecha','fecha_registro','concepto','monto_total','tipo_registro','estado','usuario','tipo_ingreso']
    search_fields = ['tipo_registro']
    list_filter = ['tipo_registro']
    
@admin.register(IngresoVenta)
class IngresoVentaAdmin(admin.ModelAdmin):
    list_display = ['ingreso','venta']
    search_fields = ['venta']
    list_filter = ['venta']
    

    
@admin.register(NotaVenta)
class NotaVentaAdmin(admin.ModelAdmin):
    list_display = ['nro_nota','venta']
    search_fields = ['venta']
    list_filter = ['venta']
    
@admin.register(Proforma)
class ProformaAdmin(admin.ModelAdmin):
    list_display = ['nro_proforma','venta','puesto_obra','tipo_cambio','condiciones_entrega','tiempo_entrega','forma_entrega','forma_pago','nombre_dirigido']
    search_fields = ['nro_proforma']
    list_filter = ['nro_proforma']