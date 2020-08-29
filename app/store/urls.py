from django.urls import path
from . import views

urlpatterns = [
    # set url to blank, becos its our home page
    path('', views.store, name="store"),
    # http:/localhost/cart/
    path('cart/', views.cart, name="cart"),
    # http:/localhost/checkout/
    path('checkout/', views.checkout, name="checkout"),
    # http:/localhost/update_item/
    path('update_item/', views.updateItem, name="update_item"),
    # http:/localhost/update_item/
    path('process_order/', views.processOrder, name="process_order"),
]
