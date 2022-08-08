from django.shortcuts import render, redirect
from .import views
# Create your views here.
# from django.http import HttpResponse
from carts.models import CartItem
from .forms import OrderForm
import datetime
from .models import Order
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json


def payments(request):
    return render(request, 'orders/payments.html')


def place_order(request, total = 0, quantity = 0): # order_payment
    current_user = request.user 
    print(current_user)   
    #if cart items less than zero or equal to zero, then redirect back to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()

    if cart_count <= 0:
        return redirect('store')
    
    grand_total = 0
    tax = 0

    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total)/100 
    grand_total = total + tax 


    if request.method == 'POST':
        form = OrderForm(request.POST)
        print(form.errors)
        if form.is_valid(): 
            data = Order()
            data.user = current_user  
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.tax = tax
            data.order_total = grand_total

            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            # Generate order number

            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d") #20210305
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            razorpay_order = client.order.create(
                {"amount": int(grand_total) * 100, "currency": "INR", "payment_capture": "0"}
            )
            # order = Order.objects.create(
            #     name=name, amount=amount, provider_order_id=razorpay_order["id"]
            # )
            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            order.razorpay_order_id = razorpay_order["id"]
            order.save()
            return render(
                request,
                "orders/payments.html",
                {
                    "callback_url": "http://" + "127.0.0.1:8000" + "/razorpay/callback/",
                    "razorpay_key": settings.RAZORPAY_KEY_ID,
                    "order": order,
                    'cart_items' : cart_items,
                    'total' : total,
                    'tax' : tax,
                    'grand_total' : grand_total, 
                    'amount' : grand_total * 100,
                    'order_id' : razorpay_order["id"],
                },
            )

    else:
        return render(request, 'checkout.html')

def order_complete(request):
    return render(request, 'orders/order_complete.html')



