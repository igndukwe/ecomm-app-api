import json
from .models import Customer, Product, Order, OrderItem


def cookieCart(request):

    # Create empty cart for now for non-logged in user
    try:
        # and json.loads() converts it into a python dict
        cart = json.loads(request.COOKIES['cart'])
    except Exception:
        # set cart to an empty dict
        # if it is the first time to the page
        cart = {}
        print('cart:', cart)

    items = []
    order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
    cartItems = order['get_cart_items']

    # iterate through cart items from cookies
    # e.g. {"4":{"quantity":2},"5":{"quantity":1}}}
    # in the for loop i represents the product.ids "4" and "5"
    # while the "quantity" for the 1st is "2" and "1" for 2nd
    for i in cart:
        # We use try block to prevent items in cart that may
        # have been removed from causing error
        try:
            cartItems += cart[i]['quantity']

            # query product from database by id
            product = Product.objects.get(id=i)

            # total is product.price times quantity
            total = (product.price * cart[i]['quantity'])

            # aum up the total amount
            order['get_cart_total'] += total

            # aum up the total quantitiy
            order['get_cart_items'] += cart[i]['quantity']

            # build out a dict in a json format
            item = {
                'id': product.id,
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'imageURL': product.imageURL
                },
                'quantity': cart[i]['quantity'],
                'digital': product.digital,
                'get_total': total,
            }

            items.append(item)

            # if it is a digital product shipping is required
            if product.digital is False:
                order['shipping'] = True
        except Exception:
            # when user is not logged in and saves a product
            # and product is deleted in database
            # but still exists in the cookies
            pass

    return {'cartItems': cartItems, 'order': order, 'items': items}


def cartData(request):

    # check if user is loged in
    if request.user.is_authenticated:

        # get the user customer from the request
        customer = request.user.customer

        # get the order of this customer with txn not completed
        order, created = Order.objects.get_or_create(
            customer=customer,
            complete=False
        )

        # Get the ordered items attached to that order
        # Order is the parent and OrderItems is the child
        # i.e. OrderItems has a Forigh key that links to Order
        # > To query child object from parent
        # > the child object must all be lower cases
        # Syntax: parent.child_function
        # Hence, to get all the order items of a particular order
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        # if user is not authenticated
        # get values from cookies
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']

    return {'cartItems': cartItems, 'order': order, 'items': items}


def guestOrder(request, data):

    # get 'name' and 'email' from 'form'
    # > 'form' is derived from the
    # body: JSON.stringify({ 'form': userFormData, ...})
    # javaScript code in the checkout.html
    # and 'total' is a value of the 'form' fied
    name = data['name']
    email = data['email']

    # invoke the mtd that fetches data from cookies
    # rather than the database for the guest uses
    cookieData = cookieCart(request)

    # get items from cookieCartin and its in form of a dic
    items = cookieData['items']

    # if we have a guest user
    # create a customer guest user
    # if email does not exist
    # otherwise attach user to that email adderess
    # this prevents always creating a new user
    # everytime we have a guest user
    customer, created = Customer.objects.get_or_create(
        email=email,
    )

    # set guest users name value
    # should they decide to change thier name
    customer.name = name

    # save in the database
    customer.save()

    # create an order for that customer
    # with order status set to not complete
    order = Order.objects.create(
        customer=customer,
        complete=False,
    )

    # travers the list of dic from cookies
    for item in items:
        # Remember from the Model
        # OrderItem is always attached to Order and Product
        # because OrderItem has a FK that links Order and Product
        product = Product.objects.get(id=item['id'])

        # attach product and order to order item
        # also put the quantity
        # orderItem = OrderItem.objects.create(
        OrderItem.objects.create(
            product=product,
            order=order,
            quantity=item['quantity'],
        )

    # return customer and order
    return customer, order
