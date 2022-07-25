from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product
from carts.models import Cart, CartItem
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

# Create your views here.

def _cart_id(request):# _cart_id this is a just a private function. coding standard
    cart = request.session.session_key
    if not cart:
        request.session.create()
        cart = request.session.session_key
    return cart    


def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id) # This will get the product

    if current_user.is_authenticated:
        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
        
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, user=current_user)
            if product in cart_item:
                product.quantity +=1
        
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request)) # Get the cart using the cart id
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
        cart.save()

        try:
            cart_item = CartItem.objects.get(product=product, cart=cart)
            cart_item.quantity += 1 # cart item quantity incrementation
            cart_item.save()
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                cart = cart,
            )
            cart_item.save()

            is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
            if is_cart_item_exists:
                cart_item = CartItem.objects.filter(product=product, cart=cart)
    
    return redirect('cart')


def cart(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total)/100 
        grand_total = total + tax 
    except ObjectDoesNotExist:
        pass # just ignore

    context = {
        'total'         : total,
        'quantity'      : quantity,
        'cart_items'    : cart_items,
        'tax'           : tax,
        'grand_total'   : grand_total,
    }
    return render(request, 'store/cart.html', context)

def remove_cart(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart') 

def remove_cart_item(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    return redirect('cart')


@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total)/100 
        grand_total = total + tax 
    except ObjectDoesNotExist:
        pass # just ignore

    context = {
        'total'         : total,
        'quantity'      : quantity,
        'cart_items'    : cart_items,
        'tax'           : tax,
        'grand_total'   : grand_total,
    }
    return render(request, 'store/checkout.html', context)