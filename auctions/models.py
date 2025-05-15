from django.utils import timezone
from django.db import models
from django.conf import settings
from account.models import User
import uuid
import datetime


class Auction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    staff = models.ForeignKey(User, on_delete=models.CASCADE)
    start_at = models.DateTimeField()
    end_at= models.DateTimeField()

    @property
    def status(self):
        now = timezone.now()
        if self.end_at < now:
            return "ended"
        else:
            return "alive"

class CapturedVehicle(models.Model):
    owner_name = models.CharField(max_length=100)
    vehicle_name = models.CharField(max_length=100)
    plate_number = models.CharField(max_length=120,unique=True)
    location = models.CharField(max_length=100,null=True, blank=True)
    is_paid_charge = models.BooleanField(default=False)
    is_auctioned = models.BooleanField(default=False)
    charged_amount= models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    captured_on= models.DateField(default=datetime.date.today)
    

class Item(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    item= models.ForeignKey(CapturedVehicle, on_delete=models.CASCADE)
    is_sold = models.BooleanField(default=False)
    reverse_price = models.IntegerField(default=0)
    primary_image = models.ImageField(upload_to='uploads/primary_images/')

    @property
    def max_price(self):
        return int((self.reverse_price * 10)/ 100)
    
    # @property
    # def min_price(self):
    #     return int(self.max_price / 3)
    
    @property
    def auction_status(self):
        now = timezone.now()
        if self.auction.start_at < now and self.auction.end_at > now:
            return "Live Bidding..."
        elif self.auction.end_at < now:
            return "Completed"
        elif self.auction.start_at > now:
            return "Not Started"
        else: 
            return "UNKNOWN"

  

class Specification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year=models.CharField(max_length=100)
    engine=models.CharField(max_length=100)
    max_torque=models.CharField(max_length=100)
    fuel_capacity=models.CharField(max_length=100)
    power = models.CharField(max_length=100)

    def __str__(self):
        return self.item.name


class Bid(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    amount = models.IntegerField(null=True, blank=True)
    bidded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.item.name


class ItemImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item = models.ForeignKey(Item, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='uploads/vehicle_images/')

    def __str__(self):
        return f"Image for {self.item.name}"


class Watchlist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(Item)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return f"{self.bidder.username}"

    

class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item = models.OneToOneField(Item, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(choices=[
            ('card', 'Credit Card'),
            ('mobile', 'Mobile Money'),
            ('receipt', 'receipt'),
        ],default="receipt",max_length=40)
    upload_bank_slip = models.FileField(upload_to='uploads/bank_slip/',blank=True, null=True)
    request_approval = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)


class Invoice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction = models.OneToOneField(Transaction,on_delete=models.CASCADE)
    issued_at = models.DateTimeField(auto_now_add=True)



class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    seen = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username



class RegistrationFeeTransaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    amount = models.IntegerField(default=5000)
    timestamp = models.DateTimeField(auto_now_add=True)
