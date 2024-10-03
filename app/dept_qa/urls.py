from django.urls import path
from . import views

app_name = 'app.dept_qa'

urlpatterns = [
    path('generate-checklist/', views.GenerateChecklistView.as_view(), name='generate_checklist'),
    path('checklist/iris-<str:iris_number>/', views.ChecklistDetailView.as_view(), name='checklist_detail'),
    path('customer-autocomplete/', views.CustomerAutocompleteView.as_view(), name='customer_autocomplete'),
    # Add more URLs as needed
]
