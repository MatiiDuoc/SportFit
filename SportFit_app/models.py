from django.db import models

# --- Tablas base ---

class Region(models.Model):
    id_region = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=50)

    class Meta:
        db_table = 'region'

    def __str__(self):
        return self.descripcion

class Comuna(models.Model):
    id_comuna = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=50)
    id_region = models.ForeignKey(Region, on_delete=models.CASCADE, db_column='id_region')

    class Meta:
        db_table = 'comuna'

    def __str__(self):
        return self.descripcion

class Genero(models.Model):
    id_genero = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=50)

    class Meta:
        db_table = 'genero'

    def __str__(self):
        return self.descripcion

class PlanEntrenamiento(models.Model):
    id_plan = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=20)
    descripcion = models.CharField(max_length=50)
    duracion_semana = models.IntegerField()
    nivel = models.CharField(max_length=50)
    id_entrenador = models.ForeignKey('Usuario', on_delete=models.CASCADE, db_column='id_entrenador', limit_choices_to={'tipo_usuario': 'entrenador'}, null=True, blank=True)
    class Meta:
        db_table = 'plan_entrenamiento'

    def __str__(self):
        return self.nombre

class Categoria(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=50)

    class Meta:
        db_table = 'categoria'

    def __str__(self):
        return self.descripcion

class Marca(models.Model):
    id_marca = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=50)

    class Meta:
        db_table = 'marca'

    def __str__(self):
        return self.descripcion

# --- Usuario único para todos los tipos ---

class Usuario(models.Model):
    TIPO_USUARIO_CHOICES = [
        ('administrador', 'Administrador'),
        ('entrenador', 'Entrenador'),
        ('cliente', 'Cliente'),
        ('vendedor', 'Vendedor'),
        # agrega más si necesitas
    ]
    id_usuario = models.AutoField(primary_key=True)
    rut = models.CharField(max_length=12)
    nombre = models.CharField(max_length=20)
    apellido = models.CharField(max_length=20)
    correo = models.EmailField(max_length=30)
    telefono = models.CharField(max_length=15)
    tel_emergencia = models.CharField(max_length=15, blank=True, null=True)
    contrasena = models.CharField(max_length=128)
    direccion = models.CharField(max_length=50)
    id_comuna = models.ForeignKey(Comuna, on_delete=models.CASCADE, db_column='id_comuna')
    id_genero = models.ForeignKey(Genero, on_delete=models.CASCADE, db_column='id_genero')
    tipo_usuario = models.CharField(max_length=20, choices=TIPO_USUARIO_CHOICES, default='cliente')
    id_entrenador = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='clientes')
    id_plan = models.ForeignKey(PlanEntrenamiento, null=True, blank=True, on_delete=models.SET_NULL)
    # otros campos...

    class Meta:
        db_table = 'usuario'

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.tipo_usuario})"

# --- Relación Entrenador-Plan (solo para usuarios tipo entrenador) ---

class EntrenadorPlan(models.Model):
    id_entrenador = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        db_column='id_entrenador',
        limit_choices_to={'tipo_usuario': 'entrenador'}
    )
    id_plan = models.ForeignKey(PlanEntrenamiento, on_delete=models.CASCADE, db_column='id_plan')

    class Meta:
        db_table = 'entrenador_plan'
        unique_together = (('id_entrenador', 'id_plan'),)

# --- Productos y relaciones ---

class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True)
    nombre_producto = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=50)
    stock = models.IntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    id_categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, db_column='id_categoria')
    id_marca = models.ForeignKey(Marca, on_delete=models.CASCADE, db_column='id_marca')

    class Meta:
        db_table = 'producto'

    def __str__(self):
        return self.nombre_producto

class Proveedor(models.Model):
    id_proveedor = models.AutoField(primary_key=True)
    nombre_proveedor = models.CharField(max_length=20)
    rut_proveedor = models.CharField(max_length=12)
    telefono = models.CharField(max_length=15)
    correo = models.EmailField(max_length=30)
    direccion = models.CharField(max_length=50)

    class Meta:
        db_table = 'proveedor'

    def __str__(self):
        return self.nombre_proveedor

class ProveedorProducto(models.Model):
    id_proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, db_column='id_proveedor')
    id_producto = models.ForeignKey(Producto, on_delete=models.CASCADE, db_column='id_producto')

    class Meta:
        db_table = 'proveedor_producto'
        unique_together = (('id_proveedor', 'id_producto'),)

# --- Carrito y detalle ---

class DetalleCarrito(models.Model):
    id_detalle_carrito = models.AutoField(primary_key=True)
    cantidad = models.IntegerField()
    precio = models.IntegerField()
    id_producto = models.ForeignKey(Producto, on_delete=models.CASCADE, db_column='id_producto')
    id_carrito = models.ForeignKey('Carrito', on_delete=models.CASCADE, db_column='id_carrito')  

    class Meta:
        db_table = 'detalle_carrito'

class Carrito(models.Model):
    id_carrito = models.AutoField(primary_key=True)
    estado = models.CharField(max_length=20)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='id_usuario')
    class Meta:
        db_table = 'carrito'

class CarritoProducto(models.Model):
    id_carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, db_column='id_carrito')
    id_producto = models.ForeignKey(Producto, on_delete=models.CASCADE, db_column='id_producto')

    class Meta:
        db_table = 'carrito_producto'
        unique_together = (('id_carrito', 'id_producto'),)

