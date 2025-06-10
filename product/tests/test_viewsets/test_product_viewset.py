import json

from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase
from rest_framework.views import status

from order.factories import UserFactory
from product.factories import CategoryFactory, ProductFactory
from product.models import Product


class TestProductViewSet(APITestCase):
    client = APIClient()

    def setUp(self):
        self.user = UserFactory()
        token = Token.objects.create(user=self.user)  # added
        token.save()  # added

        self.product = ProductFactory(
            title="pro controller",
            price=200.00,
        )

    def test_get_all_product(self):
        token = Token.objects.get(user__username=self.user.username)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
        response = self.client.get(reverse("product-list", kwargs={"version": "v1"}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        product_data = json.loads(response.content)

        # Verifica se a resposta tem paginação (estrutura do DRF)
        if isinstance(product_data, dict) and 'results' in product_data:
            # Resposta paginada
            self.assertIn('results', product_data, "A chave 'results' nao esta presente na resposta paginada.")
            self.assertIn('count', product_data, "A chave 'count' nao esta presente na resposta paginada.")
            
            results = product_data['results']
            self.assertIsInstance(results, list, "results nao e uma lista.")
            self.assertTrue(results, "results esta vazia.")
            
            first_product = results[0]
        else:
            # Resposta sem paginação (lista direta)
            self.assertIsInstance(product_data, list, "product_data nao e uma lista.")
            self.assertTrue(product_data, "product_data esta vazia.")
            
            first_product = product_data[0]

        self.assertEqual(first_product["title"], self.product.title)
        self.assertEqual(first_product["price"], self.product.price)
        self.assertEqual(first_product["active"], self.product.active)

    def test_create_product(self):
        token = Token.objects.get(user__username=self.user.username)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
        category = CategoryFactory()
        data = json.dumps(
            {"title": "notebook", "price": 800.00,
                "categories_id": [category.id]}
        )

        response = self.client.post(
            reverse("product-list", kwargs={"version": "v1"}),
            data=data,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_product = Product.objects.get(title="notebook")

        self.assertEqual(created_product.title, "notebook")
        self.assertEqual(created_product.price, 800.00)