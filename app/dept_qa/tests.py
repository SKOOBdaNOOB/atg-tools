from django.test import TestCase
from django.db.utils import IntegrityError
from app.core.models import Platform, Component, ProductGeneration, ProductLine, Customer
from .models import Task, Checklist, ChecklistTask, IssueResolution

class TaskModelTest(TestCase):
    def setUp(self):
        self.component = Component.objects.create(name='GPS Module')
        self.product_line = ProductLine.objects.create(name='Vehicle Surveillance System')
        self.generation = ProductGeneration.objects.create(product_line=self.product_line, generation_number='1')

    def test_create_task(self):
        task = Task.objects.create(name='Test GPS Functionality', order=1)
        task.components.add(self.component)
        task.product_generations.add(self.generation)
        self.assertEqual(task.name, 'Test GPS Functionality')
        self.assertEqual(task.order, 1)
        self.assertIn(self.component, task.components.all())
        self.assertIn(self.generation, task.product_generations.all())
        self.assertFalse(task.is_subtask)
        self.assertEqual(str(task), 'Test GPS Functionality')

    def test_create_subtask(self):
        parent_task = Task.objects.create(name='Main Task', order=1)
        subtask = Task.objects.create(name='Sub Task', parent_task=parent_task, order=2)
        self.assertEqual(subtask.parent_task, parent_task)
        self.assertTrue(subtask.is_subtask)
        self.assertEqual(str(subtask), 'Sub Task')

class ChecklistModelTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(name='Test Agency', timezone='UTC')
        self.product_line = ProductLine.objects.create(name='Vehicle Surveillance System')
        self.generation = ProductGeneration.objects.create(product_line=self.product_line, generation_number='1')
        self.platform = Platform.objects.create(
            iris_number='IRIS200',
            product_generation=self.generation,
            customer=self.customer
        )

    def test_create_checklist(self):
        checklist = Checklist.objects.create(platform=self.platform)
        self.assertEqual(checklist.platform, self.platform)
        self.assertIsNotNone(checklist.created_on)
        self.assertIsNone(checklist.completed_on)
        self.assertFalse(checklist.is_complete())
        self.assertEqual(str(checklist), f"Checklist for IRIS200 - {checklist.created_on.strftime('%Y-%m-%d')}")

class ChecklistTaskModelTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(name='Test Agency', timezone='UTC')
        self.product_line = ProductLine.objects.create(name='Vehicle Surveillance System')
        self.generation = ProductGeneration.objects.create(product_line=self.product_line, generation_number='1')
        self.platform = Platform.objects.create(
            iris_number='IRIS200',
            product_generation=self.generation,
            customer=self.customer
        )
        self.checklist = Checklist.objects.create(platform=self.platform)
        self.task = Task.objects.create(name='Test GPS Functionality', order=1)

    def test_create_checklist_task(self):
        checklist_task = ChecklistTask.objects.create(
            checklist=self.checklist,
            task=self.task,
            status='Incomplete'
        )
        self.assertEqual(checklist_task.checklist, self.checklist)
        self.assertEqual(checklist_task.task, self.task)
        self.assertEqual(checklist_task.status, 'Incomplete')
        self.assertEqual(str(checklist_task), 'Test GPS Functionality - Incomplete')

    def test_unique_constraint(self):
        ChecklistTask.objects.create(
            checklist=self.checklist,
            task=self.task,
            status='Incomplete'
        )
        with self.assertRaises(IntegrityError):
            ChecklistTask.objects.create(
                checklist=self.checklist,
                task=self.task,
                status='Incomplete'
            )

class IssueResolutionModelTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(name='Test Agency', timezone='UTC')
        self.product_line = ProductLine.objects.create(name='Vehicle Surveillance System')
        self.generation = ProductGeneration.objects.create(product_line=self.product_line, generation_number='1')
        self.platform = Platform.objects.create(
            iris_number='IRIS200',
            product_generation=self.generation,
            customer=self.customer
        )
        self.checklist = Checklist.objects.create(platform=self.platform)

    def test_create_issue_resolution(self):
        issue = IssueResolution.objects.create(
            checklist=self.checklist,
            issue_description='GPS module not responding.'
        )
        self.assertEqual(issue.checklist, self.checklist)
        self.assertEqual(issue.issue_description, 'GPS module not responding.')
        self.assertIsNone(issue.resolution)
        self.assertIsNotNone(issue.reported_on)
        self.assertIsNone(issue.resolved_on)
        self.assertEqual(str(issue), f"Issue on IRIS200 - Reported on {issue.reported_on.strftime('%Y-%m-%d')}")
