from rest_framework import serializers

from product.serializers.category_serializer import Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            'title',
            'slug',
            'description',
            'active',
        ]