import json

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from order.factories import OrderFactory, UserFactory
from order.models import Order
from product.factories import CategoryFactory, ProductFactory
from product.models import Product


class TestOrderViewSet(APITestCase):

    client = APIClient()

    def setUp(self):
        self.category = CategoryFactory(title="technology")
        self.product = ProductFactory(
            title="mouse", price=100, category=[self.category]
        )
        self.order = OrderFactory(product=[self.product])

    def test_order(self):
        response = self.client.get(reverse("order-list", kwargs={"version": "v1"}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        order_data = json.loads(response.content)

        # Verifica se a resposta tem paginação (estrutura do DRF)
        if isinstance(order_data, dict) and 'results' in order_data:
            # Resposta paginada
            self.assertIn('results', order_data, "A chave 'results' nao esta presente na resposta paginada.")
            self.assertIn('count', order_data, "A chave 'count' nao esta presente na resposta paginada.")
            
            results = order_data['results']
            self.assertIsInstance(results, list, "results nao e uma lista.")
            self.assertTrue(results, "results esta vazia.")
            
            first_result = results[0]
        else:
            # Resposta sem paginação (lista direta)
            self.assertIsInstance(order_data, list, "order_data nao e uma lista.")
            self.assertTrue(order_data, "order_data esta vazia.")
            
            first_result = order_data[0]

        # Verifica se 'first_result' é um dicionário
        self.assertIsInstance(first_result, dict, "O primeiro item de results nao e um dicionario.")

        # Verifica se a chave 'product' existe em 'first_result'
        self.assertIn("product", first_result, "A chave 'product' nao esta presente no primeiro item de results.")

        product_data = first_result["product"]

        # Se 'product_data' for uma lista, pega o primeiro item
        if isinstance(product_data, list):
            self.assertTrue(product_data, "A lista product esta vazia.")
            product_data = product_data[0]

        self.assertEqual(product_data["title"], self.product.title)
        self.assertEqual(product_data["price"], self.product.price)
        self.assertEqual(product_data["active"], self.product.active)

        # Verifica se a categoria está correta
        category_data = product_data.get("category")
        self.assertIsNotNone(category_data, "A chave category nao esta presente em product.")

        if isinstance(category_data, list):
            self.assertTrue(category_data, "A lista category esta vazia.")
            self.assertEqual(category_data[0]["title"], self.category.title)
        else:
            self.assertEqual(category_data["title"], self.category.title)

    def test_create_order(self):
        user = UserFactory()
        product = ProductFactory()
        data = json.dumps({"products_id": [product.id], "user": user.id})

        self.client.force_authenticate(user=user)

        response = self.client.post(
            reverse("order-list", kwargs={"version": "v2"}),
            data=data,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_order = Order.objects.get(user=user)