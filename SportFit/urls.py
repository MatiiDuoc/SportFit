"""
URL configuration for SportFit project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from SportFit_app import views  
from django.conf.urls.static import static
from django.conf import settings
from rest_framework import routers
from SportFit_app.views import PedidoViewSet

router = routers.DefaultRouter()
router.register(r'api/pedidos', PedidoViewSet)

urlpatterns = [
    path('', views.home, name='home'),
    path('__reload__/', include('django_browser_reload.urls')),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.registro, name='registro'),
    path('recuperar_contrasena/', views.recuperar_contrasena, name='recuperar_contrasena'),
    path('cambiar_contrasena/', views.cambiar_contrasena, name='cambiar_contrasena'),
    path('about/', views.about, name='about'),
    path('accounts/', include('allauth.urls')),
    #========================
    #CLIENTE
    #========================
    path('productos/', views.productos_cliente, name='productos_cliente'),
    path('pedidos/', views.pedidos_cliente, name='pedidos_cliente'),
    path('perfil/', views.perfil_cliente, name='perfil_cliente'),
    path('perfil/editar/', views.editar_perfil_cliente, name='editar_perfil_cliente'),
    path('client/checkout/usuario/', views.checkout_usuario, name='checkout_usuario'),
    path('client/checkout/entrega/', views.checkout_entrega, name='checkout_entrega'),
    path('client/checkout/pago/', views.checkout_pago, name='checkout_pago'),
    path('client/checkout/confirmacion/', views.checkout_confirmacion, name='checkout_confirmacion'),
    path('checkout/exito/', views.compra_exitosa, name='compra_exitosa'),
    path('webpay/iniciar/<int:pedido_id>/', views.iniciar_pago_webpay, name='iniciar_pago_webpay'),
    path('webpay/retorno/', views.webpay_retorno, name='webpay_retorno'),
    path('paypal/iniciar/', views.iniciar_pago_paypal, name='iniciar_pago_paypal'),
    path('paypal/retorno/', views.paypal_retorno, name='paypal_retorno'),
    path('paypal/cancelado/', views.paypal_cancelado, name='paypal_cancelado'),
    path('historial_compras/', views.historial_compras, name='historial_compras'),
    path('carrito/', views.carrito, name='carrito'),
    path('carrito/agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/eliminar/<int:detalle_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('carrito/disminuir/<int:detalle_id>/', views.disminuir_cantidad_carrito, name='disminuir_cantidad_carrito'),
    path('carrito/aumentar/<int:detalle_id>/', views.aumentar_cantidad_carrito, name='aumentar_cantidad_carrito'),
    path('envios/', views.envios, name='envios'),
    path('direcciones/', views.direcciones, name='direcciones'),
    path('pedidos/', views.pedidos, name='pedidos'),
    path('pedidos/detalle/<int:pedido_id>/', views.detalle_pedido, name='detalle_pedido'),
    path('compras/observacion/<int:compra_id>/', views.agregar_observacion, name='agregar_observacion'),
    path('compras/detalle/<int:compra_id>/', views.detalle_compra, name='detalle_compra'),
    path('client/', views.contratar_plan, name='mis_planes'),
    path('producto/<int:producto_id>/comentar/', views.agregar_comentario_producto, name='agregar_comentario_producto'),
    path('seguimiento/<int:pedido_id>/', views.seguimiento_pedido, name='seguimiento_pedido'),
    path('completar_perfil/', views.completar_perfil, name='completar_perfil'),
    #========================   
    #ENTRENADOR
    #======================== 
    path('entrenador/', views.dashboard_entrenador, name='dashboard_entrenador'),
    path('entrenador/perfil/', views.perfil_entrenador, name='perfil_entrenador'), 
    path('entrenador/perfil/editar/', views.editar_perfil_entrenador, name='editar_perfil_entrenador'),
    path('entrenador/clientes/', views.clientes_entrenador, name='clientes_entrenador'),
    path('entrenador/clientes/<int:id>/', views.cliente_detalle_entrenador, name='cliente_detalle_entrenador'),
    path('entrenador/clientes/editar/<int:id>/', views.editar_cliente_entrenador, name='editar_cliente_entrenador'),
    path('entrenador/clientes/eliminar/<int:id>/', views.eliminar_cliente_entrenador, name='eliminar_cliente_entrenador'),
    path('rutinas/', views.rutinas_entrenador, name='rutinas_entrenador'),
    path('rutinas/crear/', views.crear_rutina, name='crear_rutina'),
    path('rutinas/<int:id>/', views.rutina_detalle_entrenador, name='rutina_detalle'),
    path('rutinas/editar/<int:rutina_id>/', views.editar_rutina, name='editar_rutina'),
    path('rutinas/eliminar/<int:rutina_id>/', views.eliminar_rutina, name='eliminar_rutina'),    #========================
    #ADMINISTRADOR
    #========================
    # usuarios
    path('admin/usuarios/', views.usuarios, name='usuarios'),
    path('admin/usuarios/<int:id>/', views.usuario_detalle, name='usuario_detalle'),
    path('admin/usuarios/editar/<int:id>/', views.editar_usuario, name='editar_usuario'),
    path('admin/usuarios/eliminar/<int:id>/', views.eliminar_usuario, name='eliminar_usuario'),
    path('admin/usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    # ventas
    path('admin/ventas/', views.ventas, name='ventas'),
    path('admin/ventas/<int:id>/', views.venta_detalle, name='venta_detalle'),
    path('admin/ventas/editar/<int:id>/', views.editar_venta, name='editar_venta'),
    path('admin/ventas/eliminar/<int:id>/', views.eliminar_venta, name='eliminar_venta'),
    path('admin/ventas/crear/', views.crear_venta, name='crear_venta'),
    # productos (solo admin)
    path('admin/productos/', views.productos, name='productos'),
    path('admin/productos/<int:id>/', views.producto_detalle, name='producto_detalle'),
    path('admin/productos/editar/<int:id>/', views.editar_producto, name='editar_producto'),
    path('admin/productos/eliminar/<int:id>/', views.eliminar_producto, name='eliminar_producto'),
    path('admin/productos/crear/', views.crear_producto, name='crear_producto'),
    # marcas
    path('admin/marcas/', views.marcas,  name='marcas'),
    path('admin/marcas/crear/', views.crear_marca_ajax, name='crear_marca_ajax'),
    path('admin/marcas/editar/<int:id>/', views.editar_marca_ajax, name='editar_marca_ajax'),
    path('admin/marcas/eliminar/<int:id>/', views.eliminar_marca_ajax, name='eliminar_marca_ajax'),
    # proveedores
    path('admin/proveedores/', views.proveedores, name='proveedores'),
    path('admin/proveedores/<int:id>/', views.proveedor_detalle, name='proveedor_detalle'),
    path('admin/proveedores/crear/', views.crear_proveedor_ajax, name='crear_proveedor_ajax'),
    path('admin/proveedores/editar/<int:id>/', views.editar_proveedor_ajax, name='editar_proveedor_ajax'),
    path('admin/proveedores/eliminar/<int:id>/', views.eliminar_proveedor_ajax, name='eliminar_proveedor_ajax'),
    # ordenes
    path('admin/ordenes/', views.ordenes, name='ordenes'),
    path('admin/ordenes/<int:id>/', views.orden_detalle, name='orden_detalle'),
    path('admin/ordenes/editar/<int:id>/', views.editar_orden, name='editar_orden'),
    # perfil
    path('admin/perfil/', views.perfil, name='perfil'),
    path('admin/perfil/editar/', views.editar_perfil, name='editar_perfil'),
    path('admin/perfil/cambiar_contrasena/', views.cambiar_contrasena, name='cambiar_contrasena'),
    path('admin/perfil/editar_foto/', views.editar_foto, name='editar_foto'),
    path('admin/perfil/editar_direccion/', views.editar_direccion, name='editar_direccion'),
    path('admin/perfil/editar_telefono/', views.editar_telefono, name='editar_telefono'),
    path('admin/perfil/editar_email/', views.editar_email, name='editar_email'),
    # dashboard
    path('admin/dashboard/', views.dashboard_administrador, name='dashboard_administrador'),
    # reportes
    path('admin/reportes/', views.reportes, name='reportes'),
    path('admin/', admin.site.urls),
    

] + router.urls

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)