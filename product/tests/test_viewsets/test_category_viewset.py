import json

from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework.views import status

from product.factories import CategoryFactory
from product.models import Category

from order.factories import UserFactory  # Corrigir: certifique-se de que essa importação exista

class TestCategoryViewSet(APITestCase):  # Corrigido: nome da classe deve começar com "Test" para ser reconhecida como teste

    def setUp(self):
        self.client = APIClient()

        # Criar e autenticar o usuário
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)

        self.category = CategoryFactory(title="books")

    def test_get_all_category(self):
        response = self.client.get(reverse("category-list", kwargs={"version": "v1"}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        category_data = json.loads(response.content)

        if isinstance(category_data, dict) and 'results' in category_data:
            results = category_data['results']
            self.assertTrue(results)
            first_category = results[0]
        else:
            self.assertTrue(category_data)
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
