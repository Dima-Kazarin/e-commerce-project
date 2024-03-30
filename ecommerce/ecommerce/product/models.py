from django.core.exceptions import ValidationError
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from .fields import OrderField


class IsActiveQueryset(models.QuerySet):

    """A custom queryset manager to filter active objects."""

    def is_active(self):
        """
        Filter objects that are marked as active.

        Returns
        -------
            QuerySet: Filtered queryset containing active objects.

        """
        return self.filter(is_active=True)


class Category(MPTTModel):

    """
    Model representing product categories.

    Attributes
    ----------
        name (str): The name of the category.
        slug (str): The slug for the category URL.
        is_active (bool): Indicates if the category is active.
        parent (Category): The parent category.

    """

    name = models.CharField(max_length=235, unique=True)
    slug = models.SlugField(max_length=255, unique=True)
    is_active = models.BooleanField(default=False)
    parent = TreeForeignKey('self', on_delete=models.PROTECT, null=True, blank=True)
    objects = IsActiveQueryset.as_manager()

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):

    """
    Model representing products.

    Attributes
    ----------
        name (str): The name of the product.
        slug (str): The slug for the product URL.
        pid (str): The product ID.
        description (str): The description of the product.
        is_digital (bool): Indicates if the product is digital.
        is_active (bool): Indicates if the product is active.
        category (Category): The category to which the product belongs.
        product_type (ProductType): The type of the product.

    """

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=255)
    pid = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    is_digital = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    category = TreeForeignKey(Category, on_delete=models.PROTECT)
    product_type = models.ForeignKey('ProductType', on_delete=models.PROTECT,
                                     related_name='product_type')
    attribute_value = models.ManyToManyField('AttributeValue', through='ProductAttributeValue',
                                             related_name='product_attr_value')
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    objects = IsActiveQueryset.as_manager()

    def __str__(self):
        return self.name


class Attribute(models.Model):

    """
    Model representing attributes for products.

    Attributes
    ----------
        name (str): The name of the attribute.
        description (str): The description of the attribute.

    """

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class AttributeValue(models.Model):

    """
    Model representing values for attributes.

    Attributes
    ----------
        attribute_value (str): The value of the attribute.
        attribute (Attribute): The attribute to which the value belongs.

    """

    attribute_value = models.CharField(max_length=100)
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE,
                                  related_name='attribute_value')

    def __str__(self):
        return f'{self.attribute.name}-{self.attribute_value}'


class ProductLine(models.Model):

    """
    Model representing a line of a product.

    Attributes
    ----------
        price (Decimal): The price of the product line.
        sku (str): The stock keeping unit (SKU) of the product line.
        stock_qty (int): The quantity of stock available.
        is_active (bool): Indicates if the product line is active.
        order (int): The order of the product line.
        weight (float): The weight of the product line.
        product (Product): The product associated with the product line.
        product_type (ProductType): The type of product line.

    """

    price = models.DecimalField(decimal_places=2, max_digits=5)
    sku = models.CharField(max_length=100)
    stock_qty = models.IntegerField()
    is_active = models.BooleanField(default=False)
    order = OrderField(unique_for_field='product', blank=True)
    weight = models.FloatField()
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='product_line')
    product_type = models.ForeignKey('ProductType', on_delete=models.PROTECT,
                                     related_name='product_line_type')
    attribute_value = models.ManyToManyField(AttributeValue, through='ProductLineAttributeValue',
                                             related_name='product_line_attribute_value')
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    objects = IsActiveQueryset.as_manager()

    def clean(self):
        """
        Validates uniqueness of order field within product lines of the same product.

        Raises
        ------
            ValidationError: If duplicate order value is found.

        """
        query_set = ProductLine.objects.filter(product=self.product)
        for obj in query_set:
            if self.id != obj.id and self.order == obj.order:
                raise ValidationError('Duplicate value.')

    def save(self, *args, **kwargs):
        """
        Save method for ProductLine model instance.

        This method overrides the default save behavior to perform a full clean
        and then save the instance.

        Parameters
        ----------
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        """
        self.full_clean()
        return super(ProductLine, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.sku)


