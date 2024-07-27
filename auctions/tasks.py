from celery import shared_task
from auctions.models import  *


@shared_task
def end_auction_task(instance_id):
    items = Item.objects.filter(auction__id=instance_id)
    if items:
        for item in items:
            item.is_sold = True
            item.save()
            item_bids = Bid.objects.filter(item=item)
            current_highest_bid = item_bids.order_by('-amount').first()
            if current_highest_bid:
                Transaction.objects.create(
                    user=current_highest_bid.user,
                    item=item,
                    amount=current_highest_bid.amount
                )
                Notification.objects.create(
                    user=current_highest_bid.user,
                    message=f"You Won This vehicle at {current_highest_bid.amount} RWF  So complete payment in 1 day. "
                )
            else:
                item.is_sold=False
                item.save()
                
        return "Activity is completed"
    else:
        return "No Item Found"

