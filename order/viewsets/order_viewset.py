from rest_framework.viewsets import ModelViewSet

from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from order.models import Order
from order.serializers.order_serializer import OrderSerializer

class OrderViewSet(ModelViewSet):
    authentication_classes = [SessionAuthentication, BasicAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = OrderSerializer
    queryset = Order.objects.all().order_by("id")

    def get_queryset(self):
        return Order.objects.all().order_by("id")

    def get_serializer_context(self):
        # """Garantir que o contexto da requisição seja passado corretamente para o serializer"""
        return {"request": self.request}