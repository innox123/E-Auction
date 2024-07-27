from django.urls import path
from .views import *

urlpatterns = [
    path('', get_home_view, name='home'),
    path('items/<str:auction_id>', get_all_items, name="all-items"),
    path('items/<str:pk>/', item_details_view, name='item-detail'),
    path('create-watchlist/', create_watchlist, name='create-watchlist'),
    path('account/watchlist/', get_watchlist, name='watchlist'),
    path('watchlist/remove/<str:item_id>/', remove_item_from_watchlist, name='remove_item_from_watchlist'),
    path('ussd/', ussd_service, name='ussd_service'),
    path('invoice/<str:invoice_id>', generate_invoice, name='generate_invoice'),
    path('success/<transaction_id>/', success_payment, name='success_payment'),
]