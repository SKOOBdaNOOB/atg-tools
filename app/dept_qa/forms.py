from django import forms
from django.forms import formset_factory

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit

from app.core.models import ProductGeneration, Component, AddOnProduct, Customer, Platform
from .models import Checklist


class CustomerPresetForm(forms.Form):
    preset = forms.CharField(
        max_length=100,
        label='Preset',
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
    )
    channel = forms.CharField(
        max_length=100,
        label='Channel',
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
    )

CustomerPresetFormSet = formset_factory(CustomerPresetForm, extra=1, can_delete=True)


class PlatformSelectionForm(forms.Form):
    iris_number = forms.CharField(
        max_length=100,
        label='IRIS Number',
        widget=forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
    )
    product_generation = forms.ModelChoiceField(
        queryset=ProductGeneration.objects.all(),
        label='Platform',
        widget=forms.Select(attrs={'class': 'select select-bordered w-full'}),
    )
    customer = forms.CharField(
        max_length=100,
        label='Customer',
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full',
            'id': 'customer-input',
            'autocomplete': 'off',
        }),
    )
    components = forms.ModelMultipleChoiceField(
        queryset=Component.objects.filter(add_on_products__isnull=True).distinct(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Components',
    )
    # add_ons = forms.ModelMultipleChoiceField(
    #     queryset=AddOnProduct.objects.all(),
    #     widget=forms.CheckboxSelectMultiple,
    #     required=False,
    #     label='Add-ons',
    # )
    customer_presets = forms.JSONField(
        required=False,
        help_text='Enter customer-specific presets for radios.',
        widget=forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full'}),
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Initialize the FormHelper
        self.helper = FormHelper()
        self.helper.form_method = 'post'

        # Define the layout
        self.helper.layout = Layout(
            Field('iris_number'),
            Field('product_generation'),
            Field('customer'),
            Field('components'),
            # Field('add_ons'),
            Field('customer_presets'),
            Submit('submit', 'Generate Checklist', css_class='btn btn-primary'),
        )

        # Apply default classes to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' w-full'

            # Additional classes based on field type
            if isinstance(field.widget, forms.TextInput):
                field.widget.attrs['class'] += ' input input-bordered'
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] += ' select select-bordered appearance-none'
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs['class'] += ' textarea textarea-bordered'
            elif isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs['class'] += ' checkbox checkbox-primary'

            # Add placeholders if desired
            field.widget.attrs['placeholder'] = field.label

    def clean_iris_number(self):
        iris_number = self.cleaned_data.get('iris_number')
        
        return iris_number

    def clean(self):
        cleaned_data = super().clean()
        iris_number = cleaned_data.get('iris_number')
        product_generation = cleaned_data.get('product_generation')
        customer_name = cleaned_data.get('customer')

        if iris_number and product_generation and customer_name:
            # Get or create the Customer instance
            customer, _ = Customer.objects.get_or_create(name=customer_name)

            # Check if a Platform with the given IRIS Number exists
            try:
                platform = Platform.objects.get(iris_number=iris_number)

                # Platform exists; check if product_generation and customer match
                if platform.product_generation != product_generation or platform.customer != customer:
                    self.add_error('iris_number', "A platform with this IRIS Number already exists with different product generation or customer.")
                else:
                    # Check if a Checklist already exists for this Platform
                    if Checklist.objects.filter(platform=platform).exists():
                        self.add_error('iris_number', "A checklist already exists for this platform.")
            except Platform.DoesNotExist:
                # Platform does not exist; no issues
                pass
        else:
            # One or more required fields are missing; let individual field validators handle it
            pass

        # Existing validation logic for components and add-ons
        components = set(cleaned_data.get('components', []))
        # add_ons = cleaned_data.get('add_ons', [])

        # Get components included in selected add-ons
        # add_on_components = set(Component.objects.filter(addons__in=add_ons).distinct())

        # Check for overlapping components
        # overlapping_components = components & add_on_components
        # if overlapping_components:
        #     overlapping_names = ', '.join([component.name for component in overlapping_components])
        #     raise forms.ValidationError(
        #         f"You have selected components that are included in the selected add-ons: {overlapping_names}. "
        #         "Please adjust your selections to avoid duplicates."
        #     )
