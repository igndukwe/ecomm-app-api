from django.shortcuts import render
from .models import Product, Order


# Create your views here.
def store(request):
    # query products
    products = Product.objects.all()
    # print(products)
    context = {'products': products}
    return render(
        request,
        'store/store.html',
        context
    )


def cart(request):

    if request.user.is_authenticated:
        customer = request.user.customer
        # query Order if exists otherwise create Order obj
        # >complete=False: get the open orders,
        # i.e. orders that have complete status of false
        order, created = Order.objects.get_or_create(
            customer=customer,
            complete=False
        )

        # Then get the items attached to that order
        # To query child object from parent
        # >child object must all be lower cases
        # Syntax: parent.child_function
        # e.g. OrderIdems is a child of Order
        # Hence, to get all the order items that has an order
        items = order.orderitem_set.all()
    else:
        # if user is not authenticated return an empty list
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}

    context = {'items': items, 'order': order}

    return render(
        request,
        'store/cart.html',
        context
    )


def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer,
            complete=False
        )
        items = order.orderitem_set.all()
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}

    context = {'items': items, 'order': order}

    context = {'items': items, 'order': order}
    return render(
        request,
        'store/checkout.html',
        context
    )
