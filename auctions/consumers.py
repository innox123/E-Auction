import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import *
from channels.db import database_sync_to_async


class BidConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.item_id = self.scope["url_route"]["kwargs"]["pk"]
        self.room_group_name = f"bidder_{self.item_id}"

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )

        await self.accept()

    async def disconnect(self, close):
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        bidded_amount = text_data_json["amount"]
        item = await database_sync_to_async(Item.objects.get)(id=self.item_id)

        if item.is_sold:
            # Auction has ended, send an error message
            await self.send(text_data=json.dumps({
                "error": "Auction has been closed!"
            }))
            return
        
        item_bids = Bid.objects.filter(item__id=self.item_id)
        current_highest_bid = await database_sync_to_async(item_bids.order_by('-amount').first)() 

        if current_highest_bid:
            highest_amount = current_highest_bid.amount
        else:
            highest_amount = item.reverse_price
        
        new_amount = int(highest_amount) + int(bidded_amount)

        bid_update = await database_sync_to_async(Bid.objects.create)(
                user=self.user,
                item=item,
                amount= new_amount
                )
        await database_sync_to_async(Notification.objects.create)(
            user=self.user,
            message=f"You bid {bidded_amount} RWF The value become {bid_update.amount} RWF Thank you!"
        )
        number_of_bids = await database_sync_to_async(Bid.objects.filter(item=item).count)()

        # Send message to room group
        await self.channel_layer.group_send(    
            self.room_group_name, {
                "type": "bidding.message",
                "bid_amount": bidded_amount,
                "bidder": self.user.username,
                "number_of_bids": number_of_bids,
                "current_amount": bid_update.amount,
            }
        )


    # Receive message from room group
    async def bidding_message(self, event):
        bid_amount = event["bid_amount"]
        bidder = event['bidder']
        number_of_bids=event["number_of_bids"]
        current_amount=event["current_amount"]


        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "bid_amount": bid_amount,
            "bidder": bidder,
            "number_of_bids": number_of_bids,
            "current_amount":current_amount
        }))
