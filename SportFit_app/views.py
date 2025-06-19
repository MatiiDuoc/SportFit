from django.db import IntegrityError
from django.db import transaction
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
from dotenv import load_dotenv
import os
from rest_framework import serializers
from rest_framework import viewsets, permissions
from .serializers import PedidoSerializer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models.functions import TruncMonth
from django.db.models import Sum
from django.utils import timezone

load_dotenv()
# Forms

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = '__all__'
        labels = {
            'id_categoria': 'Categoría',
            'id_marca': 'Marca',
        }

class UsuarioForm(forms.ModelForm):
    contrasena = forms.CharField(widget=forms.PasswordInput, required=True)
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
        
class RutinaForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = [
            'nombre',
            'apellido',
            'telefono',
            'direccion',
            'tel_emergencia'
        ]

class CompletarPerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['correo','rut', 'nombre', 'apellido', 'telefono', 'direccion', 'tel_emergencia', 'id_comuna', 'id_genero']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['correo'].disabled = True

class PlanEntrenamientoForm(forms.ModelForm):
    class Meta:
        model = PlanEntrenamiento
        exclude = ['id_entrenador']

class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer
    permission_classes = []
    # Puedes filtrar solo los pedidos con despacho a domicilio
    def get_queryset(self):
        queryset = super().get_queryset()
        tipo_entrega = self.request.query_params.get('tipo_entrega')
        if tipo_entrega:
            queryset = queryset.filter(tipo_entrega=tipo_entrega)
        return queryset

class ContratarPlanForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['id_plan', 'id_entrenador']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo mostrar usuarios que sean entrenadores
        self.fields['id_entrenador'].queryset = Usuario.objects.filter(tipo_usuario='entrenador')
            
# forms.py
class EditarPerfilEntrenadorForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nombre', 'apellido', 'correo', 'telefono', 'direccion', 'id_comuna', 'id_genero']
        
class EditarPerfilClienteForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nombre', 'apellido', 'correo', 'telefono', 'direccion', 'id_comuna', 'id_genero']
        
class ComentarioPlanForm(forms.ModelForm):
    class Meta:
        model = ComentarioPlan
        fields = ['comentario']
        widgets = {
            'comentario': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Escribe tu reseña...'}),
        }

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def about(request):
    # Vista para la página "Acerca de"
    return render(request, 'about.html')
#----------------------------------
# Cliente
#----------------------------------
@login_required
def pedidos_cliente(request):
    usuario = Usuario.objects.filter(correo=request.user.email).first()
    pedidos_list = Pedido.objects.filter(usuario=usuario).order_by('-fecha_creacion')
    paginator = Paginator(pedidos_list, 10)  
    page_number = request.GET.get('page')
    pedidos = paginator.get_page(page_number)
    return render(request, 'client/pedidos.html', {'pedidos': pedidos})

def home(request):
    productos_comentados = Pedido.objects.exclude(observacion__isnull=True).exclude(observacion__exact='').order_by('-fecha_creacion')
    return render(request, 'home.html', {
        'productos_comentados': productos_comentados,
    })
    
@login_required
def historial_compras(request):
    usuario = Usuario.objects.filter(correo=request.user.email).first()
    if not usuario:
        messages.error(request, "Tu cuenta no está completamente registrada. Contacta al administrador.")
        return redirect('home')

    compras = Pedido.objects.filter(
        usuario=usuario,
        estado__in=['entregado', 'cancelado']
    ).order_by('-fecha_creacion')

    compras_con_productos = []
    for compra in compras:
        detalles = DetalleCarrito.objects.filter(id_carrito=compra.carrito).select_related('id_producto')
        detalles_con_comentario = []
        for detalle in detalles:
            comentario_usuario = ComentarioProdAten.objects.filter(
                id_producto=detalle.id_producto,
                id_usuario=usuario
            ).first()
            detalles_con_comentario.append({
                'detalle': detalle,
                'comentario_usuario': comentario_usuario
            })
        compras_con_productos.append({
            'compra': compra,
            'detalles': detalles_con_comentario,
        })

    return render(request, 'client/historial_compras.html', {'compras_con_productos': compras_con_productos})

@login_required
def detalle_compra(request, compra_id):
    usuario = Usuario.objects.filter(correo=request.user.email).first()
    if not usuario:
        messages.error(request, "Tu cuenta no está completamente registrada. Contacta al administrador.")
        return redirect('home')
    compra = get_object_or_404(Pedido, id_pedido=compra_id, usuario=usuario)
    return render(request, 'client/detalle_compra.html', {'compra': compra})

@login_required
def envios(request):
    usuario = Usuario.objects.filter(correo=request.user.email).first()
    if not usuario:
        messages.error(request, "Tu cuenta no está completamente registrada. Contacta al administrador.")
        return redirect('home')
    pedidos_enviados = Pedido.objects.filter(
        usuario=usuario,
        estado='enviado'
    ).order_by('-fecha_creacion')
    return render(request, 'client/envios.html', {'pedidos': pedidos_enviados})

@login_required
def carrito(request):
    usuario = Usuario.objects.filter(correo=request.user.email).first()
    if not usuario:
        messages.error(request, "Tu cuenta no está completamente registrada. Contacta al administrador.")
        return redirect('home')
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
                'id_detalle_carrito': detalle.id_detalle_carrito,
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
        usuario = Usuario.objects.filter(correo=request.user.email).first()
        producto = get_object_or_404(Producto, pk=producto_id)
        carrito = Carrito.objects.filter(id_usuario=usuario, estado='activo').first()
        if not carrito:
            carrito = Carrito.objects.create(id_usuario=usuario, estado='activo')

        detalle = DetalleCarrito.objects.filter(id_producto=producto, id_carrito=carrito).first()
        cantidad_actual = detalle.cantidad if detalle else 0
        cantidad_nueva = cantidad_actual + 1

        if cantidad_nueva > producto.stock:
            messages.error(request, f"No hay suficiente stock para {producto.nombre_producto}. Stock disponible: {producto.stock}")
            return redirect('productos_cliente')

        if detalle:
            detalle.cantidad += 1
            detalle.save()
        else:
            DetalleCarrito.objects.create(
                cantidad=1,
                precio=producto.precio,
                id_producto=producto,
                id_carrito=carrito
            )
        return redirect('productos_cliente')
    else:
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
def aumentar_cantidad_carrito(request, detalle_id):
    detalle = get_object_or_404(DetalleCarrito, pk=detalle_id)
    detalle.cantidad += 1
    detalle.save()
    return redirect('carrito')

