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
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('__reload__/', include('django_browser_reload.urls')),
    #========================
    #CLIENTE
    #========================
    #ENTRENADOR
    #========================
    #NUTRICIONISTA
    #========================



    
    #========================
    #ADMINISTRADOR
    #========================
    # usuarios
    path('usuarios/', views.usuarios, name='usuarios'),
    path('usuarios/<int:id>/', views.usuario_detalle, name='usuario_detalle'),
    path('usuarios/editar/<int:id>/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/eliminar/<int:id>/', views.eliminar_usuario, name='eliminar_usuario'),
    path('usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    #ventas
    path('ventas/', views.ventas, name='ventas'),
    path('ventas/<int:id>/', views.venta_detalle, name='venta_detalle'),
    path('ventas/editar/<int:id>/', views.editar_venta, name='editar_venta'),
    path('ventas/eliminar/<int:id>/', views.eliminar_venta, name='eliminar_venta'),
    path('ventas/crear/', views.crear_venta, name='crear_venta'),
    #stock
    path('stock/', views.stock, name='stock'),
    path('stock/<int:id>/', views.stock_detalle, name='stock_detalle'),
    path('stock/editar/<int:id>/', views.editar_stock, name='editar_stock'),
    path('stock/eliminar/<int:id>/', views.eliminar_stock, name='eliminar_stock'),
    path('stock/crear/', views.crear_stock, name='crear_stock'),
    #productos
    path('productos/', views.productos, name='productos'),
    path('productos/<int:id>/', views.producto_detalle, name='producto_detalle'),
    path('productos/editar/<int:id>/', views.editar_producto, name='editar_producto'),
    path('productos/eliminar/<int:id>/', views.eliminar_producto, name='eliminar_producto'),
    path('productos/crear/', views.crear_producto, name='crear_producto'),
    #categorias
    path('categorias/', views.categorias, name='categorias'),
    path('categorias/<int:id>/', views.categoria_detalle, name='categoria_detalle'),
    path('categorias/editar/<int:id>/', views.editar_categoria, name='editar_categoria'),
    path('categorias/eliminar/<int:id>/', views.eliminar_categoria, name='eliminar_categoria'),
    path('categorias/crear/', views.crear_categoria, name='crear_categoria'),
    #marcas
    path('marcas/', views.marcas,  name='marcas'),
    path('marcas/<int:id>/', views.marca_detalle, name='marca_detalle'),
    path('marcas/editar/<int:id>/', views.editar_marca, name='editar_marca'),
    path('marcas/eliminar/<int:id>/', views.eliminar_marca, name='eliminar_marca'),
    path('marcas/crear/', views.crear_marca, name='crear_marca'),
    #proveedores
    path('proveedores/', views.proveedores, name='proveedores'),
    path('proveedores/<int:id>/', views.proveedor_detalle, name='proveedor_detalle'),
    path('proveedores/editar/<int:id>/', views.editar_proveedor, name='editar_proveedor'),
    path('proveedores/eliminar/<int:id>/', views.eliminar_proveedor, name='eliminar_proveedor'),
    path('proveedores/crear/', views.crear_proveedor, name='crear_proveedor'),
    #ordenes
    path('ordenes/', views.ordenes, name='ordenes'),
    path('ordenes/<int:id>/', views.orden_detalle, name='orden_detalle'),
    path('ordenes/editar/<int:id>/', views.editar_orden, name='editar_orden'),
    #perfil
    path('perfil/', views.perfil, name='perfil'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
    path('perfil/cambiar_contrasena/', views.cambiar_contrasena, name='cambiar_contrasena'),
    path('perfil/editar_foto/', views.editar_foto, name='editar_foto'),
    path('perfil/editar_direccion/', views.editar_direccion, name='editar_direccion'),
    path('perfil/editar_telefono/', views.editar_telefono, name='editar_telefono'),
    path('perfil/editar_email/', views.editar_email, name='editar_email'),
    #dashboard
    path('dashboard_administrador/', views.dashboard_administrador, name='dashboard_administrador'),

]