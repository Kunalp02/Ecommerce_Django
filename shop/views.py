from django.shortcuts import render
from store.models import Product
from django.views.decorators.csrf import csrf_exempt
import json
from orders.models import Order, Payment
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
        print('1st if')
        payment_id = request.POST.get("razorpay_payment_id", "")
        provider_order_id = request.POST.get("razorpay_order_id", "")
        signature_id = request.POST.get("razorpay_signature", "")
        current_user = request.POST.get("current_user", "")
        print(current_user)
        print(payment_id)
        print(provider_order_id)
        print(signature_id)
        order = Order.objects.get(order_number=provider_order_id)
        print(order)
        payment = Payment(
            payment_id = payment_id,
            amount_paid = order.order_total,
        )
        # order.payment_id = payment_id
        order.signature_id = signature_id
        order.save()
        if verify_signature(request.POST):
            print('Signature is present')
            order.status = PaymentStatus.SUCCESS
            order.save()
            body = json.loads(request.POST)
            order = Order.objects.get(user=request.user, is_ordered=False, order_number = body["razorpay_order_id"])
            payment = Payment(
            user = request.user,
            payment_id = body['razorpay_payment_id'],
            payment_method = body['payment_method'],
            amount_paid = order.order_total,
            status = order.status,
            )
            payment.save()
            order.payment = payment
            order.is_ordered = True
            order.save()
            return render(request, "orders/callback.html", context={"status": order.status})
        else:
            order.status = PaymentStatus.FAILURE
            order.save()
            body = json.loads(request.body)
            order = Order.objects.get(user=request.user, is_ordered=False, order_number = body["razorpay_order_id"])
            payment = Payment(
            user = request.user,
            payment_id = body['razorpay_payment_id'],
            payment_method = body['payment_method'],
            amount_paid = order.order_total,
            status = order.status,
            )
            payment.save()
            order.payment = payment
            order.is_ordered = True
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