@login_required
def actualizar_cantidad_carrito(request, detalle_id):
    detalle = get_object_or_404(DetalleCarrito, pk=detalle_id)
    producto = detalle.id_producto
    if request.method == 'POST':
        action = request.POST.get('action')
        cantidad_actual = detalle.cantidad
        if action == 'incrementar':
            if cantidad_actual < producto.stock:
                detalle.cantidad += 1
                detalle.save()
            else:
                messages.error(request, f"No hay suficiente stock para {producto.nombre_producto}. Stock disponible: {producto.stock}")
        elif action == 'decrementar':
            if cantidad_actual > 1:
                detalle.cantidad -= 1
                detalle.save()
        elif action == 'actualizar':
            try:
                nueva_cantidad = int(request.POST.get('cantidad', 1))
                if 1 <= nueva_cantidad <= producto.stock:
                    detalle.cantidad = nueva_cantidad
                    detalle.save()
                else:
                    messages.error(request, f"No hay suficiente stock para {producto.nombre_producto}. Stock disponible: {producto.stock}")
            except ValueError:
                messages.error(request, "Cantidad inválida.")
    return redirect('carrito')

@login_required
def direcciones(request):
    usuario = Usuario.objects.filter(correo=request.user.email).first()
    if not usuario:
        messages.error(request, "Tu cuenta no está completamente registrada. Contacta al administrador.")
        return redirect('home')
    return render(request, 'client/direcciones.html', {
        'direcciones': [usuario] if usuario.direccion else [],
        'usuario_extra': usuario,
    })
    

@login_required
def checkout_usuario(request):
    usuario = Usuario.objects.filter(correo=request.user.email).first()
    if not usuario or not usuario.rut or not usuario.nombre or not usuario.apellido or not usuario.telefono or not usuario.direccion:
        messages.info(request, "Debes completar tu perfil antes de comprar.")
        return redirect('completar_perfil')
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
    
@login_required
def checkout_entrega(request):
    usuario = Usuario.objects.filter(correo=request.user.email).first()
    if not usuario:
        messages.error(request, "Tu cuenta no está completamente registrada. Contacta al administrador.")
        return redirect('home')
    if request.method == 'POST':
        request.session['checkout_entrega'] = {
            'tipo_entrega': request.POST['tipo_entrega'],
            'direccion_entrega': request.POST.get('direccion_entrega', ''),
        }
        return redirect('checkout_pago')
    return render(request, 'client/checkout/entrega.html', {
        'usuario': usuario,
    })


