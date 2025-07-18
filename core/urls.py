from django.urls import path, include
from core import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('latest-products/', views.LatestProductList.as_view()),
    path('api/v1/', views.LatestProductList.as_view()),
    path('products/', views.ProductList.as_view()),
    path('products/search/', views.search),
    path('register/', views.CustomerRegisterView.as_view()),
    path('login/', views.LoginView.as_view()),
    path('cart/', views.CartView.as_view()),
    path('products/<slug:category_slug>/<slug:product_slug>/', views.ProductDetail.as_view()),
    path('products/<slug:category_slug>/', views.CategoryDetail.as_view()),
    
]