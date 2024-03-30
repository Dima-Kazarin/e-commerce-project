import pytest
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from ecommerce.ecommerce.product import models

pytestmark = pytest.mark.django_db


class TestCategoryModel:
    def test_str_method(self, category_factory):
        obj = category_factory(name='test_cat')
        assert obj.__str__() == 'test_cat'

    def test_name_max_length(self, category_factory):
        name = 'x' * 236
        obj = category_factory(name=name)
        with pytest.raises(ValidationError):
            obj.full_clean()

    def test_slug_max_length(self, category_factory):
        slug = 'x' * 256
        obj = category_factory(slug=slug)
        with pytest.raises(ValidationError):
            obj.full_clean()

    def test_name_unique_field(self, category_factory):
        category_factory(name='test_cat')
        with pytest.raises(IntegrityError):
            category_factory(name='test_cat')

    def test_slug_unique_field(self, category_factory):
        category_factory(slug='test_slug')
        with pytest.raises(IntegrityError):
            category_factory(slug='test_slug')

    def test_is_active_false_default(self, category_factory):
        obj = category_factory()
        assert obj.is_active is False

    def test_parent_category_on_delete_protect(self, category_factory):
        obj1 = category_factory()
        category_factory(parent=obj1)
        with pytest.raises(IntegrityError):
            obj1.delete()

    def test_parent_field_null(self, category_factory):
        obj1 = category_factory()
        assert obj1.parent is None

    def test_return_category_active_only_true(self, category_factory):
        category_factory(is_active=True)
        category_factory(is_active=False)
        qs = models.Category.objects.is_active().count()
        assert qs == 1

    def test_return_category_active_only_false(self, category_factory):
        category_factory(is_active=True)
        category_factory(is_active=False)
        qs = models.Category.objects.count()
        assert qs == 2


class TestProductModel:
    def test_str_method(self, product_factory):
        obj = product_factory(name='test_product')
        assert obj.__str__() == 'test_product'

    def test_name_max_length(self, product_factory):
        name = 'x' * 256
        obj = product_factory(name=name)
        with pytest.raises(ValidationError):
            obj.full_clean()

    def test_slug_max_length(self, product_factory):
        slug = 'x' * 256
        obj = product_factory(slug=slug)
        with pytest.raises(ValidationError):
            obj.full_clean()

    def test_pid_max_length(self, product_factory):
        pid = 'x' * 11
        obj = product_factory(pid=pid)
        with pytest.raises(ValidationError):
            obj.full_clean()

    def test_is_digital_false_default(self, product_factory):
        obj = product_factory(is_digital=False)
        assert obj.is_digital is False

    def test_fk_category_on_delete_protect(self, category_factory, product_factory):
        obj1 = category_factory()
        product_factory(category=obj1)
        with pytest.raises(IntegrityError):
            obj1.delete()

    def test_return_product_active_only_true(self, product_factory):
        product_factory(is_active=True)
        product_factory(is_active=False)
        qs = models.Product.objects.is_active().count()
        assert qs == 1

    def test_return_product_active_only_false(self, product_factory):
        product_factory(is_active=True)
        product_factory(is_active=False)
        qs = models.Product.objects.count()
        assert qs == 2


class TestProductLineModel:
    def test_str_method(self, product_line_factory):
        obj = product_line_factory(sku='12345')
        assert obj.__str__() == '12345'

    def test_duplicate_order_values(self, product_line_factory, product_factory):
        obj = product_factory()
        product_line_factory(order=1, product=obj)
        with pytest.raises(ValidationError):
            product_line_factory(order=1, product=obj).clean()

    def test_field_decimal_places(self, product_line_factory):
        price = 1.001
        with pytest.raises(ValidationError):
            product_line_factory(price=price)

    def test_field_sku_max_length(self, product_line_factory):
        sku = 'x' * 101
        with pytest.raises(ValidationError):
            product_line_factory(sku=sku)

    def test_is_active_false_default(self, product_line_factory):
        obj = product_line_factory(is_active=False)
        assert obj.is_active is False

    def test_fk_product_on_delete_protect(self, product_line_factory, product_factory):
        obj1 = product_factory()
        product_line_factory(product=obj1)
        with pytest.raises(IntegrityError):
            obj1.delete()

    def test_return_product_line_active_only_true(self, product_line_factory):
        product_line_factory(is_active=True)
        product_line_factory(is_active=False)
        qs = models.ProductLine.objects.is_active().count()
        assert qs == 1

    def test_return_product_line_active_only_false(self, product_line_factory):
        product_line_factory(is_active=True)
        product_line_factory(is_active=False)
        qs = models.ProductLine.objects.count()
        assert qs == 2

    def test_duplicate_attribute_inserts(self, product_line_factory, attribute_factory, attribute_value_factory,
                                         product_line_attribute_value_factory):
        obj1 = attribute_factory(name='shoe-color')
        obj2 = attribute_value_factory(attribute_value='red', attribute=obj1)
        obj3 = attribute_value_factory(attribute_value='blue', attribute=obj1)
        obj4 = product_line_factory()
        product_line_attribute_value_factory(attribute_value=obj2, product_line=obj4)
        with pytest.raises(ValidationError):
            product_line_attribute_value_factory(attribute_value=obj3, product_line=obj4)


class TestProductImageModel:
    def test_str_method(self, product_image_factory, product_line_factory):
        obj1 = product_line_factory(sku='12345')
        obj2 = product_image_factory(order='1', product_line=obj1)
        assert obj2.__str__() == '12345_img'

    def test_alternative_text_field_max_length(self, product_image_factory):
        alternative_text = 'x' * 101
        with pytest.raises(ValidationError):
            product_image_factory(alternative_text=alternative_text)

    def test_duplicate_order_values(self, product_image_factory, product_line_factory):
        obj = product_line_factory()
        product_image_factory(order=1, product_line=obj)
        with pytest.raises(ValidationError):
            product_image_factory(order=1, product_line=obj).clean()


class TestProductTypeModel:
    def test_str_method(self, product_type_factory):
        obj = product_type_factory.create(name='test_type')
        assert obj.__str__() == 'test_type'

    def test_name_field_max_length(self, product_type_factory):
        name = 'x' * 101
        obj = product_type_factory(name=name)
        with pytest.raises(ValidationError):
            obj.full_clean()

    def test_fk_product_type_on_delete_product(self, product_type_factory, product_line_factory):
        obj1 = product_type_factory()
        product_line_factory(product_type=obj1)
        with pytest.raises(IntegrityError):
            obj1.delete()


class TestAttributeModel:
    def test_str_method(self, attribute_factory):
        obj = attribute_factory(name='test_attribute')
        assert obj.__str__() == 'test_attribute'

    def test_name_field_max_length(self, attribute_factory):
        name = 'x' * 101
        obj = attribute_factory(name=name)
        with pytest.raises(ValidationError):
            obj.full_clean()


class TestAttributeValueModel:
    def test_str_method(self, attribute_value_factory, attribute_factory):
        obj_a = attribute_factory(name='test_attribute')
        obj_b = attribute_value_factory(attribute_value='test_value', attribute=obj_a)
        assert obj_b.__str__() == 'test_attribute-test_value'

    def test_name_field_max_length(self, attribute_value_factory):
        attribute_value = 'x' * 101
        obj = attribute_value_factory(attribute_value=attribute_value)
        with pytest.raises(ValidationError):
            obj.full_clean()
