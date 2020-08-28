from django.shortcuts import render
from .models import Product, Order, OrderItem
from django.http import JsonResponse
import json


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


def updateItem(request):

    # get the body from cart.js
    # which is a JSON data
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('Product:', productId)

    # get the logged in customer
    customer = request.user.customer

    # get the product from database by id
    # the id number comes from the cart.js
    product = Product.objects.get(id=productId)

    # get the orders attached to that customer
    # that has a complete value of false
    order, created = Order.objects.get_or_create(
        customer=customer,
        complete=False
    )

    # The reason why we use get_or_create
    # is that want to change the value
    # of the OrderItem if it already exists
    # e.g. if OrderItem already exists
    # according to the Product and Order
    # we do not want to create a new one
    # we simply want to change the quantity
    # > by adding or subtracting quantities
    orderItem, created = OrderItem.objects.get_or_create(
        order=order,
        product=product
    )

    # check if action is add
    # then perform an addition
    # otherwise perform a subtraction
    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    # save in the database
    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)
