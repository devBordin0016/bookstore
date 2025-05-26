import json

from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework.views import status

from product.factories import CategoryFactory
from product.models import Category


class CategoryViewSet(APITestCase):
    client = APIClient()

    def setUp(self):
        self.category = CategoryFactory(title="books")

    def test_get_all_category(self):
        response = self.client.get(reverse("category-list", kwargs={"version": "v1"}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        category_data = json.loads(response.content)

        # Verifica se a resposta tem paginação (estrutura do DRF)
        if isinstance(category_data, dict) and 'results' in category_data:
            # Resposta paginada
            self.assertIn('results', category_data, "A chave 'results' nao esta presente na resposta paginada.")
            self.assertIn('count', category_data, "A chave 'count' nao esta presente na resposta paginada.")
            
            results = category_data['results']
            self.assertIsInstance(results, list, "results nao e uma lista.")
            self.assertTrue(results, "results esta vazia.")
            
            first_category = results[0]
        else:
            # Resposta sem paginação (lista direta)
            self.assertIsInstance(category_data, list, "category_data nao e uma lista.")
            self.assertTrue(category_data, "category_data esta vazia.")
            
            first_category = category_data[0]

        self.assertEqual(first_category["title"], self.category.title)

    def test_create_category(self):
        data = json.dumps({"title": "technology"})

        response = self.client.post(
            reverse("category-list", kwargs={"version": "v1"}),
            data=data,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_category = Category.objects.get(title="technology")

        self.assertEqual(created_category.title, "technology")