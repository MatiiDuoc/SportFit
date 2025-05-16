from django.shortcuts import render
from django.http import HttpResponse
import json
import requests
from django.contrib.auth.models import User  # O tu modelo personalizado
import urllib3
from requests.exceptions import RequestException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Create your views here.
#----------------------------------
# Cliente
#----------------------------------
# Home
def home(request):
    return render(request, 'home.html')
def login_view(request):
    # Vista para el inicio de sesión
    return render(request, 'login/login.html')
def logout_view(request):
    # Vista para cerrar sesión
    return render(request, 'logout.html')
def registro(request):
    # Vista para el registro de nuevos usuarios
    return render(request, 'registro/registro.html')
def recuperar_contrasena(request):
    # Vista para recuperar la contraseña
    return render(request, 'recuperar_contrasena/recuperar_contrasena.html')
def cambiar_contrasena(request):
    # Vista para cambiar la contraseña
    return render(request, 'cambiar_contrasena.html')
def productos_cliente(request):
    # Vista para listar productos para el cliente
    return render(request, 'client/productos.html', {})


#----------------------------------
# Administrador
#----------------------------------
def dashboard_administrador(request):
    # Datos de ejemplo (pueden venir de la base de datos)
    ventas = [1200, 1900, 3000, 5000]
    semanas = ['Semana 1', 'Semana 2', 'Semana 3', 'Semana 4']

    # Pasar los datos al contexto
    context = {
        'ventas': json.dumps(ventas),  # Convertir a JSON para usar en JavaScript
        'semanas': json.dumps(semanas),
    }
    return render(request, 'admin/dashboard/dashboard.html')
# -------------------- reportes --------------------
def reportes(request):
    # Vista para mostrar reportes
    return render(request, 'admin/reportes/reporte.html', {})

# -------------------- Usuarios --------------------
def obtener_usuarios_api():
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    driver.get('https://www.saborlatinochile.cl/duoc/servicio_web_sportfit.php?i=1')
    import time
    time.sleep(2)  # Espera a que cargue la página y el JSON
    try:
        # Si el JSON se muestra en un <pre>
        data = driver.find_element("tag name", "pre").text
        usuarios = json.loads(data)
    except Exception as e:
        print("ERROR OBTENIENDO USUARIOS:", e)
        usuarios = []
    driver.quit()
    return usuarios

def usuarios(request):
    try:
        usuarios_api = obtener_usuarios_api()
    except Exception as e:
        print("ERROR:", e)
        usuarios_api = []
    context = {'usuarios_api': usuarios_api}
    return render(request, 'admin/usuario/usuarios.html', context)

def usuario_detalle(request):
    # Vista para mostrar detalles de un usuario
    return render(request, 'usuario/usuario_detalle.html', {})

def editar_usuario(request):
    # Vista para editar un usuario
    return render(request, 'usuario/editar_usuario.html', {})

def eliminar_usuario(request):
    # Vista para eliminar un usuario
    return render(request, 'usuario/eliminar_usuario.html', {})

def crear_usuario(request):
    # Vista para crear un usuario
    return render(request, 'usuario/crear_usuario.html', {})

# -------------------- Ventas --------------------
def ventas(request):
    # Vista para listar ventas
    return render(request, 'admin/venta/ventas.html', {})

def venta_detalle(request):
    # Vista para mostrar detalles de una venta
    return render(request, 'venta/venta_detalle.html', {})

def editar_venta(request):
    # Vista para editar una venta
    return render(request, 'venta/editar_venta.html', {})

def eliminar_venta(request):
    # Vista para eliminar una venta
    return render(request, 'venta/eliminar_venta.html', {})

def crear_venta(request):
    # Vista para crear una venta
    return render(request, 'venta/crear_venta.html', {})

# -------------------- Productos --------------------
def productos(request):
    # Vista para listar productos
    return render(request, 'admin/productos/productos.html', {})

def producto_detalle(request):
    # Vista para mostrar detalles de un producto
    return render(request, 'productos/producto_detalle.html', {})

def editar_producto(request):
    # Vista para editar un producto
    return render(request, 'productos/editar_producto.html', {})

def eliminar_producto(request):
    # Vista para eliminar un producto
    return render(request, 'productos/eliminar_producto.html', {})

def crear_producto(request):
    # Vista para crear un producto
    return render(request, 'productos/crear_producto.html', {})
# -------------------- Marcas --------------------
def marcas(request):
    # Vista para listar marcas
    return render(request, 'admin/marcas/marcas.html', {})

def marca_detalle(request):
    # Vista para mostrar detalles de una marca
    return render(request, 'marcas/marca_detalle.html', {})

def editar_marca(request):
    # Vista para editar una marca
    return render(request, 'marcas/editar_marca.html', {})

def eliminar_marca(request):
    # Vista para eliminar una marca
    return render(request, 'marcas/eliminar_marca.html', {})

def crear_marca(request):
    # Vista para crear una marca
    return render(request, 'marcas/crear_marca.html', {})

# -------------------- Proveedores --------------------
def proveedores(request):
    # Vista para listar proveedores
    return render(request, 'admin/proveedores/proveedores.html', {})

def proveedor_detalle(request):
    # Vista para mostrar detalles de un proveedor
    return render(request, 'proveedores/proveedor_detalle.html', {})

def editar_proveedor(request):
    # Vista para editar un proveedor
    return render(request, 'proveedores/editar_proveedor.html', {})

def eliminar_proveedor(request):
    # Vista para eliminar un proveedor
    return render(request, 'proveedores/eliminar_proveedor.html', {})

def crear_proveedor(request):
    # Vista para crear un proveedor
    return render(request, 'proveedores/crear_proveedor.html', {})

# -------------------- Órdenes --------------------
def ordenes(request):
    # Vista para listar órdenes
    return render(request, 'admin/ordenes/ordenes.html', {})

def orden_detalle(request):
    # Vista para mostrar detalles de una orden
    return render(request, 'ordenes/orden_detalle.html', {})

def editar_orden(request):
    # Vista para editar una orden
    return render(request, 'ordenes/editar_orden.html', {})

# -------------------- Perfil --------------------
def perfil(request):
    # Vista para mostrar el perfil del usuario
    return render(request, 'admin/perfil/perfil.html', {})

def editar_perfil(request):
    # Vista para editar el perfil del usuario
    return render(request, 'perfil/editar_perfil.html', {})

def cambiar_contrasena(request):
    # Vista para cambiar la contraseña del usuario
    return render(request, 'perfil/cambiar_contrasena.html', {})

def editar_foto(request):
    # Vista para editar la foto del usuario
    return render(request, 'perfil/editar_foto.html', {})

def editar_direccion(request):
    # Vista para editar la dirección del usuario
    return render(request, 'perfil/editar_direccion.html', {})

def editar_telefono(request):
    # Vista para editar el teléfono del usuario
    return render(request, 'perfil/editar_telefono.html', {})

def editar_email(request):
    # Vista para editar el email del usuario
    return render(request, 'perfil/editar_email.html', {})
