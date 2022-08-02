from django.urls import path
from .import views


urlpatterns = [
    path('sample_payment/', views.place_order, name="sample_payment"),

]
