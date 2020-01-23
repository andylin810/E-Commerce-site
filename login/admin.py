from django.contrib import admin
from .models import UserAccount, Product, OrderProduct, Cart, ProductPicture

# Register your models here.
admin.site.register(UserAccount)
admin.site.register(Product)
admin.site.register(OrderProduct)
admin.site.register(Cart)
admin.site.register(ProductPicture)
