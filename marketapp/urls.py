from django.urls import path
from . import views
from .views import register_product, register_user, add_product, order_confirmation, checkout


urlpatterns = [
    path('', views.home, name='home'),
     path('register-product/', add_product, name='register_product'),
     path('register/', register_user, name='register_user'),
     path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
     path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'), 
    path('cart/', views.cart_view, name='cart_view'),
    path('checkout/', views.checkout, name='checkout'),

    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('chatbot/', views.chatbot, name='chatbot'),
    path('ia-chatbot/', views.ia_chatbot, name='ia_chatbot'),

]