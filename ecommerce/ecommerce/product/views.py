from django.db.models import Prefetch
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer, ProductCategorySerializer


class CategoryViewSet(viewsets.ViewSet):

    """A viewset for handling category-related operations."""

    queryset = Category.objects.all().is_active()

    @extend_schema(responses=CategorySerializer)
    def list(self, request):
        """
        Retrieves a list of active categories.

        Returns
        -------
            Response: Serialized data of active categories.

        """
        serializer = CategorySerializer(self.queryset, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ViewSet):

    """A viewset for handling product-related operations."""

    queryset = Product.objects.all().is_active()

    lookup_field = 'slug'

    def retrieve(self, request, slug=None):
        """
        Retrieves a product by slug.

        Args:
            request: The request object.
            slug (str): The slug of the product.

        Returns
        -------
            Response: Serialized data of the retrieved product.

        """
        serializer = ProductSerializer(
            self.queryset.filter(slug=slug).prefetch_related(
                Prefetch('attribute_value__attribute')
            ).prefetch_related(
                Prefetch('product_line__product_image')).prefetch_related(
                Prefetch('product_line__attribute_value__attribute')
            ), many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=False, url_path=r'category/(?P<slug>[\w-]+)')
    def list_product_by_category_slug(self, request, slug=None):
        """
        Retrieves products by category slug.

        Args:
            request: The request object.
            slug (str): The slug of the category.

        Returns
        -------
            Response: Serialized data of products belonging to the specified category.

        """
        serializer = ProductCategorySerializer(self.queryset.filter(category__slug=slug),
                                               many=True)
        return Response(serializer.data)
