from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Product, Order, OrderItem, ShippingAddress
from django.http import JsonResponse
from django.conf import settings
from .utils import cartData, guestOrder
from django.views.decorators.http import require_http_methods

import json
import datetime
import stripe


stripe.api_key = settings.STRIPE_PRIVATE_KEY


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


# @ csrf_exempt
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


@require_http_methods(["POST", ])
def charge(request):

    # timestamp
    transaction_id = datetime.datetime.now().timestamp()

    # request body comes from the js in the checkout.htm
    data = {
        'name': request.POST['name'],
        'email': request.POST['email'],
    }

    customer = None

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
    # total = int(float(request.POST['total']))
    total = int(float(request.POST['total']))

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
            address=request.POST['address'],
            city=request.POST['city'],
            state=request.POST['state'],
            zipcode=request.POST['zipcode'],
            country=request.POST['country'],
        )

    # create Stripe Customer
    customer = stripe.Customer.create(
        email=customer.email,
        name=customer.name,
        source=request.POST['stripeToken']
    )

    # charge Stripe Customer
    # charge = stripe.Charge(
    # amount=total*100,
    stripe.Charge.create(
        customer=customer,
        amount=total*100,
        currency='nzd',
        description='Payment...'
    )

    # set cookie
    # response = render(request, 'store/checkout.html')
    response = redirect(reverse('store'))
    response.delete_cookie('cart')
    # response.set_cookie('cart', request.COOKIES)
    # response.set_cookie(
    #    key=cookie.name,
    #    value=cookie.value,
    #    domain=cookie.domain,
    #    path=cookie.path,
    #    expires=cookie.expires
    # )

    return response
    # return redirect(reverse('store'), response)
