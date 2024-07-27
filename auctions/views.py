from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from .models import *
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import OuterRef, Subquery
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
# from xhtml2pdf import pisa
from django.db.models import Count




def get_home_view(request):
    now =timezone.now()
    auctions = Auction.objects.annotate(num_items=Count('item')).order_by("end_at")
    context = {"auctions": auctions, "now" :now}
    return render(request, "auctions/homepage.html", context)


def get_all_items(request, auction_id):
    current_time = timezone.now()    
    latest_bids_subquery = Bid.objects.filter(item=OuterRef('pk')).order_by("-bidded_at")
    latest_bid_amount_subquery = latest_bids_subquery.values('amount')[:1]

    # Query to get all items with their latest bid amount (or None if no bids exist)
    items_with_latest_bid = Item.objects.filter(auction__id=auction_id, auction__end_at__gt=current_time, is_sold=False).annotate(latest_bid_amount=Subquery(latest_bid_amount_subquery))
    
    # Fetch specifications for each item
    item_specifications = Specification.objects.filter(item_id__in=items_with_latest_bid.values_list('id', flat=True))
    
    # Fetch images for each item
    item_images = ItemImage.objects.filter(item__in=items_with_latest_bid)
    
    # Create dictionaries to map item ids to their specifications and images
    item_specifications_dict = {spec.item_id: spec for spec in item_specifications}
    item_images_dict = {img.item_id: img for img in item_images}
    
    # Add specifications and images to each item in the queryset
    for item in items_with_latest_bid:
        item.specification = item_specifications_dict.get(item.id)
        item.image = item_images_dict.get(item.id)

    number_of_items = items_with_latest_bid.count()
    context = {
        "items": items_with_latest_bid,
        "current_time" : current_time,
        "number_of_items": number_of_items
    }
    return render(request, "auctions/items.html", context)




def item_details_view(request, pk):
    item = get_object_or_404(Item, id=pk)
    bids = Bid.objects.filter(item=item).order_by('-amount')
    all_bids = Bid.objects.filter(item=item).order_by('amount')
    highest_bid = bids.first() if bids else None
    item_specification = Specification.objects.get(item=item)
    number_of_bids = Bid.objects.filter(item=item).count()
    uploaded_images = ItemImage.objects.filter(item=item)
    current_time = timezone.now()
    condition_to_bid = request.user.is_authenticated and item.auction.start_at < current_time and item.auction.end_at > current_time and request.user.is_verified
    context = {
        'item': item,
        'uploaded_images': uploaded_images,
        'bids':all_bids,
        'bid': highest_bid,
        "item_specification": item_specification,
        "number_of_bids":number_of_bids,
        "condition_to_bid":condition_to_bid
    }
    return render(request, 'auctions/item_detail.html', context)




@login_required
def get_watchlist(request):
    # Retrieve all watchlists associated with the logged-in user
    watchlists = Watchlist.objects.filter(user=request.user)

    # Initialize lists to store items with bids and items without bids
    items_with_bids = []
    items_without_bids = []

    # Iterate through each watchlist and retrieve its items
    for watchlist in watchlists:
        for item in watchlist.items.all():
            # Retrieve the latest bid for each item, if any
            latest_bid = Bid.objects.filter(item=item).order_by('-bidded_at').first()
            if latest_bid:
                items_with_bids.append({'item': item, 'bid_amount': latest_bid.amount})
            else:
                items_without_bids.append(item)

    return render(request, "users/watchlist.html", {'items_with_bids': items_with_bids, 'items_without_bids': items_without_bids})