class ProductAttributeValue(models.Model):

    """
    Model representing the relationship between product and attribute values.

    Attributes
    ----------
        attribute_value (AttributeValue): The attribute value.
        product (Product): The product.

    """

    attribute_value = models.ForeignKey(AttributeValue, on_delete=models.CASCADE,
                                        related_name='product_value_av')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_value_pl')

    class Meta:
        unique_together = ('attribute_value', 'product')


class ProductLineAttributeValue(models.Model):

    """
    Model representing the relationship between product line and attribute values.

    Attributes
    ----------
        attribute_value (AttributeValue): The attribute value.
        product_line (ProductLine): The product line.

    """

    attribute_value = models.ForeignKey(AttributeValue, on_delete=models.CASCADE,
                                        related_name='product_attribute_value_av')
    product_line = models.ForeignKey(ProductLine, on_delete=models.CASCADE,
                                     related_name='product_attribute_value_pl')

    class Meta:
        unique_together = ('attribute_value', 'product_line')

    def clean(self):
        """
        Validates uniqueness of attribute values within a product line.

        Raises
        ------
            ValidationError: If duplicate attribute exists.

        """
        query_set = (ProductLineAttributeValue.objects.filter(attribute_value=self.attribute_value)
                     .filter(product_line=self.product_line).exists())

        if not query_set:
            iqs = (Attribute.objects.filter(
                attribute_value__product_line_attribute_value=self.product_line
            ).values_list('pk', flat=True))

            if self.attribute_value.attribute.id in list(iqs):
                raise ValidationError('Duplicate attribute exists')

    def save(self, *args, **kwargs):
        """
        Save method for ProductLineAttributeValue model instance.

        This method overrides the default save behavior to perform a full clean
        and then save the instance.

        Parameters
        ----------
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        """
        self.full_clean()
        return super(ProductLineAttributeValue, self).save(*args, **kwargs)


class ProductImage(models.Model):

    """
    Model representing images associated with product lines.

    Attributes
    ----------
        alternative_text (str): Alternative text for the image.
        url (ImageField): The URL of the image.
        order (int): The order of the image.
        product_line (ProductLine): The product line associated with the image.

    """

    alternative_text = models.CharField(max_length=100)
    url = models.ImageField(upload_to=None, default='test.jpg')
    order = OrderField(unique_for_field='product_line', blank=True)
    product_line = models.ForeignKey(ProductLine, on_delete=models.CASCADE,
                                     related_name='product_image')

    def clean(self):
        """
        Validates uniqueness of order field within product images of the same product line.

        Raises
        ------
            ValidationError: If duplicate order value is found.

        """
        query_set = ProductImage.objects.filter(product_line=self.product_line)
        for obj in query_set:
            if self.id != obj.id and self.order == obj.order:
                raise ValidationError('Duplicate value.')

    def save(self, *args, **kwargs):
        """
        Save method for ProductImage model instance.

        This method overrides the default save behavior to perform a full clean
        and then save the instance.

        Parameters
        ----------
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        """
        self.full_clean()
        return super(ProductImage, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.product_line.sku}_img'


class ProductType(models.Model):

    """
    Model representing types of products.

    Attributes
    ----------
        name (str): The name of the product type.
        parent (ProductType): The parent product type.

    """

    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', on_delete=models.PROTECT, null=True, blank=True)
    attribute = models.ManyToManyField(Attribute, through='ProductTypeAttribute',
                                       related_name='product_type_attribute')

    def __str__(self):
        return self.name


class ProductTypeAttribute(models.Model):

    """
    Model representing the relationship between product types and attributes.

    Attributes
    ----------
        product_type (ProductType): The product type.
        attribute (Attribute): The attribute.

    """

    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE,
                                     related_name='product_type_attribute_pt')
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE,
                                  related_name='product_type_attribute_a')

    class Meta:
        unique_together = ('product_type', 'attribute')
