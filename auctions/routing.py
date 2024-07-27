from . import consumers
from django.urls import path

websocket_urlpatterns = [
    path("ws/items/<str:pk>/",consumers.BidConsumer.as_asgi())
]