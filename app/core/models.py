from django.db import models
from timezone_field import TimeZoneField

class Customer(models.Model):
    """
    Represents a customer or organization purchasing products.
    """
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=500, blank=True, null=True)
    timezone = TimeZoneField(default='UTC')
    # Additional fields can be added as needed

    def __str__(self):
        return self.name


class ProductLine(models.Model):
    """
    Represents a category of products (e.g., Vehicle, Toolbox, Mesh Radio).
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class ProductGeneration(models.Model):
    """
    Represents a specific generation/version of a product line.
    """
    product_line = models.ForeignKey(ProductLine, on_delete=models.CASCADE, related_name='generations')
    generation_number = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('product_line', 'generation_number')

    def __str__(self):
        return f"{self.product_line.name} - Gen {self.generation_number}"


class ComponentType(models.Model):
    """
    Represents a high-level grouping of components (e.g., Cameras, Radios).
    """
    name = models.CharField(max_length=255)
    # components = models.ManyToManyField('Component', related_name='component_types')

    def __str__(self):
        return self.name


class Component(models.Model):
    """
    Represents individual components used in products.
    """
    name = models.CharField(max_length=255)
    component_types = models.ManyToManyField('ComponentType', related_name='components_set')
    add_on_products = models.ManyToManyField(
        'AddOnProduct',
        blank=True,
        related_name='components_with_this_addon'
    )
    requires_customer_preset = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class AddOnProduct(models.Model):
    """
    Represents add-on products that can be bundled with main products.
    """
    name = models.CharField(max_length=255)
    components = models.ManyToManyField(
        'Component',
        related_name='addons',  # Changed related_name
        blank=True
    )
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Platform(models.Model):
    """
    Represents a specific product instance with unique configurations.
    """
    iris_number = models.CharField(max_length=100, unique=True)
    product_generation = models.ForeignKey(ProductGeneration, on_delete=models.CASCADE, related_name='platforms')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='platforms')
    components = models.ManyToManyField(Component, related_name='platforms', blank=True)
    add_ons = models.ManyToManyField(AddOnProduct, related_name='platforms', blank=True)
    customer_presets = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.iris_number} - {self.product_generation}"
