from django.contrib import admin
from .models import Category, Product
from .forms import ProductAdminForm

# Register your models here.

# Inline Subcategory Feature
class SubcategoryInline(admin.TabularInline):  # Use admin.StackedInline for a different style
    model = Category
    extra = 1  # Number of empty forms to display
    fk_name = "parent"  # Links subcategories to their parent

# Custom Filter to Display Category Levels
class CategoryLevelFilter(admin.SimpleListFilter):
    title = "Category Level"
    parameter_name = "category_level"

    def lookups(self, request, model_admin):
        return [
            ("main", "Main Category"),
            ("sub", "Subcategory"),
            ("subsub", "Sub-Subcategory"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "main":
            return queryset.filter(parent__isnull=True)  # Main Categories
        elif self.value() == "sub":
            return queryset.filter(parent__isnull=False, parent__parent__isnull=True)  # Subcategories
        elif self.value() == "subsub":
            return queryset.filter(parent__isnull=False, parent__parent__isnull=False)  # Sub-Subcategories

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "slug")
    search_fields = ("name", "slug")
    list_filter = ("parent", CategoryLevelFilter)
    prepopulated_fields = {"slug": ("name",)}
    inlines = [SubcategoryInline]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ("title", "price", "stock", "category", "subcategory", "sub_subcategory", "image_preview")
    search_fields = ("title", "category__name", "subcategory__name", "sub_subcategory__name")
    list_filter = ("category", "subcategory", "sub_subcategory", "price", "stock")
    readonly_fields = ("image_preview",)
    
    class Media:
        js = ("products/js/script.js",)