@login_required
def checkout_pago(request):
    usuario = Usuario.objects.filter(correo=request.user.email).first()
    if not usuario:
        messages.error(request, "Tu cuenta no está completamente registrada. Contacta al administrador.")
        return redirect('home')
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
    if not usuario:
        messages.error(request, "Tu cuenta no está completamente registrada. Contacta al administrador.")
        return redirect('home')

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

    # --------- DESCUENTO SABORLATINO ---------
    descuento = 0
    DESCUENTO_SABORLATINO = 0.10  # 10%
    if usuario and es_usuario_saborlatino(usuario.rut):
        descuento = carrito_total * DESCUENTO_SABORLATINO
        carrito_total -= descuento
    # -----------------------------------------

    if request.method == 'POST':
        # Si el método de pago es PayPal, redirige al flujo de PayPal
        if pago.get('metodo_pago') == 'paypal':
            return redirect('iniciar_pago_paypal')

        # Validar stock antes de procesar la compra (solo para otros métodos)
        for detalle in detalles:
            producto = detalle.id_producto
            if producto.stock < detalle.cantidad:
                messages.error(request, f"No hay suficiente stock para {producto.nombre_producto}. Stock disponible: {producto.stock}")
                return redirect('carrito')

        # Descontar stock y guardar pedido de forma atómica
        with transaction.atomic():
            for detalle in detalles:
                producto = detalle.id_producto
                producto.stock -= detalle.cantidad
                producto.save()

            # Determina el estado según el tipo de entrega
            estado_pedido = 'procesando' if entrega.get('tipo_entrega') == 'envio' else 'entregado'

            pedido = Pedido.objects.create(
                usuario=usuario,
                carrito=carrito,
                direccion_entrega=entrega.get('direccion_entrega', ''),
                tipo_entrega=entrega.get('tipo_entrega', ''),
                metodo_pago=pago.get('metodo_pago', ''),
                total=carrito_total,
                estado=estado_pedido
            )

            # Copiar detalles del carrito a DetallePedido (historial)
            for detalle in detalles:
                DetallePedido.objects.create(
                    pedido=pedido,
                    producto=detalle.id_producto,
                    cantidad=detalle.cantidad,
                    precio=detalle.precio
                )

            # Crear la entrega asociada al pedido
            entrega_obj = Entrega.objects.create(
                direccion_entrega=entrega.get('direccion_entrega', ''),
                fecha_estimada=timezone.now().date(),
            )

            # Crear la venta asociada
            Venta.objects.create(
                fecha=timezone.now(),
                monto_total=carrito_total,
                estado='completada',
                id_carrito=carrito,
                descuento=descuento,
                id_entrega=entrega_obj,
            )

            detalles.delete()
            carrito.estado = 'finalizado'
            carrito.save()
        # Limpia la sesión después de crear el pedido
        request.session.pop('checkout_usuario', None)
        request.session.pop('checkout_entrega', None)
        request.session.pop('checkout_pago', None)
        # Redirige pasando el id del pedido
        return redirect('compra_exitosa', pedido_id=pedido.id_pedido)

    es_usuario_saborlatino_flag = usuario and es_usuario_saborlatino(usuario.rut)
    return render(request, 'client/checkout/confirmacion.html', {
        'usuario': usuario,
        'entrega': entrega,
        'pago': pago,
        'carrito_productos': carrito_productos,
        'carrito_cantidad': carrito_cantidad,
        'carrito_total': carrito_total,
        'descuento': descuento,
        'es_saborlatino': es_usuario_saborlatino_flag,
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
        usuario = Usuario.objects.filter(correo=request.user.email).first()
        entrega = request.session.get('checkout_entrega', {})
        pago = request.session.get('checkout_pago', {})
        carrito = Carrito.objects.filter(id_usuario=usuario, estado='activo').first()
        detalles = DetalleCarrito.objects.filter(id_carrito=carrito)
        carrito_total = sum(d.precio * d.cantidad for d in detalles)

        # Validar stock antes de crear el pedido
        for detalle in detalles:
            producto = detalle.id_producto
            if producto.stock < detalle.cantidad:
                messages.error(request, f"No hay suficiente stock para {producto.nombre_producto}. Stock disponible: {producto.stock}")
                return redirect('carrito')

        with transaction.atomic():
            for detalle in detalles:
                producto = detalle.id_producto
                producto.stock -= detalle.cantidad
                producto.save()

            estado_pedido = 'procesando' if entrega.get('tipo_entrega') == 'envio' else 'entregado'

            pedido = Pedido.objects.create(
                usuario=usuario,
                carrito=carrito,
                direccion_entrega=entrega.get('direccion_entrega', ''),
                tipo_entrega=entrega.get('tipo_entrega', ''),
                metodo_pago=pago.get('metodo_pago', ''),
                total=carrito_total,
                estado=estado_pedido
            )

            # Copiar detalles del carrito a DetallePedido
            for detalle in detalles:
                DetallePedido.objects.create(
                    pedido=pedido,
                    producto=detalle.id_producto,
                    cantidad=detalle.cantidad,
                    precio=detalle.precio
                )

            Venta.objects.create(
                fecha=timezone.now(),
                monto_total=carrito_total,
                estado='completada',
                id_carrito=carrito,
            )

            detalles.delete()
            carrito.estado = 'finalizado'
            carrito.save()
            request.session.pop('checkout_usuario', None)
            request.session.pop('checkout_entrega', None)
            request.session.pop('checkout_pago', None)
        return redirect('compra_exitosa', pedido_id=pedido.id_pedido)
    else:
        error_msg = response.get('status', 'Pago no autorizado')
        return render(request, 'webpay/error.html', {'error': error_msg})

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
            print("LINK:", link.href, link.method)
            if link.method == "REDIRECT":
                print("Redirigiendo a:", link.href)
                return redirect(link.href)
        print("No se encontró link de redirección en PayPal.")
    else:
        print("Error al crear el pago PayPal:", payment.error)
        return render(request, 'paypal/error.html', {'error': payment.error})
    
def paypal_retorno(request):
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')
    payment = paypalrestsdk.Payment.find(payment_id)
    if payment.execute({"payer_id": payer_id}):
        usuario = Usuario.objects.filter(correo=request.user.email).first()
        entrega = request.session.get('checkout_entrega', {})
        pago = request.session.get('checkout_pago', {})
        carrito = Carrito.objects.filter(id_usuario=usuario, estado='activo').first()
        detalles = DetalleCarrito.objects.filter(id_carrito=carrito)
        carrito_total = sum(d.precio * d.cantidad for d in detalles)

        # Verifica si ya existe un pedido para este carrito y usuario
        pedido_existente = Pedido.objects.filter(carrito=carrito, usuario=usuario, estado='entregado').first()
        if pedido_existente:
            request.session.pop('checkout_usuario', None)
            request.session.pop('checkout_entrega', None)
            request.session.pop('checkout_pago', None)
            return redirect('compra_exitosa', pedido_id=pedido_existente.id_pedido)

        # Validar stock antes de crear el pedido
        for detalle in detalles:
            producto = detalle.id_producto
            if producto.stock < detalle.cantidad:
                messages.error(request, f"No hay suficiente stock para {producto.nombre_producto}. Stock disponible: {producto.stock}")
                return redirect('carrito')

        with transaction.atomic():
            for detalle in detalles:
                producto = detalle.id_producto
                producto.stock -= detalle.cantidad
                producto.save()

            estado_pedido = 'procesando' if entrega.get('tipo_entrega') == 'envio' else 'entregado'

            pedido = Pedido.objects.create(
                usuario=usuario,
                carrito=carrito,
                direccion_entrega=entrega.get('direccion_entrega', ''),
                tipo_entrega=entrega.get('tipo_entrega', ''),
                metodo_pago=pago.get('metodo_pago', ''),
                total=carrito_total,
                estado=estado_pedido
            )

            # Copiar detalles del carrito a DetallePedido
            for detalle in detalles:
                DetallePedido.objects.create(
                    pedido=pedido,
                    producto=detalle.id_producto,
                    cantidad=detalle.cantidad,
                    precio=detalle.precio
                )

            entrega_obj = Entrega.objects.create(
                direccion_entrega=entrega.get('direccion_entrega', ''),
                fecha_estimada=timezone.now().date(),
            )

            Venta.objects.create(
                fecha=timezone.now(),
                monto_total=carrito_total,
                estado='completada',
                id_carrito=carrito,
                id_entrega=entrega_obj,
            )

            detalles.delete()
            carrito.estado = 'finalizado'
            carrito.save()
            request.session.pop('checkout_usuario', None)
            request.session.pop('checkout_entrega', None)
            request.session.pop('checkout_pago', None)
        return redirect('compra_exitosa', pedido_id=pedido.id_pedido)
    else:
        error_msg = payment.error.get('message', 'No se pudo procesar el pago. Intenta nuevamente.')
        return render(request, 'paypal/error.html', {'error': error_msg})
    
@login_required
def completar_perfil(request):
    usuario = Usuario.objects.filter(correo=request.user.email).first()
    if request.method == 'POST':
        form = CompletarPerfilForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, "¡Perfil completado!")
            return redirect('home')
    else:
        form = CompletarPerfilForm(instance=usuario)
    return render(request, 'client/completar_perfil.html', {'form': form})   
    
@login_required
def agregar_observacion(request, compra_id):
    if request.method == 'POST':
        usuario = Usuario.objects.filter(correo=request.user.email).first()
        if not usuario:
            messages.error(request, "Tu cuenta no está completamente registrada. Contacta al administrador.")
            return redirect('historial_compras')
        compra = get_object_or_404(Pedido, id_pedido=compra_id, usuario=usuario)
        observacion = request.POST.get('observacion', '').strip()
        if observacion:
            compra.observacion = observacion
            compra.save()
            messages.success(request, "¡Comentario guardado!")
        else:
            messages.error(request, "El comentario no puede estar vacío.")
    return redirect('historial_compras')

@login_required
def agregar_comentario_producto(request, producto_id):
    if request.method == 'POST':
        usuario = Usuario.objects.filter(correo=request.user.email).first()
        if not usuario:
            messages.error(request, "Tu cuenta no está completamente registrada. Contacta al administrador.")
            return redirect('detalle_producto', producto_id=producto_id)
        producto = get_object_or_404(Producto, pk=producto_id)
        comentario = request.POST.get('comentario', '').strip()
        if comentario:
            ComentarioProdAten.objects.create(
                id_producto=producto,
                id_usuario=usuario,
                comentario=comentario
            )
            messages.success(request, "¡Comentario guardado!")
        else:
            messages.error(request, "El comentario no puede estar vacío.")
        return redirect('detalle_producto', producto_id=producto_id)

@login_required
def detalle_pedido(request, pedido_id):
    usuario = Usuario.objects.get(correo=request.user.email)
    pedido = get_object_or_404(Pedido, id_pedido=pedido_id, usuario=usuario)
    return render(request, 'client/detalle_pedido.html', {'pedido': pedido})

def paypal_cancelado(request):
    return render(request, 'paypal/cancelado.html')

@login_required
def compra_exitosa(request, pedido_id):
    usuario = Usuario.objects.filter(correo=request.user.email).first()
    pedido = get_object_or_404(Pedido, id_pedido=pedido_id, usuario=usuario)
    if pedido.estado not in ['entregado', 'procesando']:
        return redirect('home')
    return render(request, 'client/checkout/compra_exitosa.html', {'pedido': pedido})


@login_required
def pedidos(request):
    usuario = Usuario.objects.filter(correo=request.user.email).first()
    pedidos_list = Pedido.objects.filter(usuario=usuario).order_by('-fecha_creacion')
    paginator = Paginator(pedidos_list, 5)  
    page_number = request.GET.get('page')
    pedidos = paginator.get_page(page_number)
    return render(request, 'client/pedidos.html', {'pedidos': pedidos})
# -------------------- Login --------------------
def logout_view(request):
    # Vista para cerrar sesión
    logout(request)
    return redirect('home')

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
        correo = request.POST.get('email')
        contrasena = request.POST.get('password')

        user = authenticate(request, username=correo, password=contrasena)
        if user is not None:
            login(request, user)
            usuario_extra = Usuario.objects.filter(correo=user.email).first()
            if not usuario_extra:
                messages.error(request, "Tu cuenta no está completamente registrada. Contacta al administrador.")
                return redirect('home')
            if user.is_superuser or usuario_extra.tipo_usuario == 'administrador':
                return redirect('dashboard_administrador')
            elif usuario_extra.tipo_usuario == 'entrenador':
                return redirect('dashboard_entrenador')
            elif usuario_extra.tipo_usuario == 'vendedor':
                return redirect('dashboard_vendedor')
            elif usuario_extra.tipo_usuario == 'cliente':
                return redirect('home')
            return redirect('home')
        else:
            messages.error(request, "Correo o contraseña incorrectos.")
            return render(request, 'login/login.html', {'error': 'Credenciales inválidas'})
    return render(request, 'login/login.html')

# def recuperar_contrasena(request):
#     # Vista para recuperar la contraseña
#     return render(request, 'recuperar_contrasena/recuperar_contrasena.html')

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

    # PAGINACIÓN
    paginator = Paginator(productos, 5)  # 12 productos por página (ajusta a tu gusto)
    page_number = request.GET.get('page')
    productos_page = paginator.get_page(page_number)

    return render(request, 'client/productos.html', {
        'productos': productos_page,
        'marcas': marcas,
    })
@login_required
def contratar_plan(request):
    usuario = Usuario.objects.filter(correo=request.user.email).first()
    if not usuario or usuario.tipo_usuario != 'cliente':
        messages.error(request, "Acceso no autorizado.")
        return redirect('home')

    tiene_plan = usuario.id_plan is not None
    comentario_existente = None
    comentario_form = None

    if tiene_plan:
        # Buscar si ya existe un comentario para este usuario y plan
        comentario_existente = ComentarioPlan.objects.filter(usuario=usuario, plan=usuario.id_plan).first()
        if request.method == 'POST':
            # Si ya existe, edítalo; si no, créalo
            if comentario_existente:
                comentario_form = ComentarioPlanForm(request.POST, instance=comentario_existente)
            else:
                comentario_form = ComentarioPlanForm(request.POST)
            if comentario_form.is_valid():
                comentario = comentario_form.save(commit=False)
                comentario.usuario = usuario
                comentario.plan = usuario.id_plan
                comentario.save()
                messages.success(request, "¡Comentario guardado!")
                return redirect('mis_planes')
        else:
            comentario_form = ComentarioPlanForm(instance=comentario_existente) if comentario_existente else ComentarioPlanForm()
        return render(request, 'client/plan.html', {
            'tiene_plan': True,
            'form': None,
            'usuario_extra': usuario,
            'comentario_form': comentario_form,
            'comentario_plan': comentario_existente,
        })

    if request.method == 'POST':
        form = ContratarPlanForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, "¡Plan contratado correctamente!")
            return redirect('mis_planes')
    else:
        form = ContratarPlanForm(instance=usuario)

    return render(request, 'client/plan.html', {
        'tiene_plan': False,
        'form': form,
        'usuario_extra': usuario,
    })
