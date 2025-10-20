from django.urls import path
from .views import ProductListAV

urlpatterns = [
    path('products/', ProductListAV.as_view(), name='product-list')
]
