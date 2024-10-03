from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views import View
from django.db import models
from django.http import JsonResponse

from collections import defaultdict

from app.core.models import Platform, Component, ComponentType, AddOnProduct, Customer, ProductGeneration
from .models import Checklist, ChecklistTask, Task
from .forms import PlatformSelectionForm, CustomerPresetFormSet


class CustomerAutocompleteView(View):
    def get(self, request):
        term = request.GET.get('term', '')
        customers = Customer.objects.filter(name__icontains=term).values_list('name', flat=True)
        return JsonResponse(list(customers), safe=False)


class GenerateChecklistView(View):
    """
    Handles the creation of a new checklist based on selected components and add-ons.
    """
    def get(self, request):
        form = PlatformSelectionForm()
        preset_formset = CustomerPresetFormSet()
        component_groups = self.get_component_groups()
        return render(request, 'dept_qa/generate_checklist.html', {
            'form': form,
            'preset_formset': preset_formset,
            'component_groups': component_groups,
        })

    def post(self, request):
        form = PlatformSelectionForm(request.POST)
        preset_formset = CustomerPresetFormSet(request.POST)
        component_groups = self.get_component_groups()
        if form.is_valid() and preset_formset.is_valid():
            # Retrieve form data
            iris_number = form.cleaned_data['iris_number']
            product_generation = form.cleaned_data['product_generation']
            components = form.cleaned_data['components']
            # add_ons = form.cleaned_data['add_ons']
            customer_name = form.cleaned_data['customer']

            # Get or create the Customer instance
            customer, _ = Customer.objects.get_or_create(name=customer_name)

            # Get or create the Platform instance
            platform, created = Platform.objects.get_or_create(
                iris_number=iris_number,
                defaults={
                    'product_generation': product_generation,
                    'customer': customer,
                }
            )

            # Update Platform details if it already exists
            if not created:
                platform.product_generation = product_generation
                platform.customer = customer
                platform.save()

            # Set components and add-ons
            platform.components.set(components)
            # platform.add_ons.set(add_ons)
            platform.save()

            # Process customer presets
            customer_presets = []
            for preset_form in preset_formset:
                if preset_form.cleaned_data:
                    preset = preset_form.cleaned_data.get('preset')
                    channel = preset_form.cleaned_data.get('channel')
                    if preset and channel:
                        customer_presets.append({'preset': preset, 'channel': channel})

            # Update customer_presets on the Platform
            platform.customer_presets = customer_presets
            platform.save()

            # Generate the checklist
            checklist = Checklist.objects.create(platform=platform)

            # Collect components from selected add-ons
            # add_on_components = Component.objects.filter(add_on_products__in=add_ons).distinct()

            # Combine selected components and add-on components
            all_components = components # | add_on_components

            # Get the IDs of all components
            all_component_ids = all_components.values_list('id', flat=True)

            # Collect tasks associated with the combined components
            component_tasks = Task.objects.filter(components__id__in=all_component_ids).distinct()

            # Fetch generation-specific tasks not tied to components
            generation_tasks = Task.objects.filter(
                product_generations=product_generation,
                components__isnull=True
            ).distinct()

            # Combine tasks
            tasks = (component_tasks | generation_tasks).distinct().order_by('order')

            # Create ChecklistTask instances
            for task in tasks:
                ChecklistTask.objects.create(
                    checklist=checklist,
                    task=task
                )

            return redirect('dept_qa:checklist_detail', iris_number=checklist.platform.iris_number)
        else:
            return render(request, 'dept_qa/generate_checklist.html', {
                'form': form,
                'preset_formset': preset_formset,
                'component_groups': component_groups,
            })

    def get_component_groups(self):
        # Get all component types
        component_types = ComponentType.objects.all().order_by('name')

        # Initialize the component groups dictionary
        component_groups = {}

        for ct in component_types:
            # Get components for each component type
            components = ct.components_set.filter(
                # add_on_products__isnull=True
            ).order_by('name')

            if components.exists():
                component_groups[ct] = components

        return component_groups



class ChecklistDetailView(View):
    """
    Displays the details of a specific checklist, allowing QA specialists to mark tasks as complete.
    """
    
    def post(self, request, iris_number):
        platform = get_object_or_404(Platform, iris_number=iris_number)
        checklist = get_object_or_404(Checklist, platform=platform)
        tasks = ChecklistTask.objects.filter(checklist=checklist).select_related('task').order_by('task__order')

        # Process form data
        for task in tasks:
            status = request.POST.get(f'status_{task.id}')
            notes = request.POST.get(f'notes_{task.id}')
            if status in ['Complete', 'Incomplete', 'Failed']:
                task.status = status
            task.notes = notes
            task.save()

        # Check if all tasks are complete
        if checklist.is_complete():
            checklist.completed_on = timezone.now()
            checklist.save()

        return redirect('dept_qa:checklist_detail', iris_number=iris_number)

    def get(self, request, iris_number):
        platform = get_object_or_404(Platform, iris_number=iris_number)
        checklist = get_object_or_404(Checklist, platform=platform)
        tasks = ChecklistTask.objects.filter(checklist=checklist).select_related('task').order_by('task__order')
        completion_percentage = checklist.completion_percentage()
        # Build the grouped task tree
        task_groups = self.build_task_groups(tasks)
        return render(request, 'dept_qa/checklist_detail.html', {
            'checklist': checklist,
            'completion_percentage': completion_percentage,
            'task_groups': task_groups,
        })

    def build_task_groups(self, tasks):
        """
        Groups tasks by Component Type and builds a nested task tree.
        """
        # Organize tasks by their Component Types
        component_type_groups = {}

        # Tasks not associated with any Component Type
        general_tasks = []

        for task_obj in tasks:
            task = task_obj.task
            component_types = task.components.values_list('component_types__name', flat=True).distinct()

            if component_types:
                for ct_name in component_types:
                    if ct_name not in component_type_groups:
                        component_type_groups[ct_name] = []
                    component_type_groups[ct_name].append(task_obj)
            else:
                # For tasks not associated with any Component Type
                general_tasks.append(task_obj)

        # Build task trees for each group
        for ct_name, task_list in component_type_groups.items():
            component_type_groups[ct_name] = self.build_task_tree(task_list)

        # Build task tree for general tasks
        general_task_tree = self.build_task_tree(general_tasks)

        return {
            'component_type_groups': component_type_groups,
            'general_tasks': general_task_tree,
        }

    def build_task_tree(self, tasks):
        """
        Builds a nested task tree from a list of ChecklistTask objects.
        """
        task_dict = {}
        for task_obj in tasks:
            task_dict[task_obj.task.id] = {'task': task_obj, 'subtasks': []}

        root_tasks = []
        for task_obj in tasks:
            task = task_obj.task
            if task.parent_task:
                parent_id = task.parent_task.id
                if parent_id in task_dict:
                    task_dict[parent_id]['subtasks'].append(task_dict[task.id])
                else:
                    # Parent task not in tasks, could be a task from another component or general task
                    pass
            else:
                root_tasks.append(task_dict[task.id])

        return root_tasks
