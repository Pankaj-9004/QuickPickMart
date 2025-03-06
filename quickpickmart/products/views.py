from django.shortcuts import render
from django.http import JsonResponse
from .models import Category

# Create your views here.

def get_subcategories(request, category_id):
    subcategories = Category.objects.filter(parent_id=category_id).only("id", "name").order_by("name")
    return JsonResponse(list(subcategories.values("id", "name")), safe=False)

def get_sub_subcategories(request, subcategory_id):
    sub_subcategories = Category.objects.filter(parent_id=subcategory_id).only("id", "name").order_by("name")
    return JsonResponse(list(sub_subcategories.values("id", "name")), safe=False)