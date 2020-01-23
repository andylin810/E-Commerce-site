from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
import stripe
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Product, OrderProduct, Cart, ProductPicture
from django.core.files.storage import FileSystemStorage


# Create your views here.
stripe.api_key = settings.STRIPE_SECRET_KEY


def loginpage(request):
    return render(request, 'login/userlogin.html')


def loggedpage(request):
    username = request.POST['username']
    password = request.POST['password']
    context = {
        'username': username,
        'password': password,
    }
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        return render(request, 'login/products.html', context)
    else:
        return render(request, 'login/loginfailed.html', context)


def productlist(request):
    product_list = Product.objects.order_by('-post_date')
    sort = 'date'
    if request.GET.get('sort') == 'price':
        sort = 'price'
        product_list = Product.objects.order_by('price')
    elif request.GET.get('sort') == 'date':
        sort = 'date'
        product_list = Product.objects.order_by('-post_date')
    elif request.GET.get('search') is not None:
        term = request.GET['search']
        product_list = Product.objects.filter(name__contains=term)

    context = {
        'products': product_list,
        'type': sort,
    }

    return render(request, 'login/products.html', context)


def post_product(request):
    print(stripe)

    if request.method == "POST":

        if request.user.is_authenticated:
            product_name = request.POST['name']
            product_price = request.POST['price']

            if not product_name or not product_price:
                messages.warning(request, "please enter product and price")
                return redirect('post_product')

            product_picture = None
            files = request.FILES.getlist('product-pic')
            if files:
                product = Product.objects.create(
                    name=product_name, price=product_price, user=request.user)
                for image in files:
                    product_picture = ProductPicture.objects.create(
                        picture=image, product=product)
                return redirect('post_product')

        else:
            messages.warning(request, "please login to post products")
            return redirect('post_product')

    return render(request, 'login/post_product.html')


@login_required(login_url='/login/')
def cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    order_product_list = cart.products.order_by('-product__price')
    total = 0
    for order_product in order_product_list:
        total += order_product.product.price * order_product.quantity

    context = {
        'products': order_product_list,
        'total': total,
    }

    return render(request, 'login/cart.html', context)


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    order_product, created = OrderProduct.objects.get_or_create(
        product=product, user=request.user)
    cart_qs = Cart.objects.filter(user=request.user)
    if cart_qs.exists():
        cart = cart_qs[0]
        if cart.products.filter(product__name=product.name).exists():
            order_product.quantity += 1
            order_product.save()
        else:
            cart.products.add(order_product)
        return redirect("cart")
    else:
        cart = Cart.objects.create(user=request.user)
        cart.products.add(order_product)
        return redirect("cart")


def delete_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    return redirect('products')


def delete_from_cart(request, product_name):
    product = get_object_or_404(Product, name=product_name)
    order_product = OrderProduct.objects.get(
        product=product, user=request.user)
    cart = Cart.objects.get(user=request.user)
    if order_product.quantity > 1:
        order_product.quantity -= 1
        order_product.save()
        return redirect("cart")
    else:
        order_product.delete()
        return redirect("cart")


def register(request):

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('products')
    else:
        form = UserCreationForm()
    return render(request, 'login/register.html', {'form': form})


def log_out(request):

    logout(request)
    return redirect('login')


def productdetail(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    main_picture = product.productpicture_set.first()
    if main_picture:
        rest_picture = product.productpicture_set.exclude(
            picture=main_picture.picture)
        count = range(1, rest_picture.count()+1)
        context = {
            'product': product,
            'main_picture': main_picture,
            'rest_picture': rest_picture,
            'count': count
        }
        return render(request, 'login/product_detail.html', context)
    else:
        return render(request, 'login/product_detail.html', {'product': product})


def checkout(request):
    return render(request, 'login/checkout.html', {})


def payment(request):
    publishableKey = settings.STRIPE_PUBLISHABLE_KEY
    if request.method == "POST":
        token = request.POST['stripeToken']
        charge = stripe.Charge.create(
            amount=999,
            currency='cad',
            description='Example charge',
            source=token,
        )
        
        return render(request, 'login/payment.html', { 'publishable_key' : publishableKey})
    return render(request, 'login/payment.html', { 'publishable_key' : publishableKey})
