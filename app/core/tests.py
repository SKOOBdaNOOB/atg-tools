from django.test import TestCase
from django.db.utils import IntegrityError
from timezone_field import TimeZoneField
from .models import Customer, ProductLine, ProductGeneration, ComponentType, Component, AddOnProduct, Platform

class CustomerModelTest(TestCase):
    def test_create_customer(self):
        customer = Customer.objects.create(
            name='Test Agency',
            address='123 Main St, Anytown, USA',
            timezone='America/New_York'
        )
        self.assertEqual(customer.name, 'Test Agency')
        self.assertEqual(customer.address, '123 Main St, Anytown, USA')
        self.assertEqual(str(customer.timezone), 'America/New_York')
        self.assertEqual(str(customer), 'Test Agency')

    def test_timezone_field(self):
        customer = Customer.objects.create(
            name='Timezone Test',
            timezone='UTC'
        )
        self.assertEqual(str(customer.timezone), 'UTC')

class ProductLineModelTest(TestCase):
    def test_create_product_line(self):
        product_line = ProductLine.objects.create(
            name='Vehicle Surveillance System',
            description='Covert surveillance vehicles'
        )
        self.assertEqual(product_line.name, 'Vehicle Surveillance System')
        self.assertEqual(str(product_line), 'Vehicle Surveillance System')

class ProductGenerationModelTest(TestCase):
    def test_create_product_generation(self):
        product_line = ProductLine.objects.create(name='Toolbox')
        generation = ProductGeneration.objects.create(
            product_line=product_line,
            generation_number='1',
            description='First generation toolbox'
        )
        self.assertEqual(generation.product_line.name, 'Toolbox')
        self.assertEqual(generation.generation_number, '1')
        self.assertEqual(str(generation), 'Toolbox - Gen 1')

    def test_unique_generation(self):
        product_line = ProductLine.objects.create(name='Toolbox')
        ProductGeneration.objects.create(
            product_line=product_line,
            generation_number='1'
        )
        with self.assertRaises(IntegrityError):
            ProductGeneration.objects.create(
                product_line=product_line,
                generation_number='1'
            )

class ComponentTypeModelTest(TestCase):
    def test_create_component_type(self):
        component_type = ComponentType.objects.create(name='Camera')
        self.assertEqual(component_type.name, 'Camera')
        self.assertEqual(str(component_type), 'Camera')

class ComponentModelTest(TestCase):
    def test_create_component(self):
        camera_type = ComponentType.objects.create(name='Camera')
        component = Component.objects.create(
            name='Camera Model A',
            requires_customer_preset=False
        )
        component.component_types.add(camera_type)
        self.assertIn(camera_type, component.component_types.all())
        self.assertEqual(component.name, 'Camera Model A')
        self.assertEqual(str(component), 'Camera Model A')

class AddOnProductModelTest(TestCase):
    def test_create_add_on_product(self):
        component = Component.objects.create(name='Mesh Radio')
        add_on = AddOnProduct.objects.create(
            name='Mesh Radio Package',
            description='Includes mesh radio and extra cameras'
        )
        add_on.components.add(component)
        self.assertIn(component, add_on.components.all())
        self.assertEqual(str(add_on), 'Mesh Radio Package')

class PlatformModelTest(TestCase):
    def test_create_platform(self):
        customer = Customer.objects.create(name='Test Agency', timezone='UTC')
        product_line = ProductLine.objects.create(name='Vehicle Surveillance System')
        generation = ProductGeneration.objects.create(product_line=product_line, generation_number='2')
        component = Component.objects.create(name='GPS Module')
        platform = Platform.objects.create(
            iris_number='IRIS100',
            product_generation=generation,
            customer=customer
        )
        platform.components.add(component)
        self.assertEqual(platform.iris_number, 'IRIS100')
        self.assertEqual(platform.product_generation, generation)
        self.assertEqual(platform.customer, customer)
        self.assertIn(component, platform.components.all())
        self.assertEqual(str(platform), 'IRIS100 - Vehicle Surveillance System - Gen 2')

    def test_unique_iris_number(self):
        customer = Customer.objects.create(name='Test Agency', timezone='UTC')
        product_line = ProductLine.objects.create(name='Vehicle Surveillance System')
        generation = ProductGeneration.objects.create(product_line=product_line, generation_number='1')
        Platform.objects.create(
            iris_number='IRIS100',
            product_generation=generation,
            customer=customer
        )
        with self.assertRaises(IntegrityError):
            Platform.objects.create(
                iris_number='IRIS100',
                product_generation=generation,
                customer=customer
            )