@login_required
def remove_item_from_watchlist(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    watchlist = Watchlist.objects.filter(user=request.user).first()

    if watchlist and watchlist.items.filter(pk=item_id).exists():
        watchlist.items.remove(item)
        messages.success(request, f"{item.name} has been removed from your watchlist.")
    else:
        messages.error(request, "The item could not be removed from your watchlist.")

    return redirect('watchlist')


@login_required
def create_watchlist(request):
    if request.method == 'POST':
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            item_id = request.POST.get('item_id')
            if item_id:
                item = get_object_or_404(Item, pk=item_id)
                watchlist, created = Watchlist.objects.get_or_create(user=request.user)
                if item in watchlist.items.all():
                    return JsonResponse({'success': False, 'message': f'{item.item.vehicle_name} Is Already in your Wishstore.'})
                else:
                    watchlist.items.add(item)
                    return JsonResponse({'success': True, 'message': f'{item.item.vehicle_name} added on your wishbox keep track. '})
        else:
            return redirect('home')
    return redirect('home')



@csrf_exempt
def ussd_service(request):
    if request.method == 'POST':
        session_id = request.POST.get('sessionId')
        service_code = request.POST.get('serviceCode')
        phone_number = request.POST.get('phoneNumber')
        text = request.POST.get('text')
        response = ""
        
        if text == "":
            response = "CON Rwanda National Police Online Auction. \n"
            response += "1. English \n"
            response += "2. Kinyarwanda  \n"

        elif text =="1":
            response = "CON Select Service. \n"
            response += "1. Auctions \n"
            response += "2. Account Details \n"  
            response += "3. Pending Requests \n"
            response += "4. Incomplete Transaction \n"
            response += "5. Support \n"
        
        elif text =="2":
            response = "CON Hitamo Serivise. \n"
            response += "1. Cyamunara \n"
            response += "2. Konte Yawe \n"  
            response += "3. Ibyemezo Bitarangiye \n"
            response += "4. Igura ritarangiye \n"
            response += "5. Ubufasha \n"

        elif text == "1*1":
            response = "CON list of Auctions \n"
            now = timezone.now()
            auctions = Auction.objects.filter(end_at__gt=now)
            if auctions:
                for index, auction in enumerate(auctions, start=1):
                    response += f"({index}) {auction.start_at.date()} {auction.start_at.strftime('%I:%M%p')} close at {auction.end_at.strftime('%I:%M%p')}  \n"
            else:
                response += "No Available Auction"

        elif text == "1*2":
            response = "CON Account Details \n"
            user = User.objects.filter(phone_number__exact=phone_number).first()
            if user:
                response += f" (1) {user.first_name} {user.last_name}  \n"
                response += f" (2)  {user.phone_number}  \n"
                response += f" (3)  {user.email}  \n"
                response += f" (4)  {user.address}  \n"
                response += f" (5) Activated : {user.is_active}  \n"
                response += f" (6) Verified: {user.is_verified}  \n"
            else:
                response += "You're Not registered."

        elif text == "1*3":
            response = "CON Pending Requests \n"
            trans = Transaction.objects.filter(user__phone_number__exact=phone_number,is_completed=True,request_approval=False)
            if trans:
                for index, tran in enumerate(trans, start=1):
                    response += f"({index}) Payment of {tran.item.name} amount {tran.amount} RWF will be approved in 3 days.  \n"
            else:
                response += "No Pending Request"

        elif text == "1*4":
            response = "CON Incomplete Transactions \n"
            trans = Transaction.objects.filter(user__phone_number__exact=phone_number,is_completed=False)
            if trans:
                for index, tran in enumerate(trans, start=1):
                    response += f"({index}) {tran.item.name} {tran.amount} RWF  \n"
            else:
                response += "No Incomplete Transaction"

        elif text == "1*5":
            response = "CON Support Services \n"
            response += "No Free 112"
            response += "info@police.gov.rw"
            response += "+250 788 311 155"

        return HttpResponse(response)
    

@login_required
def generate_invoice(request, invoice_id):
    # invoice =  get_object_or_404(Invoice, pk=invoice_id)
    # html_string = render_to_string('users/invoice_template.html', {'invoice': invoice})
    # response = HttpResponse(content_type='application/pdf')
    # response['Content-Disposition'] = 'filename="invoice.pdf"'
    
    # pisa_status = pisa.CreatePDF(html_string, dest=response)
    
    # if pisa_status.err:
    #     return HttpResponse('PDF generation error')
    
    return response


def success_payment(request, transaction_id):
    reg_transaction = get_object_or_404(RegistrationFeeTransaction, id= transaction_id)
    user = User.objects.get(pk=reg_transaction.user.pk)
    if user:
        user.is_paid = True
        user.is_verified =True
        reg_transaction.is_completed =True
        user.save()
        reg_transaction.save()
        Notification.objects.create(
            user=user,
            message ="Your account has been verified. Now you can start to bid to become a winner"
                                    
                                    )
    return render(request, "users/success.html")


