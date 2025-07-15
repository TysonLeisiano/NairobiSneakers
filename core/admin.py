from django.contrib import admin

# Register your models here.
from .models import Product, Category, Customer

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Customer)
admin.site.site_header = "Online Store Admin"
