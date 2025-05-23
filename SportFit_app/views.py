from django.db import IntegrityError
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
import json
import requests
from django.contrib.auth.models import User  
import urllib3
from requests.exceptions import RequestException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from .models import *  
from django.contrib import messages
from django.views.decorators.http import require_POST
from django import forms
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from transbank.common.integration_type import IntegrationType
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.options import WebpayOptions
import paypalrestsdk

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = '__all__'
        labels = {
            'id_categoria': 'Categoría',
            'id_marca': 'Marca',
        }

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = '__all__'
        labels = {
            'id_comuna': 'Comuna',
            'id_genero': 'Género',
            'id_plan': 'Plan de Entrenamiento',
        }
        
class MarcaForm(forms.ModelForm):
    class Meta:
        model = Marca
        fields = '__all__'

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = '__all__'
        
class EditarPerfilClienteForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = [
            'nombre',
            'apellido',
            'telefono',
            'direccion',
            'tel_emergencia'
        ]



urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Create your views here.
#----------------------------------
# Cliente
#----------------------------------
# views.py

@login_required
def pedidos_cliente(request):
    usuario = Usuario.objects.get(correo=request.user.email)
    pedidos = Pedido.objects.filter(usuario=usuario).order_by('-fecha_creacion')
    return render(request, 'client/pedidos.html', {'pedidos': pedidos})
def home(request):
    return render(request, 'home.html')
def historial_compras(request):
    # Vista para el historial de compras
    return render(request, 'client/historial_compras.html')
def envios(request):
    # Vista para los envíos
    return render(request, 'client/envios.html')
@login_required
def carrito(request):
    usuario = Usuario.objects.filter(correo=request.user.email).first()
    carrito = Carrito.objects.filter(id_usuario=usuario, estado='activo').first()
    productos = []
    cantidad = 0
    if carrito:
        detalles = DetalleCarrito.objects.filter(id_carrito=carrito)
        for detalle in detalles:
            producto = detalle.id_producto
            img = producto.imagen
            if hasattr(img, 'url'):
                img_url = img.url
            else:
                img_url = img if img else ''
            productos.append({
                'id_detalle_carrito': detalle.id_detalle_carrito,  # <-- agrega esta línea
                'nombre': producto.nombre_producto,
                'imagen': img_url,
                'cantidad': detalle.cantidad,
                'precio': detalle.precio,
                'subtotal': detalle.precio * detalle.cantidad,
            })
            cantidad += detalle.cantidad
    return render(request, 'client/carrito.html', {
        'carrito_cantidad': cantidad,
        'carrito_productos': productos,
    })
# Vista para agregar un producto al carrito
@login_required
def agregar_al_carrito(request, producto_id):
    if request.method == 'POST':
        print("POST recibido para producto:", producto_id)
        usuario = Usuario.objects.filter(correo=request.user.email).first()
        print("Usuario:", usuario)
        producto = get_object_or_404(Producto, pk=producto_id)
        print("Producto:", producto)

        carrito = Carrito.objects.filter(id_usuario=usuario, estado='activo').first()
        print("Carrito encontrado:", carrito)
        if not carrito:
            carrito = Carrito.objects.create(
                id_usuario=usuario,
                estado='activo'
            )
            print("Carrito creado:", carrito)

        detalle = DetalleCarrito.objects.filter(
            id_producto=producto,
            id_carrito=carrito
        ).first()
        print("Detalle encontrado:", detalle)

        if detalle:
            detalle.cantidad += 1
            detalle.save()
            print("Cantidad actualizada:", detalle.cantidad)
        else:
            DetalleCarrito.objects.create(
                cantidad=1,
                precio=producto.precio,
                id_producto=producto,
                id_carrito=carrito
            )
            print("Detalle creado para producto:", producto_id)
        return redirect('productos_cliente')
    else:
        print("No es POST")
        return redirect('productos_cliente')
    
@login_required
def eliminar_del_carrito(request, detalle_id):
    detalle = get_object_or_404(DetalleCarrito, pk=detalle_id)
    detalle.delete()
    return redirect('carrito')

@login_required
def disminuir_cantidad_carrito(request, detalle_id):
    detalle = get_object_or_404(DetalleCarrito, pk=detalle_id)
    if detalle.cantidad > 1:
        detalle.cantidad -= 1
        detalle.save()
    else:
        detalle.delete()
    return redirect('carrito')
    
@login_required
def direcciones(request):
    usuario = Usuario.objects.filter(correo=request.user.email).first()
    return render(request, 'client/direcciones.html', {
        'direcciones': [usuario] if usuario and usuario.direccion else [],
        'usuario_extra': usuario,
    })
    