#----------------------------------
# Administrador
#----------------------------------

@login_required
def dashboard_administrador(request):
    usuario = Usuario.objects.filter(correo=request.user.email).first()
    if not usuario or usuario.tipo_usuario != 'administrador':
        messages.error(request, "Acceso no autorizado.")
        return redirect('home')

    # Ventas totales (suma de total de pedidos entregados)
    ventas_totales = Pedido.objects.filter(estado='entregado').aggregate(total=Sum('total'))['total'] or 0
    # Usuarios activos (puedes definirlo como usuarios con pedidos, o simplemente todos)
    usuarios_activos = Usuario.objects.count()
    # Órdenes pendientes (estado pendiente)
    ordenes_pendientes = Pedido.objects.filter(estado__in=['procesando', 'pendiente']).count()
    # Productos en stock (suma de stock de todos los productos)
    productos_en_stock = Producto.objects.aggregate(total=Sum('stock'))['total'] or 0
    fecha_actual = timezone.now().strftime('%Y-%m-%d')
    # Agrupa ventas por mes y suma el total
    ventas_por_mes = (
        Pedido.objects
        .filter(estado='entregado')
        .annotate(mes=TruncMonth('fecha_creacion'))
        .values('mes')
        .annotate(total=Sum('total'))
        .order_by('mes')
    )

    # Prepara los datos para el gráfico
    labels = [v['mes'].strftime('%b %Y') for v in ventas_por_mes]
    data = [v['total'] for v in ventas_por_mes]

    return render(request, 'admin/dashboard/dashboard.html', {
        'labels': labels,
        'data': data,
        'fecha_actual': fecha_actual,
        'ventas_totales': ventas_totales,
        'usuarios_activos': usuarios_activos,
        'ordenes_pendientes': ordenes_pendientes,
        'productos_en_stock': productos_en_stock,
        'usuario_extra': usuario,  # Opcional, si lo necesitas en el template
    })
