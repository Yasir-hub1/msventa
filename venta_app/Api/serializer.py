from rest_framework import serializers
from venta_app.models import Venta, DetalleVenta, Pago, TipoIngresoEgreso, Ingreso, IngresoVenta, NotaVenta, Proforma,OrdenDespacho

class DetalleVentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleVenta
        fields = '__all__'

class VentaSerializer(serializers.ModelSerializer):
    # detalle_productos = DetalleVentaSerializer(many=True)
    
    class Meta:
        model = Venta
        fields = '__all__'

class PagoSerializer(serializers.ModelSerializer):
    # venta = serializers.IntegerField()
    class Meta:
        model = Pago
        fields = '__all__'

class TipoIngresoEgresoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoIngresoEgreso
        fields = '__all__'

class IngresoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingreso
        fields = '__all__'

class IngresoVentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngresoVenta
        fields = '__all__'

class NotaVentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotaVenta
        fields = '__all__'

class ProformaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proforma
        fields = '__all__'


class OrdenDespachoSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrdenDespacho
        fields = '__all__'
