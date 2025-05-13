from rest_framework import serializers
from product.models import Product
from product.serializers.product_serializer import ProductSerializer
from order.models import Order

class OrderSerializer(serializers.ModelSerializer):
    # Serializa os produtos com os dados completos
    product = ProductSerializer(read_only=True, many=True)
    
    # Recebe os IDs dos produtos
    products_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), write_only=True, many=True
    )
    
    # Calcula o total do pedido
    total = serializers.SerializerMethodField()

    def get_total(self, instance):
        total = sum([product.price for product in instance.product.all()])
        return total

    class Meta:
        model = Order
        fields = ["product", "total", "user", "products_id"]
        extra_kwargs = {"product": {"required": False}}

    def create(self, validated_data):
        # Extrai os dados dos produtos e do usuário
        product_data = validated_data.pop("products_id")
        user_data = validated_data.pop("user")

        # Cria a ordem
        order = Order.objects.create(user=user_data)

        # Adiciona os produtos à ordem
        for product in product_data:
            order.product.add(product)

        return order