def checkout_usuario(request):
    usuario = Usuario.objects.filter(correo=request.user.email).first()
    if request.method == 'POST':
        request.session['checkout_usuario'] = {
            'rut': request.POST['rut'],
            'nombre': request.POST['nombre'],
            'direccion': request.POST['direccion'],
            'telefono': request.POST['telefono'],
        }
        return redirect('checkout_entrega')
    return render(request, 'client/checkout/usuario.html', {
        'usuario': usuario,
    })

def checkout_entrega(request):
    usuario = Usuario.objects.filter(correo=request.user.email).first()
    if request.method == 'POST':
        request.session['checkout_entrega'] = {
            'tipo_entrega': request.POST['tipo_entrega'],
            'direccion_entrega': request.POST.get('direccion_entrega', ''),
        }
        return redirect('checkout_pago')
    return render(request, 'client/checkout/entrega.html', {
        'usuario': usuario,
    })

def checkout_pago(request):
    usuario = Usuario.objects.filter(correo=request.user.email).first()
    if request.method == 'POST':
        request.session['checkout_pago'] = {
            'metodo_pago': request.POST['metodo_pago'],
            'detalles_pago': request.POST.get('detalles_pago', ''),
        }
        return redirect('checkout_confirmacion')
    return render(request, 'client/checkout/pago.html', {
        'usuario': usuario,
    })


@login_required
def checkout_confirmacion(request):
    usuario = Usuario.objects.filter(correo=request.user.email).first()
    entrega = request.session.get('checkout_entrega', {})
    pago = request.session.get('checkout_pago', {})

    carrito = Carrito.objects.filter(id_usuario=usuario, estado='activo').first()
    detalles = DetalleCarrito.objects.filter(id_carrito=carrito)

    carrito_productos = []
    carrito_cantidad = 0
    carrito_total = 0

    for detalle in detalles:
        producto = detalle.id_producto
        img = producto.imagen
        img_url = img.url if hasattr(img, 'url') else (img if img else '')
        subtotal = detalle.precio * detalle.cantidad
        carrito_productos.append({
            'nombre': producto.nombre_producto,
            'imagen': img_url,
            'cantidad': detalle.cantidad,
            'precio': detalle.precio,
            'subtotal': subtotal,
        })
        carrito_cantidad += detalle.cantidad
        carrito_total += subtotal

    if request.method == 'POST':
        metodo = pago.get('metodo_pago', '')
        if metodo == 'webpay':
            return redirect('iniciar_pago_webpay', pedido_id=carrito.id_carrito)
        elif metodo == 'paypal':
            return redirect('iniciar_pago_paypal')
        else:
            # Otros métodos de pago (ej: transferencia, efectivo)
            pedido = Pedido.objects.create(
                usuario=usuario,
                carrito=carrito,
                direccion_entrega=entrega.get('direccion_entrega', ''),
                tipo_entrega=entrega.get('tipo_entrega', ''),
                metodo_pago=metodo,
                total=carrito_total,
                estado='pendiente'
            )
            detalles.delete()
            carrito.estado = 'finalizado'
            carrito.save()
            request.session.pop('checkout_usuario', None)
            request.session.pop('checkout_entrega', None)
            request.session.pop('checkout_pago', None)
            return redirect('compra_exitosa')

    return render(request, 'client/checkout/confirmacion.html', {
        'usuario': usuario,
        'entrega': entrega,
        'pago': pago,
        'carrito_productos': carrito_productos,
        'carrito_cantidad': carrito_cantidad,
        'carrito_total': carrito_total,
    })
# -------------------- Webpay --------------------
def iniciar_pago_webpay(request, pedido_id):
    print("===> Entrando a iniciar_pago_webpay")
    pedido = get_object_or_404(Pedido, id_pedido=pedido_id)
    print("Pedido:", pedido)
    buy_order = str(pedido.id_pedido)
    session_id = str(request.user.id)
    amount = 1000  # monto fijo para pruebas
    return_url = request.build_absolute_uri('/webpay/retorno/')
    
    # Parámetros de pruebas de Transbank
    commerce_code = '597055555532'
    api_key = 'X'  # <-- ¡Esto debe ser 'X' para integración!
    integration_url = 'https://webpay3gint.transbank.cl'
    print("=== INICIANDO WEBPAY ===")
    print("Commerce Code:", commerce_code)
    print("API Key:", api_key)
    print("Integration URL:", integration_url)
    print("Buy Order:", buy_order)
    print("Session ID:", session_id)
    print("Amount:", amount)
    print("Return URL:", return_url)    

    options = WebpayOptions(commerce_code, api_key, integration_url)
    transaction = Transaction(options)
    try:
        print("===> Llamando a transaction.create()")
        response = transaction.create(
            buy_order=buy_order,
            session_id=session_id,
            amount=amount,
            return_url=return_url
        )
        print("===> Respuesta de Webpay:", response)
        url = response['url']
        token = response['token']
        return render(request, 'webpay/redirect.html', {'url': url, 'token': token})
    except Exception as e:
        print("===> ERROR en Webpay:", e)
        return render(request, 'webpay/error.html', {'error': str(e)})

