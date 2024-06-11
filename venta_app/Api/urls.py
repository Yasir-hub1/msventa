from django.urls import path
from venta_app.Api.views import (
    venta_list,
    verVentaId,
    registrar_venta,
    print_nota_venta,
    print_proforma,
    get_proformas,
    get_ventas,
    anular_nota_venta,
    getPagos,
    pagos_x_venta,
    print_pago,
    realizar_pago
)

urlpatterns = [
    path('list/', venta_list, name='venta_list'),
    path('<int:id_venta>/', verVentaId, name='verVentaId'),
    path('registrar_venta/', registrar_venta, name='registrar_venta'),
    path('print_nota_venta/<int:id>/', print_nota_venta, name='print_nota_venta'),
    path('print_proforma/<int:id>/', print_proforma, name='print_proforma'),
    path('proformas/', get_proformas, name='get_proformas'),
    path('ventas/', get_ventas, name='get_ventas'),
    path('anular_nota_venta/<int:id>/', anular_nota_venta, name='anular_nota_venta'),
    path('getPagos/', getPagos, name='getPagos'),
    path('pagos_x_venta/<int:id>/', pagos_x_venta, name='pagos_x_venta'),
    path('print_pago/<int:nro_recibo>/', print_pago, name='print_pago'),
    path('realizar_pago/', realizar_pago, name='realizar_pago'),

]
