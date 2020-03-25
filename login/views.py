from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
import stripe
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Product, OrderProduct, Cart, ProductPicture
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist


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
    
    paginator = Paginator(product_list,9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    category_A = Product.objects.filter(category='A').count()
    category_T = Product.objects.filter(category='T').count()
    category_C = Product.objects.filter(category='C').count()

    context = {
        'page_obj': page_obj,
        'type': sort,
        'A' : category_A,
        'T' : category_T,
        'C' : category_C,
    }

    return render(request, 'login/products.html', context)


def post_product(request):
    if request.method == "POST":

        if request.user.is_authenticated:
            product_name = request.POST['name']
            product_price = request.POST['price']
            product_category = request.POST['category']

            if not product_name or not product_price:
                messages.warning(request, "please enter product and price")
                return redirect('post_product')

            product_picture = None
            files = request.FILES.getlist('product-pic')
            if files:
                product = Product.objects.create(
                    name=product_name, price=product_price, user=request.user, category=product_category)
                for image in files:
                    product_picture = ProductPicture.objects.create(
                        picture=image, product=product)
                return redirect('post_product')
            else:
                product = Product.objects.create(
                    name=product_name, price=product_price, user=request.user, category=product_category)
                return redirect('post_product')

                

        else:
            messages.warning(request, "please login to post products")
            return redirect('post_product')

    return render(request, 'login/post_product.html')


@login_required(login_url='/login/')
def cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user, ordered=False)
    if request.is_ajax():
        try:
            order_product_list = cart.products.order_by('-product__price')
            subtotal = 0
            id = request.GET['product_id']
            button_type = request.GET['type']
            product = OrderProduct.objects.get(pk=id)
            if button_type == 'minus':
                if product.quantity > 1 :
                    product.quantity -= 1
                    product.save()
                    print(product.product.price * -1)
                else:
                    product.delete()
            elif button_type == 'add':
                    product.quantity += 1
                    product.save()
                    print(product.product.price)

            #calculate subtotal after quantity change
            for order_product in order_product_list:
                subtotal += order_product.get_total()
            tax = subtotal * 0.13
            total = subtotal + tax

            # if product is deleted return 0
            if not OrderProduct.objects.filter(pk=id).exists():
                return JsonResponse({
                    'quantity': 0,
                    'subtotal' : subtotal,
                    'tax' : tax,
                    'total': total
                    })
            # otherwise
            else:
                return JsonResponse({
                    'quantity': product.quantity,
                    'subtotal' : subtotal,
                    'tax' : tax,
                    'total': total
                    })
        except:
            pass
    elif request.method == "GET":
        print("get")
        order_product_list = cart.products.order_by('-product__price')
        subtotal = 0
        for order_product in order_product_list:
            subtotal += order_product.get_total()
        tax = subtotal * 0.13
        total = subtotal + tax

        context = {
            'products': order_product_list,
            'subtotal': subtotal,
            'tax' : tax,
            'total' : total
        }

        return render(request, 'login/cart.html', context)

@login_required(login_url='/login/')
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    order_product, created = OrderProduct.objects.get_or_create(
        product=product, user=request.user, ordered=False)
    cart_qs = Cart.objects.filter(user=request.user,ordered=False)
    if cart_qs.exists():
        cart = cart_qs[0]
        if not created:
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
    order_product_qs = OrderProduct.objects.filter(
        product=product, user=request.user, ordered=False)
    if order_product_qs.exists():
        order_product = order_product_qs[0]
        if order_product.quantity > 1:
            order_product.quantity -= 1
            order_product.save()
            return redirect("cart")
        else:
            order_product.delete()
            return redirect("cart")
    else:
        return redirect("products")


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
        return render(request, 'login/product_detail-new.html', context)
    else:
        return render(request, 'login/product_detail-new.html', {'product': product})


def checkout(request):
    try:
        cart = Cart.objects.get(user=request.user,ordered=False)
        total_bill = cart.total_price()
        if total_bill == 0:
            messages.warning(request, "There is nothing in your cart!")
            return redirect('products') 

        try:
            products = cart.products.all()
            context = { 
                'products' : products, 
                'total' : total_bill
                }
            return render(request,'login/checkout.html',context)

        except:
            messages.warning(request, "There is nothing in your cart!")
            return redirect('products')
    except ObjectDoesNotExist:
        messages.warning(request, "There is nothing in your cart!")
        return redirect('products')

    return render(request, 'login/checkout.html', {})


def make_payment(request):
    if request.method == "POST":
        token = request.POST['stripeToken']

        cart = Cart.objects.get(user=request.user, ordered=False)
        price = cart.total_price() * 100
        price = int(price)
        try:
            # Use Stripe's library to make requests...
            charge = stripe.Charge.create(
            amount=price,
            currency='cad',
            description='Example charge',
            source=token,
            )
        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught

            print('Status is: %s' % e.http_status)
            print('Type is: %s' % e.error.type)
            print('Code is: %s' % e.error.code)
            # param is '' in this case
            print('Param is: %s' % e.error.param)
            print('Message is: %s' % e.error.message)
            messages.warning(request, e.error.message)
            return redirect('products')
        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            pass
        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            pass
        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            pass
        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            pass
        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            pass
        except Exception as e:
            # Something else happened, completely unrelated to Stripe
            pass

        cart.ordered = True
        cart.save()
        for product in cart.products.all():
            product.ordered = True
            product.save()

        return render(request, 'login/payment.html')
    return render(request, 'login/payment.html')


def stripe_payment(request):
    publishableKey = settings.STRIPE_PUBLISHABLE_KEY

    return render(request, 'login/stripe-payment.html', { 'publishable_key' : publishableKey})

def contact(request):
    return render(request, 'login/contact.html')

def home(request):
    return render(request, 'login/home.html')