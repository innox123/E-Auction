import os
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.http import JsonResponse
from django.shortcuts import redirect, render,get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import View
from .forms import *
from .models import *
from auctions.models import *
from django.contrib.auth import update_session_auth_hash
from twilio.rest import Client
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .decorators import unauthenticated_user
from dotenv import load_dotenv
from django.db.models import Max
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

load_dotenv()

user_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
user_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
service_sid = os.getenv('TWILIO_SERVER_ID')

client = Client(user_account_sid, user_auth_token)



@unauthenticated_user
def get_signup_page(request):
    if request.method == 'POST':    
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            phone_number = form.cleaned_data.get('phone_number')
            user.is_active = True
            form.save()
            # request.session['user_id'] = user.id
            # request.session['phone_number'] = phone_number
            # client.verify.v2.services(service_sid).verifications.create(
            #     to=phone_number, channel="sms"
            # )
            messages.success(request, "Account have been created Successfully")
            return redirect('home')
    else:
        form =CustomUserCreationForm()
    return render(request, 'users/register.html' ,{'form':form})

def verify_code(request):
    user_id = request.session.get('user_id')
    phone_number = request.session.get('phone_number')
    if request.method == 'POST':
        entered_code = request.POST.get('verification_code')
        otp_check = client.verify.v2.services(service_sid).verification_checks.create(
            to=phone_number, code=entered_code
        )

        if otp_check.valid:
            user = User.objects.get(pk=user_id)
            user.is_active = True
            user.save()
            Notification.objects.create(
                user=user,
                message="Your account has been updated and verified.",
            )
            messages.success(request, "Your account has been updated and verified")
            return redirect('home')
            
        else:
            messages.error(request, "Invalid Code")

    return render(request, "users/verify_code.html")


class LoginView(View):
    template_name = 'users/login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me', False)
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            if not remember_me:
                request.session.set_expiry(0)
            messages.success(request, f"You logged in {user.username}'s account successfully!")
            
            if user.is_superuser:
                return redirect("main-admin")
            return redirect('/')  # Redirect to home page after successful login
        else:
            return render(request, self.template_name, {'error_message': 'Provided Credentials are invalid.'})


def logout_view(request):
    logout(request)
    messages.success(request, f'Thank you for using our system.')
    return redirect('/')




# users dashboard code

class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('home')


@login_required
def change_password(request):
    error_message = None
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            user = request.user
            old_password = form.cleaned_data['old_password']
            new_password = form.cleaned_data['new_password']
            confirm_new_password = form.cleaned_data['confirm_new_password']
            
            # Check if old password is correct
            if user.check_password(old_password):
                if new_password == confirm_new_password:
                    user.set_password(new_password)
                    user.save()
                    update_session_auth_hash(request, user)  # Update session to prevent user log out
                    messages.success(request,"Your password has been updated successfully")
                    return redirect('password_change')
                else:
                    error_message = "Passwords MisMatch."
            else:
                error_message = "Old Password is invalid."
    else:
        form = ChangePasswordForm()
    
    return render(request, 'users/change_password.html', {'form': form, 'error_message': error_message})

@login_required
def profile(request):
    if request.method == 'POST':
        form_image_update = UserUpdateProfileImageForm(request.POST, request.FILES, instance=request.user)
        form_profile_update = UserProfileUpdate(request.POST, instance=request.user)
        if "form_user_update" in request.POST:
            if form_profile_update.is_valid():
                form_profile_update.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('profile')
            else:
                messages.error(request, 'Error updating profile. Please correct the errors below.')
        elif "form_user_update_image_pofile" in request.POST:
            if form_image_update.is_valid():
                form_image_update.save()
                messages.success(request, 'Profile Image changed successfully.')
                return redirect("profile")

    else:
        # If it's a GET request, create an instance of the form with the current user's data
        form_profile_update = UserProfileUpdate(instance=request.user)
        form_image_update = UserUpdateProfileImageForm(instance=request.user)
    return render(request, "users/profile.html", {'form1': form_profile_update, 'form2': form_image_update})





@login_required
def dashboard(request):
    transactions = Transaction.objects.filter(user=request.user,request_approval=False)
    registration_transaction = RegistrationFeeTransaction.objects.filter(user=request.user,is_completed=False).first()
    number_of_complete_transactions = Transaction.objects.filter(user=request.user,is_completed = True).count()
    number_of_incomplete_transactions = Transaction.objects.all().count()
    context = {
        "number_of_transactions": number_of_incomplete_transactions,
        "transactions": transactions,
        "number_of_complete_transactions":number_of_complete_transactions,
        "registration_transaction":registration_transaction
    }
    return render(request, "users/main_user_dashboard.html", context)



@login_required
def bid_history(request):
    items = Item.objects.all().order_by('-auction__start_at')

    # Fetch the latest bid amount for each item
    latest_bid_amounts = (
        Bid.objects 
        .filter(user=request.user)
        .values('item')
        .annotate(latest_bid_amount=Max('amount'))
    )

    # Combine the data
    items_with_latest_bid = []
    now = timezone.now()
    for item in items:
        latest_bid_amount = next((bid['latest_bid_amount'] for bid in latest_bid_amounts if bid['item'] == item.pk), None)
        items_with_latest_bid.append({'item': item, 'latest_bid_amount': latest_bid_amount,'now': now})

    return render(request, "users/bid_history.html", {
       'items_with_latest_bid': items_with_latest_bid ,
    })




@login_required
def get_notification(request):
    user = request.user
    notifications = Notification.objects.filter(user=user).order_by("-timestamp")
    paginator = Paginator(notifications, 4)  # 10 notifications per page

    page = request.GET.get('page')
    try:
        notifications_page = paginator.page(page)
    except PageNotAnInteger:
        notifications_page = paginator.page(1)
    except EmptyPage:
        notifications_page = paginator.page(paginator.num_pages)

    seen_notifications = Notification.objects.filter(seen=False, user=user)
    num_notifications = len(seen_notifications)

    return render(request, "users/notifications.html", {
        "notifications_page": notifications_page,
        "num_notifications": num_notifications
    })

@login_required
def delete_notification(request, notification_id):
    notification = get_object_or_404(Notification, pk=notification_id)
    if notification.user == request.user:
        notification.delete()
        messages.success(request, "You remove notification!")
    return redirect('notification')



@login_required
def payments(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    spec = Specification.objects.filter(item=transaction.item.id).first()
    form_request_payment =  TransactionUploadSlipForm(request.POST, request.FILES)
    if request.method == "POST":
        if "form_request_approval" in request.POST:
            if form_request_payment.is_valid():
                uploaded_slip = form_request_payment.cleaned_data["upload_bank_slip"]
                transaction.upload_bank_slip =uploaded_slip
                transaction.is_completed= True
                transaction.save()
                html_content = render(request, 'users/upload_slip_success.html', {'transaction': transaction})
                return HttpResponse(html_content, content_type='text/html')
    else:
        form_request_payment =  TransactionUploadSlipForm()
    return render(request, "users/payment.html", {'transaction': transaction ,"spec":spec ,"form_request_payment": form_request_payment })


@login_required
def get_settings(request):
    return render(request, "users/settings.html")



@login_required
def store(request):
    invoice = Invoice.objects.filter(transaction__user=request.user,transaction__is_completed = True).order_by("-issued_at")
    number_of_transactions = invoice.count()
    context = {
        "number_of_transactions": number_of_transactions,
        "invoices": invoice
    }
    return render(request, "users/store.html", context)