# -------------------- reportes --------------------
@login_required
def reportes(request):
    # Obtener todas las ventas
    ventas = Venta.objects.all()
    # Sumar el total de ventas
    total_ventas = ventas.aggregate(total=Sum('monto_total'))['total'] or 0
    # Sumar la cantidad de productos vendidos
    total_productos = sum(
        sum(detalle.cantidad for detalle in venta.carrito.detallecarrito_set.all())
        for venta in ventas
    )
    # Pasar los resultados al contexto
    context = {
        'ventas': ventas,  # <-- para mostrar en la tabla
        'total_ventas': total_ventas,
        'total_productos': total_productos,
    }
    return render(request, 'admin/reportes/reporte.html', context)

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

def es_usuario_saborlatino(rut_usuario):
    # Llama a la API y obtén la lista de usuarios SaborLatino
    usuarios_api = obtener_usuarios_api()  # Esta función ya la tienes
    ruts_saborlatino = {u['numero_rut'] for u in usuarios_api}
    return rut_usuario in ruts_saborlatino

@login_required
def usuarios(request):
    try:
        usuarios_api = obtener_usuarios_api()
    except Exception as e:
        print("ERROR:", e)
        usuarios_api = []

    # Admins del modelo personalizado
    admins = Usuario.objects.filter(tipo_usuario='administrador')
    # Primer superusuario del modelo auth_user
    primer_admin = User.objects.filter(is_superuser=True).order_by('date_joined').first()
    usuarios_locales = Usuario.objects.all()
    paginator = Paginator(usuarios_locales, 10)  # 10 por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'usuarios_api': usuarios_api,
        'usuarios_locales': page_obj,  # paginados
        'primer_admin': primer_admin,  # <-- lo agregas al contexto
    }
    return render(request, 'admin/usuario/usuarios.html', context)

def usuario_detalle(request, id):
    usuario = get_object_or_404(Usuario, pk=id)
    return render(request, 'admin/usuario/usuario_detalle.html', {'usuario': usuario})

@login_required
def editar_usuario(request, id):
    usuario = get_object_or_404(Usuario, pk=id)
    campos_ocultos = ['tipo_usuario', 'contrasena', 'id_entrenador', 'rut', 'id_plan']
    if request.method == 'POST':
        form = UsuarioForm(request.POST, request.FILES, instance=usuario)
        if usuario.tipo_usuario == 'entrenador':
            for field in campos_ocultos:
                form.fields.pop(field, None)
        else:
            form.fields.pop('contrasena', None)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario editado correctamente.")
            return redirect('usuarios')
    else:
        form = UsuarioForm(instance=usuario)
        if usuario.tipo_usuario == 'entrenador':
            for field in campos_ocultos:
                form.fields.pop(field, None)
        else:
            form.fields.pop('contrasena', None)
    return render(request, 'admin/usuario/editar_usuario.html', {'form': form, 'usuario': usuario})

@require_POST
@login_required
def eliminar_usuario(request, id):
    usuario = get_object_or_404(Usuario, pk=id)
    # Elimina también el usuario de auth_user si existe
    user = User.objects.filter(username=usuario.correo).first()
    usuario.delete()
    if user:
        user.delete()
    return redirect('usuarios')

@login_required
def crear_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            correo = form.cleaned_data.get('correo')
            nombre = form.cleaned_data.get('nombre')
            apellido = form.cleaned_data.get('apellido')
            contrasena = form.cleaned_data.get('contrasena')

            # Crea el usuario en auth_user si no existe
            if not User.objects.filter(username=correo).exists():
                user = User.objects.create_user(
                    username=correo,
                    email=correo,
                    password=contrasena,
                    first_name=nombre,
                    last_name=apellido
                )
            else:
                user = User.objects.get(username=correo)

            # Guarda el usuario en el modelo Usuario
            usuario = form.save(commit=False)
            usuario.contrasena = contrasena  # Opcional, si quieres guardar la contraseña en tu modelo (no recomendado)
            usuario.save()
            return redirect('usuarios')
    else:
        form = UsuarioForm()
    return render(request, 'admin/usuario/crear_usuario.html', {'form': form})

# -------------------- Ventas --------------------
@login_required
def ventas(request):
    pedidos = Pedido.objects.all().order_by('-fecha_creacion')
    clientes = Usuario.objects.filter(pedido__isnull=False).distinct()

    # Filtros
    client = request.GET.get('client')
    order_date = request.GET.get('order_date')
    status = request.GET.get('status')
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    sale_date = request.GET.get('sale_date')

    if client:
        nombre, apellido = client.split(' ', 1)
        pedidos = pedidos.filter(usuario__nombre=nombre, usuario__apellido=apellido)
    if order_date:
        pedidos = pedidos.filter(fecha_creacion__date=order_date)
    if sale_date:
        pedidos = pedidos.filter(fecha_creacion__date=sale_date)
    if status:
        pedidos = pedidos.filter(estado=status)
    if price_min:
        pedidos = pedidos.filter(total__gte=price_min)
    if price_max:
        pedidos = pedidos.filter(total__lte=price_max)

    estados = Pedido.ESTADO_CHOICES if hasattr(Pedido, 'ESTADO_CHOICES') else []

    return render(request, 'admin/venta/ventas.html', {
        'pedidos': pedidos,
        'clientes': clientes,
        'estados': estados,
    })

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
        print("Datos recibidos:", form.data)
        if form.is_valid():
            try:
                form.save()
                return redirect('productos')
            except IntegrityError as e:
                print("Error de integridad:", e)
                form.add_error(None, "Ya existe un producto con ese identificador o valor único.")
    else:
        form = ProductoForm()
    return render(request, 'admin/productos/crear_producto.html', {'form': form})

# -------------------- Marcas --------------------
@login_required
def marcas(request):
    if not request.user.is_superuser:
        messages.error(request, "Acceso no autorizado.")
        return redirect('home')
    marcas = Marca.objects.all()
    return render(request, 'admin/marcas/marcas.html', {'marcas': marcas})

def marca_detalle(request):
    # Vista para mostrar detalles de una marca
    return render(request, 'marcas/marca_detalle.html', {})

def editar_marca(request):
    # Vista para editar una marca
    return render(request, 'marcas/editar_marca.html', {})

def eliminar_marca(request):
    # Vista para eliminar una marca
    return render(request, 'marcas/eliminar_marca.html', {})

