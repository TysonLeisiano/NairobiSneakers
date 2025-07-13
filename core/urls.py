from django.urls import path, include
from core import views

urlpatterns = [
    path('latest-products/', views.LatestProductList.as_view()),
    path('api/v1/', views.LatestProductList.as_view()),
    path('products/', views.ProductList.as_view()),
    path('products/<slug:category_slug>/<slug:product_slug>/', views.ProductDetail.as_view()),
]