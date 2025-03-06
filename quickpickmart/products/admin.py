from django.contrib import admin
from .models import Category, Product
from .forms import ProductAdminForm

# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "slug")  # Displays hierarchy in admin panel
    search_fields = ("name", "slug")  # Search by name and slug
    list_filter = ("parent",)  # Filter by parent category
    prepopulated_fields = {"slug": ("name",)}  # Auto-generate slug from name


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ("title", "price", "stock", "category", "subcategory", "sub_subcategory", "image_preview")  # Added subcategory fields
    search_fields = ("title", "category__name", "subcategory__name", "sub_subcategory__name")  # Added subcategory fields
    list_filter = ("category", "subcategory", "sub_subcategory", "price", "stock")  # Added subcategory fields
    readonly_fields = ("image_preview",)  # Prevent editing image preview
    
    class Media:
        js = ("products/js/script.js",)