from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction,models
from django.utils import timezone
from venta_app.models import Venta, Pago, NotaVenta, Proforma,OrdenDespacho,Ingreso,IngresoVenta,TipoIngresoEgreso,DetalleVenta
from venta_app.Api.serializer import VentaSerializer, DetalleVentaSerializer, PagoSerializer, NotaVentaSerializer,OrdenDespachoSerializer,ProformaSerializer,IngresoSerializer,IngresoVentaSerializer
from rest_framework import status
from django.db.models import Max
import logging
from django.template.loader import get_template
import os
from django.http import HttpResponse ,JsonResponse
from weasyprint import HTML
from django.utils import timezone
import requests
from django.views.decorators.csrf import csrf_exempt
import json
from django.core.serializers import serialize

logger = logging.getLogger('django')
@api_view(['GET'])
def venta_list(request):
    ventas = Venta.objects.all()
    serializer = VentaSerializer(ventas, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def verVentaId(request, id_venta):
    venta = get_object_or_404(Venta, pk=id_venta)
    serializer = VentaSerializer(venta)
    return Response(serializer.data)






def obtener_producto(producto_id):
    try:
        response = requests.get(f'http://localhost:3000/api/productos/{producto_id}')
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f'Error al obtener el producto: {str(e)}')
@api_view(['POST'])
def registrar_venta(request):
    datos = {}
    try:
        with transaction.atomic():
            data = request.data
            
            tipo = data.get('tipo')
            venta = {
                'tipo_venta': '',
                'estado': 1,
                'observacion_proforma': None,
                'tipo_transaccion': ''
            }

            if tipo == 'nv':
                venta['tipo_venta'] = 'NOTA'
            elif tipo == 'f':
                venta['tipo_venta'] = 'FACTURA'
            elif tipo == 'pr':
                venta['tipo_venta'] = 'PROFORMA'
                venta['estado'] = 0
                observacion = '<p><b>OBSERVACION</b><br><b>1.- Puesto en obra: </b>' + data.get('puesto_obra', '') + '<br>' +\
                            '<b>2.- Tipo de cambio: </b>' + data.get('tipo_cambio', '') + '<br>' +\
                            '<b>3.- Condiciones de entrega: </b>' + data.get('condiciones_entrega', '') + '<br>' +\
                            '<b>4.- Tiempo de entrega: </b>' + data.get('tiempo_entrega', '') + '<br>' +\
                            '<b>5.- Forma de entrega: </b>' + data.get('forma_entrega', '') + '<br>' +\
                            '<b>6.- Forma de pago: </b>' + data.get('forma_pago', '') + '<br>' +\
                            '<h4>' + data.get('nombre_dirigido', '') + '</h4></p>'
                venta['observacion_proforma'] = observacion

                obs = {
                "puesto_obra": data.get('puesto_obra', '').strip() or 'No',
                "tipo_cambio": data.get('tipo_cambio', '').strip() or 'No',
                "condiciones_entrega": data.get('condiciones_entrega', '').strip() or 'No',
                "tiempo_entrega": data.get('tiempo_entrega', '').strip() or 'No',
                "forma_entrega": data.get('forma_entrega', '').strip() or 'No',
                "forma_pago": data.get('forma_pago', '').strip() or 'No',
                "nombre_dirigido": data.get('nombre_dirigido', '').strip() or 'No',
            }

            cliente_id = data.get('cliente')

            transaccion = data.get('trans')
            if transaccion == 'mp':
                venta['tipo_transaccion'] = 'MATERIA'
                obj_venta = {
                    'tipo_pago': data.get('tipo_pago'),
                    'acuenta': float(data.get('a_cuenta', 2)),  # Conversión a float
                    'saldo': float(data.get('saldo', 2))  # Conversión a float
                }
            elif transaccion == 'ot':
                venta['tipo_transaccion'] = 'OTROS'
                obj_venta = {
                    'tipo_pago': False
                }
            print("TIPO PAFO ===",obj_venta)
            venta.update({
                'fecha': timezone.now(),
                'subtotal': float(data.get('subtotal', 0)),  # Conversión a float
                'descuento': float(data.get('descuento', 0)),  # Conversión a float
                'total': float(data.get('total', 0)),  # Conversión a float
                'cliente': cliente_id,
                'usuario': 'admin',
                'reingreso': data.get('suggestion'),
            })

            venta_serializer = VentaSerializer(data=venta)
            venta_serializer.is_valid(raise_exception=True)
            new_venta = venta_serializer.save()
            datos["venta"] = venta_serializer.data

            detalle_productos = data.get('detalle_productos', [])
            for detalle in detalle_productos:
                detalle_venta = {
                    'venta': new_venta.id,
                    'detalle': detalle.get('detalle'),
                    'precio_venta': float(detalle.get('precio', 0)),  # Conversión a float
                    'cantidad': int(detalle.get('cantidad_derivado', 0) if transaccion == 'ot' else detalle.get('cantidad', 0)),  # Conversión a int
                    'subtotal': float(detalle.get('subtotal', 0)),  # Conversión a float
                    'total_pie': 0 if transaccion == 'ot' else round(
                        (float(detalle.get('espesor', 0)) * float(detalle.get('ancho', 0)) * float(detalle.get('largo', 0)) / 12) * int(detalle.get('cantidad', 0)), 2),  # Conversión a float/int
                    'largo_mt': 0 if transaccion == 'ot' else float(detalle.get('largo_mt', 0)),  # Conversión a float
                }

                if transaccion != 'ot':
                    detalle_venta.update({
                        'reingreso': detalle.get('suggestion'),
                        'especie': detalle.get('especie_id'),
                        'espesor': float(detalle.get('espesor', 0)),  # Conversión a float
                        'ancho': float(detalle.get('ancho', 0)),  # Conversión a float
                        'largo': float(detalle.get('largo', 0)),  # Conversión a float
                        'detalle': detalle.get('observacion'),
                    })

                detalle_serializer = DetalleVentaSerializer(data=detalle_venta)
                detalle_serializer.is_valid(raise_exception=True)
                detalle_to_array = detalle_serializer.save()
                datos.setdefault('detalle_venta', []).append(detalle_serializer.data)

                # Obtener información del producto desde la URL
                producto_id = detalle.get('id')  # Ajustar según el nombre del campo del producto
                producto_info = obtener_producto(producto_id)

                # Verificar y reducir el stock del producto
                if producto_info['cantidad'] < detalle_venta['cantidad']:
                    raise Exception(f"Stock insuficiente para el producto {producto_info['nombre']}. Disponible: {producto_info['cantidad']}, solicitado: {detalle_venta['cantidad']}")
                
                producto_info['cantidad'] -= int(detalle_venta['cantidad'])

                # Actualizar el producto en el servicio externo
                update_response = requests.put(f'http://localhost:3000/api/productos/{producto_id}', json={'cantidad': producto_info['cantidad']})
                update_response.raise_for_status()

            if venta['tipo_venta'] != 'PROFORMA':
                datos["orden_venta"] = registrar_orden(new_venta.id)

            tipo_pago = obj_venta['tipo_pago']

            # Convertir tipo_pago a booleano correctamente
            tipo_pago_bool = str(tipo_pago).lower() in ('true', '1')
            print("VERIF y tipo_pago", tipo_pago_bool,obj_venta.get('tipo_pago'),  venta['tipo_venta'] != 'PROFORMA')
            if venta['tipo_venta'] != 'PROFORMA' and tipo_pago_bool==True:
                Venta.objects.filter(id=new_venta.id).update(a_plazos=1)
                datos["venta_modificacion"] = VentaSerializer(get_object_or_404(Venta, id=new_venta.id)).data
            
                nro_recibo = Pago.objects.count() + 1
                pagos = {
                    'venta':  new_venta.pk,
                    'nro_recibo': nro_recibo,
                    'fecha_pago': timezone.now(),
                    'monto_total': venta['total'],
                    'monto_pagado': obj_venta['acuenta'],
                    'monto_saldo': obj_venta['saldo'],
                    'observacion': 'Se hizo el primer pago del total vendido.',
                    'monto_gift_card': data.get('monto_gift_card'),
                    'numero_tarjeta': data.get('numero_tarjeta'),
                    'tipo_pago': data.get('metodo_pago')
                }
                pago_serializer = PagoSerializer(data=pagos)
                pago_serializer.is_valid(raise_exception=True)
                pago_dato = pago_serializer.save()
                datos["pago"] = pago_serializer.data
            
                datos["verrif"] = ingreso_venta(venta, obj_venta, new_venta.id, '1')
            elif venta['tipo_venta'] != 'PROFORMA':
                nro_recibo = Pago.objects.count() + 1
                pagos = {
                    'venta': new_venta.pk,
                    'nro_recibo': nro_recibo,
                    'fecha_pago': timezone.now(),
                    'monto_total': venta['total'],
                    'monto_pagado': venta['total'],
                    'monto_saldo': 0,
                    'observacion': 'Pago por venta al contado.',
                    'monto_gift_card': data.get('monto_gift_card'),
                    'numero_tarjeta': data.get('numero_tarjeta'),
                    'tipo_pago': data.get('metodo_pago')
                }
                pago_serializer = PagoSerializer(data=pagos)
                pago_serializer.is_valid(raise_exception=True)
                pago_dato = pago_serializer.save()
                datos["pago"] = pago_serializer.data

            if venta['tipo_venta'] == 'NOTA':
                datos["nota_venta"] = registro_nota_venta(new_venta.id)
            elif venta['tipo_venta'] == 'PROFORMA':
                datos["proforma"] = registro_proforma(new_venta.id, obs)

            return Response(datos, status=status.HTTP_200_OK)
    except Exception as e:
        transaction.rollback()
        return JsonResponse({'error': str(e)}, status=500)
   
    
