from django.urls import path
from . import views

urlpatterns = [
    # set url to blank, becos its our home page
    path('', views.store, name="store"),
    # http:/localhost/cart/
    path('cart/', views.cart, name="cart"),
    # http:/localhost/checkout/
    path('checkout/', views.checkout, name="checkout"),
]
