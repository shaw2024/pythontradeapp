from django.urls import path
from . import views

app_name = "trader"

urlpatterns = [
    path("", views.index, name="index"),
    path("trade/", views.trade_action, name="trade"),
    path("reset/", views.reset_action, name="reset"),
]
