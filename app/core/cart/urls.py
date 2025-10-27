from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.AddToCartView.as_view()),
    path('get/', views.GetCartView.as_view()),
    path('delete/', views.RemoveCartView.as_view()),
    path('clear/', views.GetCartView.as_view()),
    path('increment/', views.UpdateCartView.as_view()),
    path('increment/qty/', views.SetExiplicityView.as_view()),
]