def registro_nota_venta(venta_id):
    max_nro_nota = NotaVenta.objects.aggregate(max_nro_nota=models.Max('nro_nota'))['max_nro_nota']
    if not max_nro_nota:
        max_nro_nota = 100
    else:
        max_nro_nota += 1

    nota_venta = NotaVenta.objects.create(venta_id=venta_id, nro_nota=max_nro_nota)
    return NotaVentaSerializer(nota_venta).data

def registro_proforma(venta_id, obs):
  
        max_nro_proforma = Proforma.objects.aggregate(Max('nro_proforma'))['nro_proforma__max']
        if max_nro_proforma is None:
            max_nro_proforma = 100
        else:
            max_nro_proforma += 1
        
        obs['venta'] = venta_id
        obs['nro_proforma'] = max_nro_proforma

        proforma_serializer = ProformaSerializer(data=obs)
        proforma_serializer.is_valid(raise_exception=True)
        proforma = proforma_serializer.save()
        
        return proforma_serializer.data
    
def registrar_orden(venta_id):
    # Obtener el número máximo de despacho
    max_orden_despacho = OrdenDespacho.objects.aggregate(Max('nro_despacho'))['nro_despacho__max']
    
    # Si no existe ningún registro, inicializar a 100, de lo contrario incrementar en 1
    if max_orden_despacho is None:
        max_orden_despacho = 100
    else:
        max_orden_despacho += 1
    
    # Crear el nuevo registro de OrdenDespacho
    nueva_orden = OrdenDespacho.objects.create(venta_id=venta_id, nro_despacho=max_orden_despacho)
    
    # Serializar el nuevo registro de OrdenDespacho
    orden_serializer = OrdenDespachoSerializer(nueva_orden)
    
    return orden_serializer.data



