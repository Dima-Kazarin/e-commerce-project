from django.core import checks
from django.core.exceptions import ObjectDoesNotExist
from django.db import models


class OrderField(models.PositiveIntegerField):

    """
    An integer field that automatically populates itself with a unique order value.

    Parameters
    ----------
        unique_for_field (str): The name of the field that this order field should be unique for.

    Attributes
    ----------
        description (str): Description of the field.

    Methods
    -------
        check: Performs model checks to ensure the field is properly configured.
        pre_save: Automatically assigns a unique order value before saving the model instance.

    """

    description = "Ordering field on a unique field"

    def __init__(self, unique_for_field=None, *args, **kwargs):
        """
        Initialize the OrderField.

        Parameters
        ----------
            unique_for_field (str, optional): The name of the field that

        Args:
        ----
            this order field should be unique for.

            *args: Positional arguments.
            **kwargs: Keyword arguments.

        """
        self.unique_for_field = unique_for_field
        super().__init__(*args, **kwargs)

    def check(self, **kwargs):
        """
        Perform model checks to ensure the field is properly configured.

        Returns
        -------
            list: A list of errors found during the check.

        """
        return [
            *super().check(**kwargs),
            *self._check_for_field_attribute(**kwargs),
        ]

    def _check_for_field_attribute(self, **kwargs):
        """
        Check if the unique_for_field attribute is properly defined.

        Returns
        -------
            list: A list of errors found during the check.

        """
        if self.unique_for_field is None:
            return [
                checks.Error("OrderField must define a 'unique_for_field' attribute")
            ]
        if self.unique_for_field not in [
            f.name for f in self.model._meta.get_fields()
        ]:
            return [
                checks.Error("OrderField entered does not match an existing model field")
            ]
        return []

    def pre_save(self, model_instance, add):
        """
        Automatically assign a unique order value before saving the model instance.

        Args:
            model_instance: The instance of the model.
            add (bool): True if a new instance is being added, False if it's an update.

        Returns
        -------
            int: The calculated order value.

        """
        if getattr(model_instance, self.attname) is None:
            query_set = self.model.objects.all()
            try:
                query = {
                    self.unique_for_field: getattr(
                        model_instance, self.unique_for_field
                    )
                }
                query_set = query_set.filter(**query)
                last_item = query_set.latest(self.attname)
                value = last_item.order + 1
            except ObjectDoesNotExist:
                value = 1
            return value
        return super().pre_save(model_instance, add)
