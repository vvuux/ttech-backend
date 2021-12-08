from django.urls import path

from momo.views import MomoPaymentReturn,NotifyUrl

app_name = "momo"

urlpatterns = [
    path("payment-return/",MomoPaymentReturn.as_view(),name='momo-payment-return'),
    path("notify-url/",NotifyUrl.as_view(),name="notify-url")
]