def webpay_retorno(request):
    token = request.POST.get('token_ws')
    response = Transaction.commit(token)
    if response['status'] == 'AUTHORIZED':
        # Recupera datos de sesión
        usuario = Usuario.objects.filter(correo=request.user.email).first()
        entrega = request.session.get('checkout_entrega', {})
        pago = request.session.get('checkout_pago', {})
        carrito = Carrito.objects.filter(id_usuario=usuario, estado='activo').first()
        detalles = DetalleCarrito.objects.filter(id_carrito=carrito)
        carrito_total = sum(d.precio * d.cantidad for d in detalles)
        # Crea el pedido solo si el pago fue exitoso
        pedido = Pedido.objects.create(
            usuario=usuario,
            carrito=carrito,
            direccion_entrega=entrega.get('direccion_entrega', ''),
            tipo_entrega=entrega.get('tipo_entrega', ''),
            metodo_pago=pago.get('metodo_pago', ''),
            total=carrito_total,
            estado='pagado'
        )
        # Finaliza el carrito
        detalles.delete()
        carrito.estado = 'finalizado'
        carrito.save()
        # Limpia la sesión
        request.session.pop('checkout_usuario', None)
        request.session.pop('checkout_entrega', None)
        request.session.pop('checkout_pago', None)
        return redirect('compra_exitosa')
    else:
        error_msg = response.get('status', 'Pago no autorizado')
        return render(request, 'webpay/error.html', {'error': error_msg})

#paypal
paypalrestsdk.configure({
    "mode": "sandbox",  # sandbox o live
    "client_id": "AQOJfhilIjFvum229XltMVFSdB7s90R8FP7FgBOTrq0vQG4hjq0mnWaWBXG2C2BdTih6jLCyERQt1BJE",
    "client_secret": "ELtDyBybhL4tZfKRe1GXmeUgcWPVY036SDwVNkIts7_YcUQHyfuCLaWShl4WHXY9bbDGUqL90cVzU0po"
})

def iniciar_pago_paypal(request):
    usuario = Usuario.objects.filter(correo=request.user.email).first()
    carrito = Carrito.objects.filter(id_usuario=usuario, estado='activo').first()
    detalles = DetalleCarrito.objects.filter(id_carrito=carrito)
    carrito_total = sum(d.precio * d.cantidad for d in detalles)

    # PayPal requiere el monto como string y con dos decimales
    total_usd = "{:.2f}".format(carrito_total / 900)  # Ejemplo: divide por 900 si tu precio está en CLP y quieres USD

    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {"payment_method": "paypal"},
        "redirect_urls": {
            "return_url": "http://localhost:8000/paypal/retorno/",
            "cancel_url": "http://localhost:8000/paypal/cancelado/"
        },
        "transactions": [{
            "amount": {
                "total": total_usd,
                "currency": "USD"
            },
            "description": "Pago en SportFit"
        }]
    })

    if payment.create():
        for link in payment.links:
            if link.method == "REDIRECT":
                return redirect(link.href)
    else:
        return render(request, 'paypal/error.html', {'error': payment.error})

def paypal_retorno(request):
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')
    payment = paypalrestsdk.Payment.find(payment_id)
    if payment.execute({"payer_id": payer_id}):
        # Lógica igual que en webpay_retorno
        usuario = Usuario.objects.filter(correo=request.user.email).first()
        entrega = request.session.get('checkout_entrega', {})
        pago = request.session.get('checkout_pago', {})
        carrito = Carrito.objects.filter(id_usuario=usuario, estado='activo').first()
        detalles = DetalleCarrito.objects.filter(id_carrito=carrito)
        carrito_total = sum(d.precio * d.cantidad for d in detalles)
        # Crea el pedido solo si el pago fue exitoso
        pedido = Pedido.objects.create(
            usuario=usuario,
            carrito=carrito,
            direccion_entrega=entrega.get('direccion_entrega', ''),
            tipo_entrega=entrega.get('tipo_entrega', ''),
            metodo_pago=pago.get('metodo_pago', ''),
            total=carrito_total,
            estado='pagado'
        )
        # Finaliza el carrito
        detalles.delete()
        carrito.estado = 'finalizado'
        carrito.save()
        # Limpia la sesión
        request.session.pop('checkout_usuario', None)
        request.session.pop('checkout_entrega', None)
        request.session.pop('checkout_pago', None)
        return redirect('compra_exitosa')
    else:
        return render(request, 'paypal/error.html', {'error': payment.error})

