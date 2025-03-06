from django.urls import path
from . import views

urlpatterns = [
    path("get-subcategories/<int:category_id>/", views.get_subcategories, name="get_subcategories"),
    path("get-sub-subcategories/<int:subcategory_id>/", views.get_sub_subcategories, name="get_sub_subcategories"),
]