@csrf_exempt
@login_required
def crear_marca_ajax(request):
    if request.method == 'POST':
        descripcion = request.POST.get('brand_description', '').strip()
        if not descripcion:
            return JsonResponse({'success': False, 'error': 'La descripción es obligatoria.'})
        # Validar existencia ignorando mayúsculas/minúsculas y espacios
        existe = Marca.objects.filter(descripcion__iexact=descripcion).exists()
        if existe:
            return JsonResponse({'success': False, 'error': 'Ya existe una marca con esa descripción.'})
        try:
            Marca.objects.create(descripcion=descripcion)
            return JsonResponse({'success': True})
        except IntegrityError:
            return JsonResponse({'success': False, 'error': 'Ya existe una marca con esa descripción.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Método no permitido.'})

@csrf_exempt
@login_required
def editar_marca_ajax(request, id):
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Acceso no autorizado.'})
    marca = get_object_or_404(Marca, id_marca=id)  # <-- aquí el cambio
    if request.method == 'POST':
        descripcion = request.POST.get('brand_description')
        if descripcion:
            marca.descripcion = descripcion
            marca.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Todos los campos son obligatorios.'})
    return JsonResponse({'success': False, 'error': 'Método no permitido.'})

@login_required
def eliminar_marca_ajax(request, id):
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Acceso no autorizado.'})
    marca = get_object_or_404(Marca, id_marca=id)  # <-- aquí el cambio
    if request.method == 'POST':
        marca.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Método no permitido.'})

