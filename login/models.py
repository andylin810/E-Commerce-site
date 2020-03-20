from django.db import models
from django.conf import settings
from django.utils import timezone
from django.urls import reverse


# Create your models here.

class UserAccount(models.Model):
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)


class Product(models.Model):
    CATEGORY = [
        ('A', 'Appliance'),
        ('C', 'Computer'),
        ('T', 'Toy')
    ]

    name = models.CharField(max_length=100)
    price = models.IntegerField(default=0)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    post_date = models.DateTimeField('post date:', default=timezone.now)
    category = models.CharField(choices=CATEGORY, max_length=1)

    def __str__(self):
        return self.name

    def add_to_cart_url(self):
        return reverse("add_to_cart", kwargs={
            'product_id': self.pk
        })

    def delete_product_url(self):
        return reverse("delete_product", kwargs={
            'product_id': self.pk
        })

    def delete(self, *args, **kwargs):
        for image in self.productpicture_set.all():
            image.delete()
        super().delete(*args, **kwargs)


class ProductPicture(models.Model):
    picture = models.ImageField(upload_to='product/', null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def delete(self, *args, **kwargs):
        self.picture.delete()
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.picture.name


class OrderProduct(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.product.name

    def delete_from_cart_url(self):
        return reverse("delete_from_cart", kwargs={
            'product_name': self.product.name
        })

    def get_total(self):
        return self.quantity * self.product.price


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    products = models.ManyToManyField(OrderProduct)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    def total_price(self):
        total = 0
        for item in self.products.all():
            total += item.get_total()
        tax = total * 0.13
        total += tax
        return total
