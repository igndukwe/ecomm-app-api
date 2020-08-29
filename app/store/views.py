from django.shortcuts import render
from .models import Product, Order, OrderItem, ShippingAddress
from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
import json
import datetime
# from .utils import cookieCart, cartData, guestOrder
from .utils import cartData, guestOrder


def store(request):

    # handle the logic for loged in and unauthenticated users
    data = cartData(request)

    cartItems = data['cartItems']

    products = Product.objects.all()
    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'store/store.html', context)


def cart(request):

    # handle the logic for loged in and unauthenticated users
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)


def checkout(request):

    # handle the logic for loged in and unauthenticated users
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('Product:', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(
        customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(
        order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

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
        # or create one if it does not exist
        order, created = Order.objects.get_or_create(
            customer=customer,
            complete=False
        )
    else:
        # else anonymous users
        customer, order = guestOrder(request, data)

    # get 'total' from the 'form'
    # > 'form' is derived from the
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

    return JsonResponse('Payment submitted..', safe=False)