def ingreso_venta(datos_venta, datos_formulario, venta_id, tipo):
    try:
        ref = {}
        with transaction.atomic():
            # Determinar tipo de ingreso
            if tipo == '1':
                tipo_ingreso = 1
            elif tipo == '2':
                tipo_ingreso = 2
            else:
                raise ValueError("Tipo de ingreso no válido")

            # Crear el registro de Ingreso
            ingreso = Ingreso(
                tipo_ingreso=get_object_or_404(TipoIngresoEgreso, pk=tipo_ingreso),
                fecha=datos_venta['fecha'],
                fecha_registro=datos_venta['fecha'],
                concepto='Ingreso por venta al contado.' if datos_formulario['tipo_pago'] in ['false', False,0] else 'Ingreso por venta dada a plazos, el dinero registrado es el monto a cuenta.',
                monto_total=datos_venta['total'] if datos_formulario['tipo_pago'] in ['false', False,0] else datos_formulario['acuenta'],
                tipo_registro='AUTOMATICO',
                usuario=datos_venta['usuario'],
            )
            ingreso.save()
            ref["ingreso"] = IngresoSerializer(ingreso).data

            # Crear el registro de IngresoVenta
            ingreso_venta = IngresoVenta(
                venta=get_object_or_404(Venta, pk=venta_id),
                ingreso=ingreso,
            )
            ingreso_venta.save()
            ref["ingreso_venta"] = IngresoVentaSerializer(ingreso_venta).data

        return ref
    except Exception as e:
        return {'error': str(e)}
    