# -------------------- Proveedores --------------------
def proveedores(request):
    proveedores = Proveedor.objects.all()
    return render(request, 'admin/proveedores/proveedores.html', {'proveedores': proveedores})

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
@csrf_exempt
def crear_proveedor_ajax(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre_proveedor')
        rut_proveedor = request.POST.get('rut_proveedor')
        direccion = request.POST.get('direccion')
        correo = request.POST.get('correo')
        telefono = request.POST.get('telefono')
        if nombre and direccion:
            Proveedor.objects.create(
                nombre_proveedor=nombre,
                rut_proveedor=rut_proveedor,
                direccion=direccion,
                correo=correo,
                telefono=telefono
            )
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Todos los campos obligatorios.'})
    return JsonResponse({'success': False, 'error': 'Método no permitido.'})

@csrf_exempt
def editar_proveedor_ajax(request, id):
    proveedor = Proveedor.objects.filter(pk=id).first()
    if not proveedor:
        return JsonResponse({'success': False, 'error': 'Proveedor no encontrado.'})
    if request.method == 'POST':
        proveedor.nombre_proveedor = request.POST.get('nombre_proveedor')
        proveedor.rut_proveedor = request.POST.get('rut_proveedor')
        proveedor.direccion = request.POST.get('direccion')
        proveedor.correo = request.POST.get('correo')
        proveedor.telefono = request.POST.get('telefono')
        proveedor.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Método no permitido.'})

@csrf_exempt
def eliminar_proveedor_ajax(request, id):
    proveedor = Proveedor.objects.filter(pk=id).first()
    if not proveedor:
        return JsonResponse({'success': False, 'error': 'Proveedor no encontrado.'})
    if request.method == 'POST':
        proveedor.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Método no permitido.'})

# -------------------- Órdenes --------------------
def ordenes(request):
    pedidos = Pedido.objects.select_related('usuario').prefetch_related('detallepedido_set', 'detallepedido_set__producto').order_by('-fecha_creacion')
    clientes = Usuario.objects.filter(pedido__isnull=False).distinct()
    client = request.GET.get('client')
    order_date = request.GET.get('order_date')
    status = request.GET.get('status')

    if client:
        nombre, apellido = client.split(' ', 1)
        pedidos = pedidos.filter(usuario__nombre=nombre, usuario__apellido=apellido)
    if order_date:
        pedidos = pedidos.filter(fecha_creacion__date=order_date)
    if status:
        pedidos = pedidos.filter(estado=status)

    # Cambio de estado desde el modal
    if request.method == 'POST':
        id_pedido = request.POST.get('pedido_id')
        nuevo_estado = request.POST.get('estado')
        pedido = Pedido.objects.filter(pk=id_pedido).first()
        if pedido and nuevo_estado in dict(Pedido.ESTADO_CHOICES):
            pedido.estado = nuevo_estado
            pedido.save()
        return redirect('ordenes')

    estados = Pedido.ESTADO_CHOICES
    return render(request, 'admin/ordenes/ordenes.html', {
        'pedidos': pedidos,
        'estados': estados,
        'clientes': clientes,
    })

def admin_detalle_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    detalles = pedido.carrito.detallecarrito_set.select_related('id_producto').all()
    return render(request, 'admin/ordenes/detalle_pedido_modal.html', {
        'pedido': pedido,
        'detalles': detalles,
    })

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
    if not usuario:
        messages.error(request, "Tu cuenta no está completamente registrada. Contacta al administrador.")
        return redirect('home')
    return render(request, 'admin/perfil/perfil.html', {
        'user': request.user,
        'usuario_extra': usuario,
    })

def perfil_cliente(request):
    usuario = Usuario.objects.filter(correo=request.user.email).first()
    if not usuario:
        messages.error(request, "Tu cuenta no está completamente registrada. Contacta al administrador.")
        return redirect('home')
    return render(request, 'client/perfil_cliente.html', {
        'user': request.user,
        'usuario_extra': usuario,
    })

def editar_perfil(request):
    # Vista para editar el perfil del usuario
    return render(request, 'perfil/editar_perfil.html', {})


@login_required
def editar_perfil_cliente(request):
    usuario = Usuario.objects.filter(correo=request.user.email).first()
    if not usuario:
        messages.error(request, "No se encontró el usuario.")
        return redirect('home')
    if request.method == 'POST':
        form = EditarPerfilClienteForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            # Sincronizar con auth.User
            user = User.objects.filter(email=usuario.correo).first()
            if user:
                user.first_name = usuario.nombre
                user.last_name = usuario.apellido
                user.email = usuario.correo
                user.username = usuario.correo  # si usas el correo como username
                user.save()
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

# -------------------- Entrenadores --------------------
@login_required
def dashboard_entrenador(request):
    entrenador = Usuario.objects.get(correo=request.user.email)
    clientes_asignados = Usuario.objects.filter(id_entrenador=entrenador).count()
    planes_creados = PlanEntrenamiento.objects.filter(id_entrenador=entrenador).count()
    return render(request, 'entrenador/dashboard/dashboard.html', {
        'clientes_asignados': clientes_asignados,
        'plan_entrenamiento': planes_creados,
    })

@login_required
def clientes_entrenador(request):
    usuario = Usuario.objects.filter(correo=request.user.email).first()
    if not usuario or usuario.tipo_usuario != 'entrenador':
        messages.error(request, "Acceso no autorizado.")
        return redirect('home')

    # Mostrar solo los clientes asignados a este entrenador
    clientes = Usuario.objects.filter(tipo_usuario='cliente', id_entrenador=usuario)
    return render(request, 'entrenador/alumnos/alumnos_rutinas.html', {'clientes': clientes})

@login_required
def cliente_detalle_entrenador(request, cliente_id):
    # Vista para mostrar detalles de un cliente del entrenador
    usuario = Usuario.objects.filter(correo=request.user.email).first()
    if not usuario or usuario.tipo_usuario != 'entrenador':
        messages.error(request, "Acceso no autorizado.")
        return redirect('home')

    cliente = get_object_or_404(Usuario, id_usuario=cliente_id, id_entrenador=usuario)
    return render(request, 'entrenador/clientes/cliente_detalle.html', {
        'cliente': cliente,
        'entrenador': usuario,  # Opcional, si lo necesitas en el template
    })

@login_required
def seguimiento_pedido(request, pedido_id):
    usuario = Usuario.objects.filter(correo=request.user.email).first()
    if not usuario:
        messages.error(request, "Tu cuenta no está completamente registrada. Contacta al administrador.")
        return redirect('home')
    pedido = get_object_or_404(Pedido, id_pedido=pedido_id, usuario=usuario)
    entrega = Entrega.objects.filter(id_entrega=pedido.venta.id_entrega_id).first() if pedido.venta and pedido.venta.id_entrega_id else None
    seguimientos = SeguimientoEntrega.objects.filter(id_entrega=entrega).order_by('-fecha_actualizacion') if entrega else []
    estados = ["Procesando", "Enviado", "En reparto", "Entregado"]
    # Prepara una lista de los estados alcanzados
    estados_alcanzados = list(seguimientos.values_list('estado_envio', flat=True)) if seguimientos else []
    return render(request, 'client/seguimiento_pedido.html', {
        'pedido': pedido,
        'entrega': entrega,
        'seguimientos': seguimientos,
        'estados': estados,
        'estados_alcanzados': estados_alcanzados,
    })

@login_required
def crear_rutina(request):
    usuario = Usuario.objects.filter(correo=request.user.email).first()
    if not usuario or usuario.tipo_usuario != 'entrenador':
        messages.error(request, "Acceso no autorizado.")
        return redirect('home')

    if request.method == 'POST':
        form = PlanEntrenamientoForm(request.POST)
        if form.is_valid():
            rutina = form.save(commit=False)
            rutina.id_entrenador = usuario
            rutina.save()
            messages.success(request, "Rutina creada exitosamente.")
            return redirect('rutinas_entrenador')
        else:
            print("Errores del formulario:", form.errors)
            messages.error(request, "Corrige los errores del formulario.")
    else:
        form = PlanEntrenamientoForm()

    return render(request, 'entrenador/rutinas/crear_rutina.html', {
        'form': form,
        'entrenador': usuario,  # Opcional, si lo necesitas en el template
    })

@login_required
def rutinas_entrenador(request):
    usuario = Usuario.objects.filter(correo=request.user.email).first()
    if not usuario or usuario.tipo_usuario != 'entrenador':
        messages.error(request, "Acceso no autorizado.")
        return redirect('home')

    # Mostrar solo los planes creados por este entrenador
    rutinas = PlanEntrenamiento.objects.filter(id_entrenador=usuario)
    form = PlanEntrenamientoForm()

    return render(request, 'entrenador/rutinas/rutinas.html', {
        'rutinas': rutinas,
        'form': form,
        'entrenador': usuario,  # Opcional, si lo necesitas en el template
    })

@login_required
def rutina_detalle_entrenador(request, rutina_id):
    usuario = Usuario.objects.filter(correo=request.user.email).first()
    if not usuario or usuario.tipo_usuario != 'entrenador':
        messages.error(request, "Acceso no autorizado.")
        return redirect('home')

    rutina = get_object_or_404(PlanEntrenamiento, id_plan=rutina_id, id_entrenador=usuario)
    return render(request, 'entrenador/rutinas/rutina_detalle.html', {
        'rutina': rutina,
        'entrenador': usuario,  # Opcional, si lo necesitas en el template
    })

@login_required
def editar_rutina(request, rutina_id):
    usuario = Usuario.objects.filter(correo=request.user.email).first()
    if not usuario or usuario.tipo_usuario != 'entrenador':
        messages.error(request, "Acceso no autorizado.")
        return redirect('home')

    rutina = get_object_or_404(PlanEntrenamiento, id_plan=rutina_id, id_entrenador=usuario)
    if request.method == 'POST':
        form = PlanEntrenamientoForm(request.POST, instance=rutina)
        if form.is_valid():
            form.save()
            messages.success(request, "Rutina actualizada exitosamente.")
            return redirect('rutinas_entrenador')
    else:
        form = PlanEntrenamientoForm(instance=rutina)

    return render(request, 'entrenador/rutinas/editar_rutina.html', {
        'form': form,
        'rutina': rutina,
        'entrenador': usuario,  # Opcional, si lo necesitas en el template
    })

@login_required
def eliminar_rutina(request, rutina_id):
    usuario = Usuario.objects.filter(correo=request.user.email).first()
    if not usuario or usuario.tipo_usuario != 'entrenador':
        messages.error(request, "Acceso no autorizado.")
        return redirect('home')

    rutina = get_object_or_404(PlanEntrenamiento, id_plan=rutina_id, id_entrenador=usuario)
    if request.method == 'POST':
        rutina.delete()
        messages.success(request, "Rutina eliminada exitosamente.")
        return redirect('rutinas_entrenador')

    # Muestra una página de confirmación antes de eliminar
    return render(request, 'entrenador/rutinas/eliminar_rutina.html', {
        'rutina': rutina,
        'entrenador': usuario,  # Opcional, si lo necesitas en el template
    })

def cliente_detalle_entrenador(request, cliente_id):
    usuario = Usuario.objects.filter(correo=request.user.email).first()
    if not usuario or usuario.tipo_usuario != 'entrenador':
        messages.error(request, "Acceso no autorizado.")
        return redirect('home')

    cliente = get_object_or_404(Usuario, id_usuario=cliente_id, entrenador=usuario)
    rutinas = EntrenadorPlan.objects.filter(id_entrenador=usuario, id_usuario=cliente)
    return render(request, 'entrenador/clientes/cliente_detalle.html', {
        'cliente': cliente,
        'rutinas': rutinas,
    })

@login_required
def asignar_rutina_entrenador(request, cliente_id):
    usuario = Usuario.objects.filter(correo=request.user.email).first()
    if not usuario or usuario.tipo_usuario != 'entrenador':
        messages.error(request, "Acceso no autorizado.")
        return redirect('home')

    cliente = get_object_or_404(Usuario, id_usuario=cliente_id, id_entrenador=usuario)
    if request.method == 'POST':
        rutina_id = request.POST.get('rutina')
        rutina = get_object_or_404(EntrenadorPlan, id_plan=rutina_id, id_entrenador=usuario)
        cliente.rutina_asignada = rutina
        cliente.save()
        messages.success(request, "Rutina asignada exitosamente.")
        return redirect('cliente_detalle_entrenador', cliente_id=cliente.id_usuario)

    rutinas = EntrenadorPlan.objects.filter(id_entrenador=usuario)
    return render(request, 'entrenador/clientes/asignar_rutina.html', {
        'cliente': cliente,
        'rutinas': rutinas,
    })


@login_required
def eliminar_rutina_cliente(request, cliente_id):
    usuario = Usuario.objects.filter(correo=request.user.email).first()
    if not usuario or usuario.tipo_usuario != 'entrenador':
        messages.error(request, "Acceso no autorizado.")
        return redirect('home')

    cliente = get_object_or_404(Usuario, id_usuario=cliente_id, id_entrenador=usuario)
    if request.method == 'POST':
        cliente.rutina_asignada = None
        cliente.save()
        messages.success(request, "Rutina eliminada exitosamente.")
        return redirect('cliente_detalle_entrenador', cliente_id=cliente.id_usuario)

    return render(request, 'entrenador/clientes/eliminar_rutina.html', {'cliente': cliente})

@login_required
def perfil_entrenador(request):
    entrenador = Usuario.objects.filter(correo=request.user.email, tipo_usuario='entrenador').first()
    if not entrenador:
        messages.error(request, "No se encontró el perfil del entrenador.")
        return redirect('home')
    return render(request, 'entrenador/perfil/perfil.html', {'entrenador': entrenador})

@login_required
def editar_perfil_entrenador(request):
    entrenador = Usuario.objects.filter(correo=request.user.email, tipo_usuario='entrenador').first()
    if not entrenador:
        messages.error(request, "Acceso no autorizado.")
        return redirect('home')

    if request.method == 'POST':
        form = EditarPerfilEntrenadorForm(request.POST, instance=entrenador)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect('perfil_entrenador')
        else:
            messages.error(request, "Corrige los errores del formulario.")
    else:
        form = EditarPerfilEntrenadorForm(instance=entrenador)

    return render(request, 'entrenador/perfil/editar_perfil.html', {
        'form': form,
        'entrenador': entrenador,
    })
    
@login_required
def editar_cliente_entrenador(request, id):
    usuario = Usuario.objects.filter(correo=request.user.email).first()
    if not usuario or usuario.tipo_usuario != 'entrenador':
        messages.error(request, "Acceso no autorizado.")
        return redirect('home')

    cliente = get_object_or_404(Usuario, id_usuario=id, id_entrenador=usuario)
    if request.method == 'POST':
        cliente.nombre = request.POST.get('nombre', cliente.nombre)
        cliente.apellido = request.POST.get('apellido', cliente.apellido)
        cliente.telefono = request.POST.get('telefono', cliente.telefono)
        cliente.direccion = request.POST.get('direccion', cliente.direccion)
        cliente.save()
        messages.success(request, "Cliente actualizado correctamente.")
        return redirect('cliente_detalle_entrenador', cliente_id=cliente.id_usuario)

    return render(request, 'entrenador/clientes/editar_cliente.html', {
        'cliente': cliente,
    })

@login_required
def eliminar_cliente_entrenador(request, id):
    usuario = Usuario.objects.filter(correo=request.user.email).first()
    if not usuario or usuario.tipo_usuario != 'entrenador':
        messages.error(request, "Acceso no autorizado.")
        return redirect('home')

    cliente = get_object_or_404(Usuario, id_usuario=id, id_entrenador=usuario)
    if request.method == 'POST':
        cliente.delete()
        messages.success(request, "Cliente eliminado correctamente.")
        return redirect('clientes_entrenador')

    return render(request, 'entrenador/clientes/eliminar_cliente.html', {'cliente': cliente})

def rutina_detalle_entrenador(request, id):
    usuario = Usuario.objects.filter(correo=request.user.email).first()
    if not usuario or usuario.tipo_usuario != 'entrenador':
        messages.error(request, "Acceso no autorizado.")
        return redirect('home')

    rutina = get_object_or_404(EntrenadorPlan, id_plan=id, entrenador=usuario)
    return render(request, 'entrenador/rutinas/rutina_detalle.html', {
        'rutina': rutina,
    })

def ver_alumno(request, id_usuario):
    usuario = Usuario.objects.filter(correo=request.user.email).first()
    if not usuario or usuario.tipo_usuario != 'entrenador':
        messages.error(request, "Acceso no autorizado.")
        return redirect('home')

    cliente = get_object_or_404(Usuario, id_usuario=id_usuario, id_entrenador=usuario)
    plan = None
    if cliente.id_plan and cliente.id_plan.id_entrenador == usuario:
        plan = cliente.id_plan

    return render(request, 'entrenador/alumnos/ver_alumno.html', {
        'cliente': cliente,
        'plan': plan,
    })

def editar_alumno(request, id_usuario):
    usuario = Usuario.objects.filter(correo=request.user.email).first()
    if not usuario or usuario.tipo_usuario != 'entrenador':
        messages.error(request, "Acceso no autorizado.")
        return redirect('home')

    cliente = get_object_or_404(Usuario, id_usuario=id_usuario, id_entrenador=usuario)
    planes = PlanEntrenamiento.objects.filter(id_entrenador=usuario)

    if request.method == 'POST':
        print("POST:", request.POST)
        cliente.telefono = request.POST.get('telefono', cliente.telefono)
        cliente.direccion = request.POST.get('direccion', cliente.direccion)
        id_plan = request.POST.get('id_plan')
        print("id_plan recibido:", id_plan)
        cliente.id_plan_id = int(id_plan) if id_plan else None
        cliente.save()
        messages.success(request, "Cliente actualizado correctamente.")
        return redirect('ver_alumno', id_usuario=cliente.id_usuario)

    return render(request, 'entrenador/alumnos/editar_alumno.html', {
        'alumno': cliente,
        'planes': planes,
    })

    
