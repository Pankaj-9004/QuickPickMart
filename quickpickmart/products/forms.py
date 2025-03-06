from django import forms
from .models import Product, Category

class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Show only main categories (parent categories)
        self.fields['category'].queryset = Category.objects.filter(parent=None).order_by("name")
        # Set default empty queryset for subcategories & sub-subcategories
        self.fields['subcategory'].queryset = Category.objects.none()
        self.fields['sub_subcategory'].queryset = Category.objects.none()
        
        # Filter subcategories based on the selected category
        if 'category' in self.data:
            try:
                category_id = int(self.data.get('category'))
                self.fields['subcategory'].queryset = Category.objects.filter(parent_id=category_id).order_by("name")
            except (ValueError, TypeError):
                self.fields['subcategory'].queryset = Category.objects.none()
        elif self.instance.pk:
            self.fields['subcategory'].queryset = Category.objects.filter(parent=self.instance.category).order_by("name")

        # Filter sub-subcategories based on the selected subcategory
        if 'subcategory' in self.data:
            try:
                subcategory_id = int(self.data.get('subcategory'))
                self.fields['sub_subcategory'].queryset = Category.objects.filter(parent_id=subcategory_id).order_by("name")
            except (ValueError, TypeError):
                self.fields['sub_subcategory'].queryset = Category.objects.none()
        elif self.instance.pk:
            self.fields['sub_subcategory'].queryset = Category.objects.filter(parent=self.instance.subcategory).order_by("name")