# --- Planes y detalle ---

class DetallePlan(models.Model):
    id_detalle_plan = models.AutoField(primary_key=True)
    id_plan = models.ForeignKey(PlanEntrenamiento, on_delete=models.CASCADE, db_column='id_plan')
    id_categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, db_column='id_categoria')
    precio = models.IntegerField()

    class Meta:
        db_table = 'detalle_plan'

class DetalleProducto(models.Model):
    id_detalle_producto = models.AutoField(primary_key=True)
    id_producto = models.ForeignKey(Producto, on_delete=models.CASCADE, db_column='id_producto')
    id_categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, db_column='id_categoria')
    id_plan = models.ForeignKey(PlanEntrenamiento, on_delete=models.CASCADE, db_column='id_plan')
    precio = models.IntegerField()

    class Meta:
        db_table = 'detalle_producto'

# --- Comentarios, ventas, pagos, comprobantes, etc. ---

class ComentarioProdAten(models.Model):
    id_comentario = models.AutoField(primary_key=True)
    comentario = models.CharField(max_length=100)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='id_usuario')
    id_producto = models.ForeignKey(Producto, on_delete=models.CASCADE, db_column='id_producto')

    class Meta:
        db_table = 'comentario_prod_aten'

class Entrega(models.Model):
    id_entrega = models.AutoField(primary_key=True)
    direccion_entrega = models.CharField(max_length=50)
    fecha_estimada = models.DateField()

    class Meta:
        db_table = 'entrega'

class Venta(models.Model):
    id_venta = models.AutoField(primary_key=True)
    fecha = models.DateField()
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20)
    id_carrito = models.OneToOneField(Carrito, on_delete=models.CASCADE, db_column='id_carrito')
    descuento = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    id_entrega = models.OneToOneField(Entrega, on_delete=models.CASCADE, db_column='id_entrega')

    class Meta:
        db_table = 'venta'

class MetodoPago(models.Model):
    id_metodo_pago = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=50)
    id_venta = models.ForeignKey(Venta, on_delete=models.CASCADE, db_column='id_venta')

    class Meta:
        db_table = 'metodo_pago'

class Pago(models.Model):
    id_pago = models.AutoField(primary_key=True)
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, db_column='id_venta')
    metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.CASCADE, db_column='id_metodo_pago')
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_pago = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20)

    class Meta:
        db_table = 'pago'

    def __str__(self):
        return f"Pago {self.id_pago} - Venta {self.venta.id_venta}"

class Comprobante(models.Model):
    id_comprobante = models.AutoField(primary_key=True)
    formato = models.CharField(max_length=20)
    fecha_emision = models.DateField()
    id_venta = models.OneToOneField(Venta, on_delete=models.CASCADE, db_column='id_venta')

    class Meta:
        db_table = 'comprobante'

class Reserva(models.Model):
    id_reserva = models.AutoField(primary_key=True)
    fecha_reserva = models.DateField()
    estado = models.CharField(max_length=20)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='id_usuario')
    id_producto = models.ForeignKey(Producto, on_delete=models.CASCADE, db_column='id_producto')

    class Meta:
        db_table = 'reserva'

class SeguimientoEntrega(models.Model):
    id_seguimiento = models.AutoField(primary_key=True)
    estado_envio = models.CharField(max_length=20)
    fecha_actualizacion = models.DateField()
    id_entrega = models.ForeignKey(Entrega, on_delete=models.CASCADE, db_column='id_entrega')

    class Meta:
        db_table = 'seguimiento_entrega'
        unique_together = (('id_entrega',),)
        
class Pedido(models.Model):
    ESTADO_CHOICES = [
        ('en_curso', 'En curso'),
        ('procesando', 'Procesando'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]
    id_pedido = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='id_usuario')
    carrito = models.OneToOneField(Carrito, on_delete=models.CASCADE, db_column='id_carrito')
    venta = models.OneToOneField(Venta, on_delete=models.CASCADE, db_column='id_venta', null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='en_curso')
    observacion = models.CharField(max_length=200, blank=True, null=True)
    direccion_entrega = models.CharField(max_length=255, blank=True, null=True)
    tipo_entrega = models.CharField(max_length=50, blank=True, null=True)
    metodo_pago = models.CharField(max_length=50, blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        db_table = 'pedido'

    def __str__(self):
        return f"Pedido {self.id_pedido} - {self.usuario.nombre} {self.usuario.apellido}"

class TipoEntrega(models.Model):
    id_tipo_entrega = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=50)
    id_entrega = models.ForeignKey(Entrega, on_delete=models.CASCADE, db_column='id_entrega')

    class Meta:
        db_table = 'tipo_entrega'

class TipoDocumento(models.Model):
    id_tipo_documento = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=50)
    id_comprobante = models.ForeignKey(Comprobante, on_delete=models.CASCADE, db_column='id_comprobante')

    class Meta:
        db_table = 'tipo_documento'
        
class DetallePedido(models.Model):
    id_detalle_pedido = models.AutoField(primary_key=True)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)  # Relación al pedido
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)  # Relación al producto
    cantidad = models.IntegerField()
    precio = models.IntegerField()
    
    class Meta:
        db_table = 'detalle_pedido'
        managed = False  # <--- Agrega esto