""" @api_view(['GET'])
def print_nota_venta(request, id):
    try:
        datos = {}
        datos["pago"] = Pago.objects.filter(venta_id=id).first()
        datos["orden_trabajo"] = OrdenDespacho.objects.filter(venta_id=id).first()
        datos["nota_venta"] = NotaVenta.objects.filter(pk=id).first()
        datos["venta"] = get_object_or_404(Venta, pk=id)
        datos["datos"] = DetalleVenta.objects.filter(venta_id=id)
      
        # Agregar la ruta de las librerías de GTK a PATH
        os.add_dll_directory(r"C:\Program Files\GTK3-Runtime Win64\bin")

        template = get_template('template/print_nota_venta.html')
        html_content = template.render(datos)  # Pasar el diccionario 'datos' al template

        # Crear un archivo PDF
        pdf_file = HTML(string=html_content).write_pdf()

        # Preparar la respuesta con el contenido del PDF
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'
        return response
    except Exception as e:
        return HttpResponse(str(e)) """
@api_view(['GET'])       


def print_nota_venta(request, id):
    try:
        datos = {}
        datos["pago"] = Pago.objects.filter(venta_id=id).first()
        datos["orden_trabajo"] = OrdenDespacho.objects.filter(venta_id=id).first()
        datos["nota_venta"] = NotaVenta.objects.filter(venta_id=id).first()
        datos["venta"] = get_object_or_404(Venta, pk=id)

        detalle_venta = DetalleVenta.objects.filter(venta_id=id).select_related('venta')
        datos["datos"] = []

        for item in detalle_venta:
            especie_id = item.especie

            # Hacer la petición POST al endpoint para obtener el nombre de la especie
            url_especie = f'http://localhost:3000/api/especies/{especie_id}'
            response_especie = requests.post(url_especie)
            response_especie.raise_for_status()  # Lanza una excepción si la petición falla
            especie_data = response_especie.json()
            print("GET ESPECIE ", especie_data)
            datos["datos"].append({
                "cantidad": item.cantidad,
                "especie": especie_data['nombre'],  # Suponiendo que el nombre de la especie está en el campo 'nombre'
                "largo": item.largo,
                "ancho": item.ancho,
                "espesor": item.espesor,
                "subtotal": item.subtotal,
                "precio_unitario": round(item.subtotal / item.cantidad, 2) if item.cantidad != 0 else 0

            })

        # Obtener el ID del cliente desde datos["venta"]
        cliente_id = datos["venta"].cliente

        # Hacer la petición GET a la URL externa con el ID del cliente
        url_cliente = f'http://clientemongodb.test:84/api/customers_for_id?id={cliente_id}'
        response_cliente = requests.get(url_cliente)
        response_cliente.raise_for_status()  # Lanza una excepción si la petición falla

        # Convertir la respuesta a JSON
        cliente_data = response_cliente.json()

        # Agregar los datos del cliente al diccionario de datos
        datos["cliente"] = cliente_data

        # Agregar la ruta de las librerías de GTK a PATH (si es necesario)
        os.add_dll_directory(r"C:\Program Files\GTK3-Runtime Win64\bin")

        # Renderizar la plantilla con los datos
        template = get_template('template/print_nota_venta.html')
        html_content = template.render(datos)  # Pasar el diccionario 'datos' al template

        # Crear un archivo PDF
        pdf_file = HTML(string=html_content).write_pdf()

        # Preparar la respuesta con el contenido del PDF para visualizar en el navegador
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="invoice.pdf"'
        return response

    except requests.RequestException as e:
        return HttpResponse(f'Error al realizar la petición: {str(e)}', status=500)
    except Exception as e:
        return HttpResponse(str(e), status=500)
    
