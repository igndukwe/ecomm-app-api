from django.shortcuts import render
from .models import Product, Order, OrderItem, ShippingAddress
from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
import json
import datetime


# Create your views here.
def store(request):

    # calculates total items ordered in the cart icon
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer,
            complete=False
        )
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        # if user is not authenticated return an empty list
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
        cartItems = order['get_cart_items']

    # query products
    products = Product.objects.all()
    # print(products)
    context = {'items': items, 'products': products, 'cartItems': cartItems}
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
        cartItems = order.get_cart_items
    else:
        # if user is not authenticated return an empty list
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}
        cartItems = order['get_cart_items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}

    return render(
        request,
        'store/cart.html',
        context
    )


# @csrf_exempt
def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer,
            complete=False
        )
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}
        cartItems = order['get_cart_items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}

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


def processOrder(request):
    # timestamp
    transaction_id = datetime.datetime.now().timestamp()

    # request body comes from the js in the checkout.htm
    data = json.loads(request.body)

    # check if user is loged in
    if request.user.is_authenticated:

        # get the user customer from the request
        customer = request.user.customer

    # get the order of this customer with txn not completed
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)

    # 'form' is derived from the
    # body: JSON.stringify({ 'form': userFormData, ...})
    # javaScript code in the checkout.html
    # and 'total' is a value of the 'form' fied
        total = float(data['form']['total'])

    # time the transaction was made
        order.transaction_id = transaction_id

    # set txn to complete
        if total == order.get_cart_total:
            order.complete = True

    # save order in the database
        order.save()

    # if customer needs shipping
        if order.shipping is True:
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                # these values are derived from the
                # body: JSON.stringify({ ..., 'shipping': shippingInfo})
                # javaScript code in the checkout.html
                address=data['shipping']['address'],
                city=data['shipping']['city'],
                state=data['shipping']['state'],
                zipcode=data['shipping']['zipcode'],
            )
    else:
        print('User is not logged in')

    return JsonResponse('Payment submitted..', safe=False)
