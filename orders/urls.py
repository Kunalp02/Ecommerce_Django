from django.urls import path
from .import views


urlpatterns = [
    path('place_order/', views.place_order, name="place_order"),
    path('payments/', views.payments, name="payments"),
    path('razorpay/callback/', views.callback, name="callback"),
    path('order_complete/', views.payments, name = 'order_complete')
]
