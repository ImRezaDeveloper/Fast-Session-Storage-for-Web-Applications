from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.AddToCartView.as_view()),
    path('get/', views.GetCartView.as_view())
]
