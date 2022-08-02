from django.shortcuts import render
from store.models import Product
from django.views.decorators.csrf import csrf_exempt
import json
from orders.models import Order
from .settings import RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET
import razorpay
from orders.constants import PaymentStatus


def home(request):
    products = Product.objects.all().filter(is_available=True)
    context = {
        'products' : products,
    }

    return render(request, 'home.html', context)



@csrf_exempt
def callback(request):
    def verify_signature(response_data):
        client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
        print('If')
        return client.utility.verify_payment_signature(response_data)

    if "razorpay_signature" in request.POST:
        print('In if')
        payment_id = request.POST.get("razorpay_payment_id", "")
        provider_order_id = request.POST.get("razorpay_order_id", "")
        signature_id = request.POST.get("razorpay_signature", "")
        print(payment_id)
        print(provider_order_id)
        print(signature_id)
        order = Order.objects.get(order_number=provider_order_id)
        print(order)
        order.payment_id = payment_id
        order.signature_id = signature_id
        order.save()
        if verify_signature(request.POST):
            order.status = PaymentStatus.SUCCESS
            order.save()
            return render(request, "orders/callback.html", context={"status": order.status})
        else:
            order.status = PaymentStatus.FAILURE
            order.save()
            return render(request, "orders/callback.html", context={"status": order.status})
    else:
        payment_id = json.loads(request.POST.get("error[metadata]")).get("payment_id")
        print(payment_id)
        order_number = json.loads(request.POST.get("error[metadata]")).get("order_id")  
        print(order_number)    
        description = request.POST.get("error[description]")
        reason = request.POST.get("error[reason]")
        print(description)
        print(reason)
        order = Order.objects.get(order_number=order_number)
        order.payment_id = payment_id
        order.status = PaymentStatus.FAILURE
        order.save()
        context = {
            'status' : order.status,
            'description' : description,
            'reason' : reason,
        }
        return render(request, "orders/callback.html", context)
