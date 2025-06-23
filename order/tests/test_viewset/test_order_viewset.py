import json
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from order.factories import OrderFactory, UserFactory
from order.models import Order
from product.factories import CategoryFactory, ProductFactory
from product.models import Product


class TestOrderViewSet(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # Cria e autentica um usuário (caso a API exija autenticação)
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)

        self.category = CategoryFactory(title="technology")
        self.product = ProductFactory(
            title="mouse", price=100, category=[self.category]
        )
        self.order = OrderFactory(product=[self.product], user=self.user)

    def test_order(self):
        response = self.client.get(reverse("order-list", kwargs={"version": "v1"}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        order_data = json.loads(response.content)

        # Verifica se a resposta tem paginação
        if isinstance(order_data, dict) and 'results' in order_data:
            self.assertIn('results', order_data)
            self.assertIn('count', order_data)

            results = order_data['results']
            self.assertIsInstance(results, list)
            self.assertTrue(results)

            first_result = results[0]
        else:
            self.assertIsInstance(order_data, list)
            self.assertTrue(order_data)

            first_result = order_data[0]

        self.assertIsInstance(first_result, dict)
        self.assertIn("product", first_result)

        product_data = first_result["product"]

        if isinstance(product_data, list):
            self.assertTrue(product_data)
            product_data = product_data[0]

        self.assertEqual(product_data["title"], self.product.title)
        self.assertEqual(product_data["price"], self.product.price)
        self.assertEqual(product_data["active"], self.product.active)

        category_data = product_data.get("category")
        self.assertIsNotNone(category_data)

        if isinstance(category_data, list):
            self.assertTrue(category_data)
            self.assertEqual(category_data[0]["title"], self.category.title)
        else:
            self.assertEqual(category_data["title"], self.category.title)

    def test_create_order(self):
        product = ProductFactory()
        data = json.dumps({"products_id": [product.id], "user": self.user.id})

        response = self.client.post(
            reverse("order-list", kwargs={"version": "v2"}),
            data=data,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Corrigido: usa filter + order_by para evitar MultipleObjectsReturned
        created_order = Order.objects.filter(user=self.user).order_by('-id').first()

        self.assertIsNotNone(created_order)
        self.assertIn(product, created_order.product.all())
