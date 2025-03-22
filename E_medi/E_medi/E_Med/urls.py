# urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('signup/', views.user_signup, name='signup'),
    path('signup_success/', views.signup_success, name='signup_success'),
    path('product_list/', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('category_list/', views.category_list, name='category_list'),
    path('cart/', views.cart_view, name='cart'),
    path('ocr_scan/', views.ocr_scan, name='ocr_scan'),
    path('add_to_cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('add_from_ocr/', views.add_from_ocr, name='add_from_ocr'),
    path('cart_list/', views.cart_list, name='cart_list'),
    path('logout/', views.user_logout, name='logout'),
]