def paypal_cancelado(request):
    return render(request, 'paypal/cancelado.html')

def compra_exitosa(request):
    return render(request, 'client/checkout/compra_exitosa.html')


def pedidos(request):
    # Vista para los pedidos
    return render(request, 'client/pedidos.html')
# -------------------- Login --------------------
def logout_view(request):
    # Vista para cerrar sesión
    logout(request)
    return render(request, 'home.html')

# -------------------- Registro --------------------
def registro(request):
    regiones = Region.objects.all()
    comunas = Comuna.objects.all()
    generos = Genero.objects.all()
    planes = PlanEntrenamiento.objects.all()

    if request.method == 'POST':
        rut = request.POST.get('rut')
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        correo = request.POST.get('correo_electronico')
        telefono = request.POST.get('telefono')
        telefono_emergencia = request.POST.get('telefono_emergencia')
        direccion = request.POST.get('direccion')
        contrasena = request.POST.get('contrasena')
        id_comuna = request.POST.get('id_comuna')
        id_genero = request.POST.get('id_genero')
        id_plan = request.POST.get('id_plan')  # Puede ser vacío

        # Validaciones de unicidad
        if User.objects.filter(username=correo).exists() or Usuario.objects.filter(correo=correo).exists():
            messages.error(request, "El correo ya está registrado.")
            return render(request, 'registro/registro.html', {
                'regiones': regiones,
                'comunas': comunas,
                'generos': generos,
                'planes': planes
            })
        if Usuario.objects.filter(rut=rut).exists():
            messages.error(request, "El RUT ya está registrado.")
            return render(request, 'registro/registro.html', {
                'regiones': regiones,
                'comunas': comunas,
                'generos': generos,
                'planes': planes
            })

        # Crea el usuario Django
        user = User.objects.create_user(
            username=correo,
            email=correo,
            password=contrasena,
            first_name=nombre,
            last_name=apellido
        )

        usuario_kwargs = {
            'rut': rut,
            'nombre': nombre,
            'apellido': apellido,
            'correo': correo,
            'telefono': telefono,
            'tel_emergencia': telefono_emergencia,
            'direccion': direccion,
            'contrasena': contrasena,
            'id_comuna_id': id_comuna,
            'id_genero_id': id_genero,
            'tipo_usuario': 'cliente',  # Solo clientes pueden registrarse
        }
        if id_plan:
            usuario_kwargs['id_plan_id'] = id_plan

        nuevo_usuario = Usuario.objects.create(**usuario_kwargs)
        print("Cliente creado:", nuevo_usuario)
    

        messages.success(request, "Registro exitoso. Ahora puedes iniciar sesión.")
        return redirect('login')

    return render(request, 'registro/registro.html', {
        'regiones': regiones,
        'comunas': comunas,
        'generos': generos,
        'planes': planes
    })

def login_view(request):
    if request.method == 'POST':
        correo = request.POST['email']
        contrasena = request.POST['password']

        # Buscar usuario por correo
        user_obj = User.objects.filter(email=correo).first()
        if user_obj:
            username = user_obj.username
        else:
            username = correo  # Por si acaso el username es el correo

        user = authenticate(request, username=username, password=contrasena)
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('dashboard_administrador')
            elif hasattr(user, 'cliente'):
                return redirect('productos_cliente')
            else:
                return redirect('home')
        else:
            return render(request, 'login/login.html', {'error': 'Credenciales inválidas'})
    return render(request, 'login/login.html')

def recuperar_contrasena(request):
    # Vista para recuperar la contraseña
    return render(request, 'recuperar_contrasena/recuperar_contrasena.html')
def cambiar_contrasena(request):
    # Vista para cambiar la contraseña
    return render(request, 'cambiar_contrasena.html')