@api_view(['GET'])   
def print_proforma(request, id):
    try:
        datos = {}

        # Obtener datos de los modelos
        proforma=get_object_or_404(Proforma, venta_id=id)
       


        datos["proforma"] =proforma
        datos["venta"] = get_object_or_404(Venta, pk=id)
        
        detalle_venta = DetalleVenta.objects.filter(venta_id=id).select_related('venta')
        print("detalle ", detalle_venta)
        # Verificar que detalle_venta sea un queryset
        if not isinstance(detalle_venta, (list, tuple)):
            detalle_venta = list(detalle_venta)
        
        datos["datos"] = []

        for item in detalle_venta:
            especie_id = item.especie  # Asegúrate de obtener el ID de la especie correctamente

            # Hacer la petición POST al endpoint para obtener el nombre de la especie
            url_especie = f'http://localhost:3000/api/especies/{especie_id}'
            response_especie = requests.post(url_especie)
            response_especie.raise_for_status()  # Lanza una excepción si la petición falla
            especie_data = response_especie.json()
            print("especie_data ", especie_data)
            datos["datos"].append({
                "cantidad": item.cantidad,
                "especie": especie_data['nombre'],  # Suponiendo que el nombre de la especie está en el campo 'nombre'
                "largo": item.largo,
                "ancho": item.ancho,
                "espesor": item.espesor,
                "subtotal": item.subtotal,
                "detalles": item.detalle,
                "precio_unitario": round(item.subtotal / item.cantidad, 2) if item.cantidad != 0 else 0
            })

        # Obtener el ID del cliente desde datos["venta"]
        cliente_id = datos["venta"].cliente  # Asegúrate de obtener el ID del cliente correctamente
        print("cliente_id ", cliente_id)
        datos["rango"] = range(20)
        # Hacer la petición GET a la URL externa con el ID del cliente
        url_cliente = f'http://clientemongodb.test:84/api/customers_for_id?id={cliente_id}'
        response_cliente = requests.get(url_cliente)
        response_cliente.raise_for_status()  # Lanza una excepción si la petición falla

        # Convertir la respuesta a JSON
        cliente_data = response_cliente.json()
        print("cliente_data ", cliente_data)
        
        # Agregar los datos del cliente al diccionario de datos
        datos["cliente"] = cliente_data
        print("datos ", datos)
        
        # Renderizar la plantilla
        template = get_template('template/print_proforma.html')
        html_content = template.render(datos)
        
        # Crear el archivo PDF
        pdf_file = HTML(string=html_content).write_pdf()

        # Preparar la respuesta con el contenido del PDF
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="print_proforma.pdf"'  # Cambiar a inline para visualizar
        return response
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)
    
    
@api_view(['GET'])  
def get_proformas(request):
    try:
        # Consultar las proformas que tienen ventas con estado 0
        proformas = Proforma.objects.filter(venta__estado=0).select_related('venta')

        # Construir la lista de ventas con la información necesaria
        ventas_list = []
        for proforma in proformas:
            venta = proforma.venta

            # Obtener el ID del cliente de la venta
            cliente_id = venta.cliente
            print("cliente_id ", cliente_id)

            # Hacer la petición GET a la URL externa con el ID del cliente
            url_cliente = f'http://clientemongodb.test:84/api/customers_for_id?id={cliente_id}'
            response_cliente = requests.get(url_cliente)
            response_cliente.raise_for_status()  # Lanza una excepción si la petición falla

            # Convertir la respuesta a JSON
            cliente_data = response_cliente.json()
            print("cliente_data ", cliente_data)

            venta_info = {
                "id": venta.id,
                "fecha": venta.fecha,
                "total": venta.total,
                "name": cliente_data['name'] if cliente_data else '',
                "nro_proforma": proforma.nro_proforma
            }
            ventas_list.append(venta_info)

        return JsonResponse(ventas_list, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
@api_view(['GET'])
def get_ventas(request):
    try:
        # Consultar las ventas de tipo "NOTA" y con estado 1
        ventas = Venta.objects.filter(tipo_venta='NOTA', estado=1)

        # Construir la lista de ventas con la información necesaria
        ventas_list = []
        for venta in ventas:
            # Obtener la nota de venta y la orden de despacho relacionadas con esta venta
            nota_venta = NotaVenta.objects.get(venta=venta)
            orden_despacho = OrdenDespacho.objects.get(venta=venta)

            # Obtener el ID del cliente de la venta
            cliente_id = venta.cliente
            print("cliente_id ", cliente_id)

            # Hacer la petición GET a la URL externa con el ID del cliente
            url_cliente = f'http://clientemongodb.test:84/api/customers_for_id?id={cliente_id}'
            response_cliente = requests.get(url_cliente)
            response_cliente.raise_for_status()  # Lanza una excepción si la petición falla

            # Convertir la respuesta a JSON
            cliente_data = response_cliente.json()
            print("cliente_data ", cliente_data)

            venta_info = {
                "id": venta.id,
                "fecha": venta.fecha,
                "total": venta.total,
                "name": cliente_data['name'] if cliente_data else '',
                "nro_nota": nota_venta.nro_nota,
                "nro_despacho": orden_despacho.nro_despacho
            }
            ventas_list.append(venta_info)

        return JsonResponse(ventas_list, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    
@api_view(['POST'])
def anular_nota_venta(request, id):
    try:
        # Buscar la venta por su ID
        venta = get_object_or_404(Venta, pk=id)
        
        # Actualizar el estado de la venta
        venta.estado = 0
        venta.save()
        
        return JsonResponse({"message": "Venta anulada correctamente."}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@api_view(['GET'])
def getPagos(request):
    try:
        ventas = Venta.objects.filter(tipo_venta='NOTA', estado=1).exclude(a_plazos=0)
        pagos_list = []

        for venta in ventas:
            print("VENTA ", venta.pk)
            nota_venta = NotaVenta.objects.get(venta_id=venta.pk)
            pagos = Pago.objects.filter(venta_id=venta.pk)
            print("NOTA VENTA ", nota_venta)

            cliente_id = venta.cliente
            response_cliente = requests.get(f'http://clientemongodb.test:84/api/customers_for_id?id={cliente_id}')
            cliente_data = response_cliente.json()

            for pago in pagos:
                pago_info = {
                    "id": venta.id,
                    "fecha": venta.fecha,
                    "estado_pago": venta.a_plazos,
                    "name": cliente_data['name'] if cliente_data else 'Cliente Particular',
                    "nro_nota": nota_venta.nro_nota,
                    "monto_total": pago.monto_total,
                    "a_cuenta": sum(pago.monto_pagado for pago in pagos),
                    "saldo": pago.monto_total - sum(pago.monto_pagado for pago in pagos)
                }
                pagos_list.append(pago_info)

        return JsonResponse(pagos_list, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
@api_view(['GET'])
def pagos_x_venta(request, id):
    try:
        # Obtener la venta por ID
        venta = get_object_or_404(Venta, id=id)
        
        # Obtener el ID del cliente de la venta
        cliente_id = venta.cliente
        
        # Hacer la petición GET a la URL externa con el ID del cliente
        url_cliente = f'http://clientemongodb.test:84/api/customers_for_id?id={cliente_id}'
        response_cliente = requests.get(url_cliente)
        response_cliente.raise_for_status()  # Lanza una excepción si la petición falla

        # Convertir la respuesta a JSON
        cliente_data = response_cliente.json()

        # Obtener los pagos asociados a la venta
        pagos = Pago.objects.filter(venta_id=id).values(
            'nro_recibo', 'monto_pagado', 'fecha_pago', 'tipo_pago', 'venta_id',"monto_total","monto_saldo","observacion",
        )
        # Construir la respuesta
        response_data = {
            "pagos": list(pagos),
            "venta": {
                "id": venta.id,
                "fecha": venta.fecha,
                "total": venta.total,
                "cliente_id": venta.cliente,
            },
            "cliente": cliente_data if cliente_data else {"error": "Cliente no encontrado"}
        }

        return JsonResponse(response_data)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    
def print_pago(request, nro_recibo):
    try:
        datos = {}

        # Obtener el pago
        datos["pago"] = Pago.objects.filter(nro_recibo=nro_recibo).first()

        # Obtener la venta relacionada
        datos["venta"] = get_object_or_404(Venta, id=datos["pago"].venta_id)


        # Obtener el ID del cliente desde datos["venta"]
        cliente_id = datos["venta"].cliente

        # Hacer la petición GET a la URL externa con el ID del cliente
        url_cliente = f'http://clientemongodb.test:84/api/customers_for_id?id={cliente_id}'
        response_cliente = requests.get(url_cliente)
        response_cliente.raise_for_status()  # Lanza una excepción si la petición falla

        # Convertir la respuesta a JSON
        cliente_data = response_cliente.json()

        # Agregar los datos del cliente al diccionario de datos
        datos["customer"] = cliente_data
        datos["rango"] = range(20)
        # Renderizar la plantilla con los datos
        template = get_template('template/print_pago.html')
        html_content = template.render(datos)  # Pasar el diccionario 'datos' al template

        # Crear un archivo PDF
        pdf_file = HTML(string=html_content).write_pdf()

        # Preparar la respuesta con el contenido del PDF para visualizar en el navegador
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="print_pago.pdf"'
        return response

    except requests.RequestException as e:
        return HttpResponse(f'Error al realizar la petición: {str(e)}', status=500)
    except Exception as e:
        return HttpResponse(str(e), status=500)
    
@api_view(['POST'])
def realizar_pago(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                data = json.loads(request.body)

                # Verifica los datos recibidos
                print("Datos recibidos:", data)

                # Obtener el máximo número de recibo y aumentar en 1
                max_nro_recibo = Pago.objects.aggregate(max_nro_recibo=Max('nro_recibo'))['max_nro_recibo'] or 0
                nuevo_nro_recibo = max_nro_recibo + 1

                # Convertir los valores a los tipos de datos correctos
                venta_id = int(data.get('venta_id'))
                monto_total = float(data.get('monto_total'))
                monto_pagado = float(data.get('monto_pagado'))
                monto_saldo = float(data.get('monto_saldo'))
                metodo_pago = int(data.get('metodo_pago'))

                # Crear el objeto Pago
                pago = Pago.objects.create(
                    venta_id=venta_id,
                    nro_recibo=nuevo_nro_recibo,
                    fecha_pago=timezone.now(),
                    monto_total=monto_total,
                    monto_pagado=monto_pagado,
                    monto_saldo=monto_saldo,
                    observacion=data.get('observacion'),
                    tipo_pago=metodo_pago
                )

                # Si el monto saldo es 0, actualizar la venta
                if monto_saldo == 0:
                    venta = get_object_or_404(Venta, pk=venta_id)
                    venta.a_plazos = 2
                    venta.save()

                # Crear el objeto Ingreso
                ingreso = Ingreso.objects.create(
                    tipo_ingreso_id=2,
                    fecha=timezone.now(),
                    fecha_registro=timezone.now(),
                    concepto=data.get('observacion', 'Pago a cuenta.'),
                    monto_total=monto_total,
                    tipo_registro="AUTOMATICO"
                )

                # Serializar los objetos antes de devolverlos
                pago_data = json.loads(serialize('json', [pago]))[0]['fields']
                ingreso_data = json.loads(serialize('json', [ingreso]))[0]['fields']

                # Devolver los datos guardados
                datos = {
                    'pago': pago_data,
                    'venta': venta_id if monto_saldo == 0 else None,
                    'ingreso': ingreso_data
                }
                return JsonResponse(datos, safe=False)

        except Exception as e:
            transaction.rollback()
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Método no permitido'}, status=405)