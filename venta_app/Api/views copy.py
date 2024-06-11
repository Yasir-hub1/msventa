
from venta_app.models import Venta,DetalleVenta,Pago, OrdenDespacho, NotaVenta, Proforma, Ingreso, IngresoVenta, Venta
from rest_framework.response import Response
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from django.db import transaction,models
from django.utils import timezone
from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view
from venta_app.Api.serializer import VentaSerializer, DetalleVentaSerializer

@api_view(['GET'])
def venta_list(request):
    # Obtener todas las ventas
    ventas = Venta.objects.all()
    serializer = VentaSerializer(ventas, many=True)
    
    # Crear una lista para almacenar la información de las ventas con sus detalles
    ventas_data = []

    for venta in ventas:
        # Filtrar los detalles de la venta actual
        detalles_venta = DetalleVenta.objects.filter(venta=venta)

        # Crear una lista de diccionarios con los detalles de la venta
        detalles_serializer = DetalleVentaSerializer(detalles_venta, many=True)

        # Agregar la información de la venta y sus detalles a la lista de ventas
        ventas_data.append({
            'id': venta.id,
            'tipo_venta': venta.tipo_venta,
            'tipo_transaccion': venta.tipo_transaccion,
            'fecha': venta.fecha,
            'a_plazos': venta.a_plazos,
            'subtotal': venta.subtotal,
            'descuento': venta.descuento,
            'total': venta.total,
            'observacion_proforma': venta.observacion_proforma,
            'estado': venta.estado,
            'reingreso': venta.reingreso,
            'cliente': venta.cliente,
            'usuario': venta.usuario,
            'detalles': detalles_serializer.data
        })

    # Retornar la información como JSON
    return Response(ventas_data)
@api_view()
def verVentaId(request, id_venta):
    # Obtener la venta especificada por id_venta
    venta = get_object_or_404(Venta, pk=id_venta)
    
    # Filtrar todos los detalles de la venta por el id de la venta
    detalles_venta = DetalleVenta.objects.filter(venta=venta)
    
    # Crear una lista de diccionarios con los detalles de la venta
    detalles = []
    for detalle in detalles_venta:
        detalles.append({
            'id': detalle.id,
            'espesor': detalle.espesor,
            'ancho': detalle.ancho,
            'largo': detalle.largo,
            'largo_mt': detalle.largo_mt,
            'detalle': detalle.detalle,
            'estado_inventario': detalle.estado_inventario,
            'cantidad': detalle.cantidad,
            'precio_venta': detalle.precio_venta,
            'subtotal': detalle.subtotal,
            'total_pie': detalle.total_pie,
            'reingreso': detalle.reingreso,
            'especie': detalle.especie  # Assuming you want the ID; adjust as needed
        })
    
    # Crear un diccionario con la información de la venta y sus detalles
    data = {
        'id': venta.id,
        'tipo_venta': venta.tipo_venta,
        'tipo_transaccion': venta.tipo_transaccion,
        'fecha': venta.fecha,
        'a_plazos': venta.a_plazos,
        'subtotal': venta.subtotal,
        'descuento': venta.descuento,
        'total': venta.total,
        'observacion_proforma': venta.observacion_proforma,
        'estado': venta.estado,
        'reingreso': venta.reingreso,
        'cliente': venta.cliente,  # Assuming you want the ID; adjust as needed
     
        'usuario': venta.usuario,  # Assuming you want the ID; adjust as needed
        'detalles': detalles
    }
    
    # Retornar la información como JSON
    return JsonResponse(data)







