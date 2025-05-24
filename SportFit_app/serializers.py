from rest_framework import serializers
from .models import Pedido

class PedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = [
            'id_pedido', 'usuario', 'direccion_entrega', 'tipo_entrega',
            'metodo_pago', 'total', 'estado', 'fecha_creacion'
        ]