from .models import *
from account.models import *
from django.db.models import Sum

def user_bid_count(request):
    if request.user.is_authenticated:
        bid_count = Bid.objects.filter(user=request.user).count()
    else:
        bid_count = 0
    return {'user_bid_count': bid_count}

def user_notification_count(request):
    if request.user.is_authenticated:
        not_count = Notification.objects.filter(user=request.user).count()
    else:
        not_count = 0
    return {'user_notif_count': not_count}


def user_watchlist_count(request):
    if request.user.is_authenticated:
        watch_count = Watchlist.objects.filter(user=request.user).count()
        users_count = User.objects.filter(is_superuser__exact=False).count()
        inactive_users_count = User.objects.filter(is_superuser__exact=False,is_active=False).count()
        verified_users_count = User.objects.filter(is_superuser__exact=False,is_verified=True).count()
        invoice_count = Invoice.objects.filter(transaction__is_completed__exact=True).count()
        transaction = Transaction.objects.filter(request_approval__exact=True)
        un_approved_transaction = Transaction.objects.filter(is_completed=True,
                                                            request_approval__exact=False).count()
        total_amount = transaction.aggregate(total=Sum('amount'))['total']
        vehicles_count = CapturedVehicle.objects.all().count()
        sold_vehicles_count = Item.objects.filter(is_sold=True).count()

    
    else:
        watch_count = 0
        vehicles_count=0
        invoice_count=0
        users_count = 0
        total_amount=0
        un_approved_transaction=0
        inactive_users_count=0
        verified_users_count =0
        sold_vehicles_count=0
    return {'watch_count': watch_count,
            "un_approved_transaction":un_approved_transaction,
            "sold_vehicles_count": sold_vehicles_count,
            "verified_users_count":verified_users_count ,
            "inactive_users_count":inactive_users_count,
            'users_count': users_count, 'vehicles_count': vehicles_count, 
            'invoice_count': invoice_count, 'total_amount':total_amount}