from rest_framework.viewsets import ModelViewSet

from order.models import Order
from order.serializers.order_serializer import OrderSerializer

class OrderViewSet(ModelViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()

    def get_queryset(self):
        return Order.objects.all().order_by("id")

    def get_serializer_context(self):
        # """Garantir que o contexto da requisição seja passado corretamente para o serializer"""
        return {"request": self.request}
