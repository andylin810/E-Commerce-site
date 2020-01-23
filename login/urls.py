from django.urls import path
from  . import views
from django.conf.urls.static import static
from django.conf import settings



urlpatterns = [
    path('', views.loginpage, name='login'),
    path('logged/', views.loggedpage, name='logged'),
    path('products/', views.productlist, name='products'),
    path('products/<int:product_id>/', views.productdetail, name='product_detail'),
    path('post_product/', views.post_product, name='post_product'),
    path('cart/', views.cart, name='cart'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('delete_product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('delete_from_cart/<str:product_name>/', views.delete_from_cart, name='delete_from_cart'),
    path('register/', views.register, name='register'),
    path('logout/', views.log_out, name='logout'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment/',views.payment,name='payment'),
]