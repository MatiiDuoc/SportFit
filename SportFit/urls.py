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
from SportFit_app import views  # Cambiado para importar desde SportFit_app

urlpatterns = [
    path('', views.home, name='home'),
    path('__reload__/', include('django_browser_reload.urls')),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.registro, name='registro'),
    path('recuperar_contrasena/', views.recuperar_contrasena, name='recuperar_contrasena'),
    path('cambiar_contrasena/', views.cambiar_contrasena, name='cambiar_contrasena'),
    #========================
    #CLIENTE
    #========================
    path('productos/', views.productos_cliente, name='productos_cliente'),
    #ENTRENADOR
    #========================
    #NUTRICIONISTA
    #========================



    
    #========================
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
    path('admin/marcas/<int:id>/', views.marca_detalle, name='marca_detalle'),
    path('admin/marcas/editar/<int:id>/', views.editar_marca, name='editar_marca'),
    path('admin/marcas/eliminar/<int:id>/', views.eliminar_marca, name='eliminar_marca'),
    path('admin/marcas/crear/', views.crear_marca, name='crear_marca'),
    # proveedores
    path('admin/proveedores/', views.proveedores, name='proveedores'),
    path('admin/proveedores/<int:id>/', views.proveedor_detalle, name='proveedor_detalle'),
    path('admin/proveedores/editar/<int:id>/', views.editar_proveedor, name='editar_proveedor'),
    path('admin/proveedores/eliminar/<int:id>/', views.eliminar_proveedor, name='eliminar_proveedor'),
    path('admin/proveedores/crear/', views.crear_proveedor, name='crear_proveedor'),
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
    path('dashboard/dashboard_administrador/', views.dashboard_administrador, name='dashboard_administrador'),
    # reportes
    path('admin/reportes/', views.reportes, name='reportes'),
    path('admin/', admin.site.urls),
    

]