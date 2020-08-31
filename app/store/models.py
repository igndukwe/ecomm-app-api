import uuid
import os
from django.db import models
from django.contrib.auth.models import User


def product_image_file_path(instance, filename):
    """Generate file path for new recipe image"""
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'

    # path to store the file
    return os.path.join('uploads/product/', filename)


# Create your models here.
class Customer(models.Model):

    # once Customer is deleted
    # let User be deleted as well
    user = models.OneToOneField(
        User,
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    digital = models.BooleanField(default=False, null=True, blank=True)
    image = models.ImageField(
        null=True,
        blank=True,
        upload_to=product_image_file_path
    )

    def __str__(self):
        return self.name

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except Exception:
            url = ''
        return url


class Order(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100, null=True)

    def __str__(self):
        return str(self.id)

    @property
    def get_cart_total(self):
        """Total amount of ordered items in cart"""

        # Total is a product of price and quantity
        # >OrderItem is a Child of Order
        # Syntax: Parent.child_set.all()
        # remember that child must be lower cases
        # e.g. call from inside inside class/method:
        # self.orderitem_set.all()
        # call from outside the class:
        # Order.orderitem_set.all()
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def get_cart_items(self):
        """Total quantity of ordered items in cart"""

        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total

    @property
    def shipping(self):
        shipping = False
        orderitems = self.orderitem_set.all()
        for i in orderitems:
            if i.product.digital is False:
                shipping = True
        return shipping


class OrderItem(models.Model):
    # on deleting OrderItem, do not delete products or orders
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    @property
    def get_total(self):
        """Total of a particular item"""

        # Total is a product of price and quantity
        total = self.product.price * self.quantity
        return total


class ShippingAddress(models.Model):
    # want customers info even if order gets deleted
    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True
    )
    address = models.CharField(max_length=200, null=False)
    city = models.CharField(max_length=200, null=False)
    state = models.CharField(max_length=200, null=False)
    zipcode = models.CharField(max_length=200, null=False)
    country = models.CharField(max_length=200, null=False)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address
