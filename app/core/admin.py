from django.contrib import admin
from .models import Customer, ProductLine, ProductGeneration, ComponentType, Component, AddOnProduct, Platform

admin.site.register(Customer)
admin.site.register(ProductLine)
admin.site.register(ProductGeneration)
admin.site.register(ComponentType)
admin.site.register(Component)
admin.site.register(AddOnProduct)
admin.site.register(Platform)
