from rest_framework import serializers
from .models import Category, Product, ProductImage, ProductLine, AttributeValue, Attribute


class CategorySerializer(serializers.ModelSerializer):

    """Serializer for Category model."""

    category = serializers.CharField(source='name')

    class Meta:
        model = Category
        fields = ['category', 'slug']


class ProductImageSerializer(serializers.ModelSerializer):

    """Serializer for ProductImage model."""

    class Meta:
        model = ProductImage
        exclude = ('id', 'product_line')


class AttributeSerializer(serializers.ModelSerializer):

    """Serializer for Attribute model."""

    class Meta:
        model = Attribute
        fields = ('id', 'name')


class AttributeValueSerializer(serializers.ModelSerializer):

    """Serializer for AttributeValue model."""

    attribute = AttributeSerializer(many=False)

    class Meta:
        model = AttributeValue
        fields = ('id', 'attribute', 'attribute_value')


class ProductLineSerializer(serializers.ModelSerializer):

    """Serializer for ProductLine model."""

    product_image = ProductImageSerializer(many=True)
    attribute_value = AttributeValueSerializer(many=True)

    class Meta:
        model = ProductLine
        fields = ('price', 'sku', 'stock_qty', 'order', 'product_image', 'attribute_value')

    def to_representation(self, instance):
        """Converts instance to representation."""
        data = super().to_representation(instance)
        av_data = data.pop('attribute_value')
        attr_values = {}
        for key in av_data:
            attr_values.update({key['attribute']['id']: key['attribute_value']})
        data.update({'specification': attr_values})
        return data


class ProductSerializer(serializers.ModelSerializer):

    """Serializer for Product model."""

    product_line = ProductLineSerializer(many=True)
    attribute_value = AttributeValueSerializer(many=True)

    class Meta:
        model = Product
        fields = ('name', 'slug', 'pid', 'description', 'product_line', 'attribute_value')

    def to_representation(self, instance):
        """Converts instance to representation."""
        data = super().to_representation(instance)
        av_data = data.pop('attribute_value')
        attr_values = {}
        for key in av_data:
            attr_values.update({key['attribute']['name']: key['attribute_value']})
        data.update({'attribute': attr_values})

        return data


class ProductLineCategorySerializer(serializers.ModelSerializer):

    """Serializer for ProductLine in Category."""

    product_image = ProductImageSerializer(many=True)

    class Meta:
        model = ProductLine
        fields = ('price', 'product_image')


class ProductCategorySerializer(serializers.ModelSerializer):

    """Serializer for Product in Category."""

    product_line = ProductLineCategorySerializer(many=True)

    class Meta:
        model = Product
        fields = ('name', 'slug', 'pid', 'created_at', 'product_line')

    def to_representation(self, instance):
        """Converts instance to representation."""
        data = super().to_representation(instance)
        product_line = data.pop('product_line')

        if product_line:
            item = product_line[0]
            data.update({'price': item['price'], 'image': item['product_image']})

        return data