@api_view()
@transaction.atomic
def registrar_venta(request):
    datos = {}
    try:
        data = {}
        tipo = request.POST.get('tipo')
        venta = {}
        
        if tipo == 'nv':
            venta['tipo_venta'] = 'NOTA'
            venta['estado'] = 1
        elif tipo == 'f':
            venta['tipo_venta'] = 'FACTURA'
            venta['estado'] = 1
        elif tipo == 'pr':
            venta['tipo_venta'] = 'PROFORMA'
            venta['estado'] = 0
            observacion = '<p><b>OBSERVACION</b><br><b>1.- Puesto en obra: </b>\n' + request.POST.get('puesto_obra', '') + '<br>' +\
                          '<b>2.- Tipo de cambio: </b>' + request.POST.get('tipo_cambio', '') + '<br>' +\
                          '<b>3.- Condiciones de entrega: </b>' + request.POST.get('condiciones_entrega', '') + '<br>' +\
                          '<b>4.- Tiempo de entrega: </b>' + request.POST.get('tiempo_entrega', '') + '<br>' +\
                          '<b>5.- Forma de entrega: </b>' + request.POST.get('forma_entrega', '') + '<br>' +\
                          '<b>6.- Forma de pago: </b>' + request.POST.get('forma_pago', '') + '<br>' +\
                          '<h4>' + request.POST.get('nombre_dirigido', '') + '</h4></p>'
            venta['observacion_proforma'] = observacion

            obs = {
                "puesto_obra": request.POST.get('puesto_obra', 'No'),
                "tipo_cambio": request.POST.get('tipo_cambio', 'No'),
                "condiciones_entrega": request.POST.get('condiciones_entrega', 'No'),
                "tiempo_entrega": request.POST.get('tiempo_entrega', 'No'),
                "forma_entrega": request.POST.get('forma_entrega', 'No'),
                "forma_pago": request.POST.get('forma_pago', 'No'),
                "nombre_dirigido": request.POST.get('nombre_dirigido', 'No'),
            }

        cliente_id = request.POST.get('cliente_id')

        transaccion = request.POST.get('trans')
        if transaccion == 'mp':
            venta['tipo_transaccion'] = 'MATERIA'
            obj_venta = {
                'tipo_pago': request.POST.get('tipo_pago'),
                'acuenta': request.POST.get('a_cuenta'),
                'saldo': request.POST.get('saldo')
            }
        elif transaccion == 'ot':
            venta['tipo_transaccion'] = 'OTROS'
            obj_venta = {
                'tipo_pago': False
            }

        venta.update({
            'fecha': timezone.now(),
            'subtotal': request.POST.get('subtotal'),
            'descuento': request.POST.get('descuento'),
            'total': request.POST.get('total'),
            'cliente': cliente_id,
           
            'usuario_id': request.POST.get('user_id'),
            'reingreso': request.POST.get('suggestion'),
        })

        new_venta = Venta.objects.create(**venta)
        datos["venta"] = new_venta

        detalle_productos = request.POST.getlist('detalle_productos')
        for detalle in detalle_productos:
            detalle_venta = {
                'venta_id': new_venta.id,
                'detalle': detalle['detalle'],
                'precio_venta': detalle['precio'],
                'cantidad': detalle['cantidad_derivado'] if transaccion == 'ot' else detalle['cantidad'],
                'subtotal': detalle['subtotal'],
                'total_pie': 0 if transaccion == 'ot' else round((detalle['espesor'] * detalle['ancho'] * detalle['largo'] / 12) * (detalle['cantidad']), 2),
                'largo_mt': 0 if transaccion == 'ot' else detalle['largo_mt'],
            }

            if transaccion != 'ot':
                detalle_venta.update({
                    'reingreso': detalle['suggestion'],
                    'especie_id': detalle['especie_id'],
                    'espesor': detalle['espesor'],
                    'ancho': detalle['ancho'],
                    'largo': detalle['largo'],
                    'detalle': detalle['observacion'],
                })

            detalle_to_array = DetalleVenta.objects.create(**detalle_venta)
            datos.setdefault('detalle_venta', []).append(detalle_to_array)

            

            """ if detalle.get("otro_material") == "":
                producto = get_object_or_404(Producto, id=detalle['id'])
                producto.cantidad -= detalle['cantidad']
                producto.save()
                datos.setdefault('productos', []).append(producto) """

        if venta['tipo_venta'] != 'PROFORMA':
            datos["orden_venta"] = registrar_orden(new_venta.id)

        if venta['tipo_venta'] != 'PROFORMA' and obj_venta.get('tipo_pago'):
            Venta.objects.filter(id=new_venta.id).update(a_plazos=1)
            datos["venta_modificacion"] = get_object_or_404(Venta, id=new_venta.id)

            nro_recibo = Pago.objects.count() + 1
            pagos = {
                'venta_id': new_venta.id,
                'nro_recibo': nro_recibo,
                'fecha_pago': timezone.now(),
                'monto_total': venta['total'],
                'monto_pagado': obj_venta['acuenta'],
                'monto_saldo': obj_venta['saldo'],
                'observacion': 'Se hizo el primer pago del total vendido.',
                'monto_gift_card': request.POST.get('monto_gift_card'),
                'numero_tarjeta': request.POST.get('numero_tarjeta'),
                'tipo_pago': request.POST.get('metodo_pago')
            }
            pago_dato = Pago.objects.create(**pagos)
            datos["pago"] = pago_dato

            
            datos["verrif"] = ingreso_venta(venta, obj_venta, new_venta.id, '1')
        elif venta['tipo_venta'] != 'PROFORMA':
            nro_recibo = Pago.objects.count() + 1
            pagos = {
                'venta_id': new_venta.id,
                'nro_recibo': nro_recibo,
                'fecha_pago': timezone.now(),
                'monto_total': venta['total'],
                'monto_pagado': venta['total'],
                'monto_saldo': 0,
                'observacion': 'Pago por venta al contado.',
                'monto_gift_card': request.POST.get('monto_gift_card'),
                'numero_tarjeta': request.POST.get('numero_tarjeta'),
                'tipo_pago': request.POST.get('metodo_pago')
            }
            Pago.objects.create(**pagos)

        if venta['tipo_venta'] == 'NOTA':
            datos["nota_venta"] = registro_nota_venta(new_venta.id)
        elif venta['tipo_venta'] == 'PROFORMA':
            datos["proforma"] = registro_proforma(new_venta.id, obs)

        return JsonResponse(datos, status=200)
    except Exception as e:
        transaction.set_rollback(True)
        return JsonResponse({'error': str(e)}, status=500)