def productos_cliente(request):
    productos = Producto.objects.all()
    marcas = Marca.objects.all()

    # Filtro por marca
    marca_id = request.GET.get('brand')
    if marca_id:
        productos = productos.filter(id_marca=marca_id)

    # Filtro por precio máximo
    precio_max = request.GET.get('price')
    if precio_max:
        productos = productos.filter(precio__lte=precio_max)

    # Filtro por búsqueda (nombre o descripción)
    search = request.GET.get('search')
    if search:
        productos = productos.filter(
            nombre_producto__icontains=search
        ) | productos.filter(
            descripcion__icontains=search
        )

    return render(request, 'client/productos.html', {
        'productos': productos,
        'marcas': marcas,
    })


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
    usuarios_locales = Usuario.objects.all()
    paginator = Paginator(usuarios_locales, 10)  # 10 por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'usuarios_api': usuarios_api,
        'usuarios_locales': page_obj,  # paginados
    }
    return render(request, 'admin/usuario/usuarios.html', context)

def usuario_detalle(request):
    # Vista para mostrar detalles de un usuario
    return render(request, 'usuario/usuario_detalle.html', {})

def editar_usuario(request, id):
    usuario = get_object_or_404(Usuario, pk=id)
    if request.method == 'POST':
        form = Usuario(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            return redirect('usuarios')
    else:
        form = Usuario(instance=usuario)
    return

@require_POST
def eliminar_usuario(request, id):
    usuario = get_object_or_404(Usuario, pk=id)
    usuario.delete()
    return redirect('usuarios')

def crear_usuario(request):
    # Vista para crear un usuario
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                return redirect('usuarios')
            except IntegrityError:
                form.add_error(None, "Ya existe un usuario con ese identificador o valor único.")
    else:
        form = UsuarioForm()
    return render(request, 'admin/usuario/crear_usuario.html', {'form': form})

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
    productos = Producto.objects.all()
    marcas = Marca.objects.all()
    # Filtro por marca (ajusta el nombre del parámetro según tu select)
    marca_id = request.GET.get('brand')  # o 'marca', según tu formulario
    if marca_id:
        productos = productos.filter(id_marca=marca_id)

    # Filtro por precio máximo
    precio_max = request.GET.get('price')
    if precio_max:
        productos = productos.filter(precio__lte=precio_max)

    # Filtro por búsqueda (nombre o descripción)
    search = request.GET.get('search')
    if search:
        productos = productos.filter(
            nombre_producto__icontains=search
        ) | productos.filter(
            descripcion__icontains=search
        )
    if marca_id:
        productos = productos.filter(id_marca=marca_id)

    return render(request, 'admin/productos/productos.html', {
        'productos': productos,
        'marcas': marcas,
    })

def producto_detalle(request, id):
    producto = Producto.objects.get(id_producto=id)
    return render(request, 'admin/productos/producto_detalle.html', {'producto': producto})

def editar_producto(request, id):
    producto = Producto.objects.get(id_producto=id)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, "¡Producto modificado exitosamente!")
            return redirect('editar_producto', id=producto.id_producto)
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'admin/productos/editar_producto.html', {'form': form, 'producto': producto})

@require_POST
def eliminar_producto(request, id):
    producto = get_object_or_404(Producto, id_producto=id)
    producto.delete()
    messages.success(request, "¡Producto eliminado exitosamente!")
    return redirect('productos')


def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                form.save()
                return redirect('productos')
            except IntegrityError:
                form.add_error(None, "Ya existe un producto con ese identificador o valor único.")
    else:
        form = ProductoForm()
    return render(request, 'admin/productos/crear_producto.html', {'form': form})

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
@login_required
def perfil(request):
    usuario = Usuario.objects.filter(correo=request.user.email).first()
    return render(request, 'admin/perfil/perfil.html', {
        'user': request.user,
        'usuario_extra': usuario,
    })

def perfil_cliente(request):
    usuario = Usuario.objects.filter(correo=request.user.email).first()
    return render(request, 'client/perfil_cliente.html', {
        'user': request.user,
        'usuario_extra': usuario,
    })

def editar_perfil(request):
    # Vista para editar el perfil del usuario
    return render(request, 'perfil/editar_perfil.html', {})

def editar_perfil_cliente(request):
    usuario = Usuario.objects.get(correo=request.user.email)
    if request.method == 'POST':
        form = EditarPerfilClienteForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, "¡Perfil actualizado correctamente!")
            return redirect('editar_perfil_cliente')
        else:
            messages.error(request, "Hubo un error al actualizar el perfil. Revisa los campos.")
    else:
        form = EditarPerfilClienteForm(instance=usuario)
    return render(request, 'client/editar_perfil_cliente.html', {'form': form, 'usuario_extra': usuario})

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
