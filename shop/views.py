from django.shortcuts import render
from store.models import Product
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import json
from orders.models import Order, Payment
from .settings import RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET
import razorpay
from orders.constants import PaymentStatus
# import hashlib
import hmac
# import base64
# import hmac_sha256

client = razorpay.Client(
    auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))


def home(request):
    products = Product.objects.all().filter(is_available=True)
    context = {
        'products' : products,
    }

    return render(request, 'home.html', context)
