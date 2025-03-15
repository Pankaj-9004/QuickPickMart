from django.db import models
from django.utils.text import slugify
from django.utils.html import mark_safe

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(blank=True)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, related_name="subcategories", null=True, blank=True
    )

    class Meta:
        unique_together = ('name', 'parent')  # Ensures unique subcategory names within a category

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            if self.parent:
                self.slug = f"{self.parent.slug}-{base_slug}"  # Ensures unique slug under different parents
            else:
                self.slug = base_slug
        original_slug = self.slug
        count = 1
        while Category.objects.filter(slug=self.slug).exclude(id=self.id).exists():
            self.slug = f"{original_slug}-{count}"
            count += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.parent.name} → {self.name}" if self.parent else self.name


class Product(models.Model):
    title = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, limit_choices_to={'parent': None}, related_name="products")
    subcategory = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="product_subcategories", null=True, blank=True)
    sub_subcategory = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="product_sub_subcategories", blank=True, null=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to="product_images/")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def image_preview(self):
        if self.image:
            return mark_safe(f'<img src="{self.image.url}" width="50" height="50" style="border-radius:5px;" />')
        return "No Image"

    image_preview.short_description = "Image Preview"

    def __str__(self):
        return self.title