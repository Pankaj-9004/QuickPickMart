from django.contrib import admin
from .models import Category, Product
from .forms import ProductAdminForm

# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "slug")
    search_fields = ("name", "slug")
    list_filter = ("parent",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ("title", "price", "stock", "category", "subcategory", "sub_subcategory", "image_preview")
    search_fields = ("title", "category__name", "subcategory__name", "sub_subcategory__name")
    list_filter = ("category", "subcategory", "sub_subcategory", "price", "stock")
    readonly_fields = ("image_preview",)
    
    class Media:
        js = ("products/js/script.js",)