def registro_nota_venta(venta_id):
    max_nro_nota = NotaVenta.objects.aggregate(max_nro_nota=models.Max('nro_nota'))['max_nro_nota']
    if not max_nro_nota:
        max_nro_nota = 100
    else:
        max_nro_nota += 1

    nota_venta = NotaVenta.objects.create(venta_id=venta_id, sucursal_id=1, nro_nota=max_nro_nota)
    return nota_venta

def registro_proforma(venta_id, obs):
    max_nro_proforma = Proforma.objects.aggregate(max_nro_proforma=models.Max('nro_proforma'))['max_nro_proforma']
    if not max_nro_proforma:
        max_nro_proforma = 100
    else:
        max_nro_proforma += 1

    obs["venta_id"] = venta_id
    obs["nro_proforma"] = max_nro_proforma
    proforma = Proforma.objects.create(**obs)
    return proforma

def registrar_orden(venta_id):
    max_orden_despacho = OrdenDespacho.objects.aggregate(max_orden_despacho=models.Max('nro_despacho'))['max_orden_despacho']
    if not max_orden_despacho:
        max_orden_despacho = 100
    else:
        max_orden_despacho += 1

    orden_despacho = OrdenDespacho.objects.create(venta_id=venta_id, nro_despacho=max_orden_despacho)
    return orden_despacho



def ingreso_venta(datos_venta, datos_formulario, venta_id, tipo):
    try:
        ref = {}
        with transaction.atomic():
            user = 1  # Cambiar por session['usuario_sesion'] si se usa sesiones

            if tipo == '1':
                tipo_ingreso = '1'
            elif tipo == '2':
                tipo_ingreso = '2'
            else:
                tipo_ingreso = 'otro'

            ingreso = Ingreso(
                tipo_ingreso_id=tipo_ingreso,
                fecha=datos_venta['fecha'],
                fecha_registro=datos_venta['fecha'],
                concepto='Ingreso por venta al contado.' if datos_formulario['tipo_pago'] == 'false' else 'Ingreso por venta dada a plazos, el dinero registrado es el monto a cuenta.',
                monto_total=datos_formulario['acuenta'] if datos_formulario['tipo_pago'] == 'true' else datos_venta['total'],
                tipo_registro='AUTOMATICO',
                usuario_id=datos_venta['usuario_id'],
                sucursal_id=datos_venta['sucursal_id']
            )
            ingreso.save()
            ref["ingreso"] = ingreso

            ingreso_venta = IngresoVenta(
                venta_id=venta_id,
                ingreso_id=ingreso.id
            )
            ingreso_venta.save()
            ref["ingreso_venta"] = ingreso_venta

        return ref
    except Exception as e:
        transaction.set_rollback(True)
        return str(e)

@require_POST
def registrar_ingreso(request):
    try:
        ingreso = Ingreso(
            tipo_ingreso_id=request.POST['tipo_ingreso_id'],
            fecha=request.POST['fecha'],
            fecha_registro=request.POST['fecha'],
            concepto=request.POST['concepto'],
            monto_total=request.POST['monto_total'],
            tipo_registro='MANUAL',
          
        )
        ingreso.save()
        return JsonResponse({'status': 'success', 'ingreso': ingreso}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_POST
def eliminar_ingreso(request, ingreso_id):
    try:
        ingreso = get_object_or_404(Ingreso, id=ingreso_id)
        ingreso.estado = 0
        ingreso.monto_total = 0.00
        ingreso.save()
        return JsonResponse({'status': 'success', 'ingreso': ingreso}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

