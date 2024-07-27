from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import get_user_model
from auctions.models import *
from django.shortcuts import redirect
from .forms import  *
from django.contrib import messages
from django_celery_beat.models import PeriodicTask
from django_celery_results.models import TaskResult
from account.forms import *
import os
from django import template
from mimetypes import guess_type
from django.http import HttpResponse
from dateutil.relativedelta import relativedelta
from datetime import date





User = get_user_model()

# Create your views here.

def superuser_required(user):
    return user.is_superuser

@user_passes_test(superuser_required)
def main_admin(request):
    bids = Bid.objects.all().order_by('-bidded_at')
    return render(request, 'admin/main_admin.html', {'bids': bids})

@user_passes_test(superuser_required)
def create_user_admin(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_paid = True
            user.is_active = True
            user.is_verified = True
            form.save()
            messages.success(request, "Account have been created Successfully")
            return redirect('user-admin')
    else:
        form =CustomUserCreationForm()  
    
    return render(request, 'admin/user_creation_admin.html', {'form':form})


@user_passes_test(superuser_required)
def update_user_admin(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        form = UserProfileUpdateAdmin(request.POST, request.FILES,instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Account have been Updated Successfully")
            return redirect('user-admin')
    else:
        form =UserProfileUpdateAdmin(instance=user)  
    
    return render(request, 'admin/user_update_admin.html', {'form':form})


@user_passes_test(superuser_required)
def delete_user(request, pk):
    post = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        post.delete()
        messages.success(request, "User is successfully deleted")
        return redirect('user-admin')
    
@user_passes_test(superuser_required)
def delete_bid(request, pk):
    bit = get_object_or_404(Bid, id=pk)
    if request.method == 'POST':
        bit.delete()
        return redirect('main-admin')


@user_passes_test(superuser_required)
def user_admin(request):
    user = User.objects.all().order_by("is_verified")
    return render(request, 'admin/user_admin.html', {'users': user})

@user_passes_test(superuser_required)
def automated_task_admin(request):
    periodic_tasks = PeriodicTask.objects.all()
    task_results = TaskResult.objects.all()
    return render(request, 'admin/automated_task_admin.html', {'periodic_tasks': periodic_tasks, 'task_results': task_results})

@user_passes_test(superuser_required)
def delete_periodic_tasks(request, name):
    task = get_object_or_404(PeriodicTask, name=name)
    if request.method == 'POST':
        task.delete()
        return redirect('automated-task-admin')
    

@user_passes_test(superuser_required)
def delete_task_results(request, task_id):
    result = get_object_or_404(TaskResult, task_id=task_id)
    if request.method == 'POST':
        result.delete()
        return redirect('automated-task-admin')
    


# Auction Crud operations
@user_passes_test(superuser_required)
def get_auction_admin(request):
    now = timezone.now()
    auctions = Auction.objects.all().order_by('-start_at')
    return render(request, 'admin/auction_admin.html', {'auctions': auctions, "now" : now })

@user_passes_test(superuser_required)
def add_auction_admin(request):
    users = User.objects.filter(is_superuser=True)
    if request.method == 'POST':
        form = AuctionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"New Auction is added successfully")
            return redirect('auction-admin')
    else:
        form = AuctionForm()
    return render(request, 'admin/add_auction_admin.html', {'form': form, 'users': users})

# Delete auction
@user_passes_test(superuser_required)
def delete_auction(request, pk):
    auction = get_object_or_404(Auction, id=pk)
    if request.method == 'POST':
        auction.delete()
        return redirect('auction-admin')



# Vehicle Crud operations
@user_passes_test(superuser_required)
def get_vehicle_admin(request):
    items = CapturedVehicle.objects.all().order_by("created_at")
    return render(request, 'admin/vehicle_admin.html', {'items': items,})


@user_passes_test(superuser_required)
def all_vehicle_auction_admin(request,auction_pk):
    auction = get_object_or_404(Auction, pk=auction_pk)
    items = Item.objects.filter(auction=auction)
    return render(request, 'admin/all_vehicle_auction.html', {'items': items,})



@user_passes_test(superuser_required)
def add_vehicle_admin(request):
    if request.method == 'POST':
        form = ItemCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"New Item is added successfully")
            return redirect('vehicle-admin') 
        else:
            print(form.errors)
    else:
        form = ItemCreateForm()
    return render(request, 'admin/add_vehicle_admin.html', {'form': form})

@user_passes_test(superuser_required)
def add_vehicle_to_auction_admin(request,auction_pk):
    three_month_ago= date.today() - relativedelta(months=3)
    auction = get_object_or_404(Auction, pk=auction_pk)
    items= CapturedVehicle.objects.filter(captured_on__lt=three_month_ago,is_paid_charge=False,is_auctioned=False)
    if request.method == 'POST':
        form = AddVehicleToAuctionForm(request.POST, request.FILES)
        if form.is_valid():
            reverse_price=form.cleaned_data['reverse_price']
            item_pk = request.POST['item']
            item = CapturedVehicle.objects.get(pk=item_pk)
            item.is_auctioned=True
            item.save()
            primary_image= form.cleaned_data['primary_image']
            new_item=Item.objects.create(
                auction=auction,
                reverse_price=reverse_price,
                primary_image=primary_image,
                item=item,
            )
            messages.success(request,"Vehicle added to auction successfully")
            return redirect('auction-admin')
        else:
            print(form.errors)
    else:
        form = AddVehicleToAuctionForm()
    return render(request, 'admin/add_vehicle_to_auction.html', {'form': form, "items":items})


@user_passes_test(superuser_required)
def update_vehicle(request, pk):
    item = get_object_or_404(CapturedVehicle, id=pk)
    if request.method == 'POST':
        form_update = ItemUpdateForm(request.POST, instance=item)
        if form_update.is_valid():
           form_update.save()
           messages.success(request,"Item updated successfully")
           return redirect('vehicle-admin')
    return redirect('vehicle-admin')
    

        
@user_passes_test(superuser_required)
def add_vehicle_image(request, pk):
    if request.method == 'POST':
        image = request.FILES.get('image')
        item = get_object_or_404(Item,pk=pk)
        ItemImage.objects.create(
            item=item,
            image=image
        )
        messages.success(request, "Image added successfully")
    return redirect('vehicle-admin')

    
@user_passes_test(superuser_required)
def delete_vehicle(request, pk):
    vehicle = get_object_or_404(CapturedVehicle, id=pk)
    if request.method == 'POST':
        vehicle.delete()
        messages.success(request,"Vehicle data removed successfully!")
        return redirect('vehicle-admin')

@user_passes_test(superuser_required)
def remove_vehicle_auction(request, pk):
    vehicle = get_object_or_404(Item, id=pk)
    if request.method == 'POST':
        vehicle.delete()
        messages.success(request,"Vehicle data removed successfully!")
        return redirect('auction-admin')
    



@user_passes_test(superuser_required)
def specification_admin(request):
    specs = Specification.objects.all()
    return render(request, 'admin/specification_admin.html', {'specs':specs})


@user_passes_test(superuser_required)
def update_specifications_admin(request, spec_id):
    spec = get_object_or_404(Specification, id=spec_id)
    if request.method == 'POST':
        form = SpecificationUpdateForm(request.POST,instance=spec)
        if form.is_valid():
           form.save()
           messages.success(request,"Item updated successfully")
        return redirect('specification-admin')
    

# transactions
@user_passes_test(superuser_required)
def transaction_admin(request):
    transactions = Transaction.objects.all().order_by('request_approval')
    reg_tansactions = RegistrationFeeTransaction.objects.all().order_by('is_completed')
    for transaction in transactions:
        if transaction.upload_bank_slip:
            transaction.upload_bank_slip = os.path.join(settings.MEDIA_URL, str(transaction.upload_bank_slip))
        else:
            transaction.upload_bank_slip = None
    return render(request, 'admin/transaction_admin.html', {'transactions': transactions, "reg_tansactions":reg_tansactions})


def download_bank_slip(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    if transaction.upload_bank_slip:
        file_path = transaction.upload_bank_slip.path
        if os.path.exists(file_path):
            content_type, _ = guess_type(file_path)
            if content_type is None:
                content_type = 'application/octet-stream'
            with open(file_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type=content_type)
                file_name = os.path.basename(file_path)
                response['Content-Disposition'] = f'attachment; filename="{file_name}"'
                return response
        else:
            return HttpResponse("Bank slip not found.", status=404)
    else:
        return HttpResponse("Bank slip not found.")
    

@user_passes_test(superuser_required)
def approve_payement(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    if request.method == "POST":
        transaction.request_approval =True
        transaction.save()
        Invoice.objects.create(
            transaction=transaction,
        )
        Notification.objects.create(
            user=transaction.user,
            message="""The payment transaction has been approved. 
            You have the invoice and certificate of sale in your store already. \n
            You can now come and pick your vehicle not more than 3 days. \n
            Don't forget to come with this invoice, certificate of sale and national id
            Thank you!
            """  
        )
        messages.success(request,"The Transaction has been approved")
        return redirect("transaction-admin")