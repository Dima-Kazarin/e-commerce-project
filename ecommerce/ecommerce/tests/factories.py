import factory

from ecommerce.ecommerce.product.models import (Attribute, AttributeValue, Category, Product, ProductImage,
                                                ProductLine,ProductType, ProductLineAttributeValue)


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: 'test_category_%d' % n)
    slug = factory.Sequence(lambda n: 'test_slug_%d' % n)


class ProductTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductType

    name = factory.Sequence(lambda n: 'test_type_name_%d' % n)

    @factory.post_generation
    def attribute(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        self.attribute.add(*extracted)


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Sequence(lambda n: 'test_product_name_%d' % n)
    pid = factory.Sequence(lambda n: '0000_%d' % n)
    description = "test_description"
    is_digital = True
    category = factory.SubFactory(CategoryFactory)
    is_active = True
    product_type = factory.SubFactory(ProductTypeFactory)

    @factory.post_generation
    def attribute_value(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        self.attribute_value.add(*extracted)


class ProductLineFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductLine

    price = 10.00
    sku = "12345"
    stock_qty = 1
    product = factory.SubFactory(ProductFactory)
    is_active = True
    weight = 100
    product_type = factory.SubFactory(ProductTypeFactory)

    @factory.post_generation
    def attribute_value(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        self.attribute_value.add(*extracted)


class ProductImageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductImage

    alternative_text = 'test text'
    url = 'test.jpg'
    product_line = factory.SubFactory(ProductLineFactory)


class AttributeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Attribute

    name = 'attribute_name_test'
    description = 'attr_description_test'


class AttributeValueFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AttributeValue

    attribute_value = 'attr_test'
    attribute = factory.SubFactory(AttributeFactory)


class ProductLineAttributeValueFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductLineAttributeValue

    attribute_value = factory.SubFactory(AttributeValueFactory)
    product_line = factory.SubFactory(ProductLineFactory)
