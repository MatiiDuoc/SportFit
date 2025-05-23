from .models import Carrito, DetalleCarrito, Usuario

def carrito_context(request):
    if request.user.is_authenticated:
        usuario = Usuario.objects.filter(correo=request.user.email).first()
        if usuario:
            carrito = Carrito.objects.filter(id_usuario=usuario, estado='activo').first()
            productos = []
            cantidad = 0
            total = 0
            if carrito:
                detalles = DetalleCarrito.objects.filter(id_carrito=carrito)
                for detalle in detalles:
                    producto = detalle.id_producto
                    img = producto.imagen
                    if hasattr(img, 'url'):
                        img_url = img.url
                    else:
                        img_url = img if img else ''
                    subtotal = detalle.precio * detalle.cantidad
                    productos.append({
                        'id_detalle_carrito': detalle.id_detalle_carrito,  # <-- agrega esta línea
                        'nombre': producto.nombre_producto,
                        'imagen': img_url,
                        'cantidad': detalle.cantidad,
                        'precio': detalle.precio,
                        'subtotal': detalle.precio * detalle.cantidad,
                    })
                    cantidad += detalle.cantidad
                    total += subtotal
            return {
                'carrito_cantidad': cantidad,
                'carrito_productos': productos,
                'carrito_total': total,
            }
    return {'carrito_cantidad': 0, 'carrito_productos': [], 'carrito_total': 0}