from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from auctions.models import *


User =get_user_model()

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name','last_name','username','phone_number','id_card','address','email','password1', 'password2']

    def clean_username(self):
        username = self.cleaned_data['username']
        if len(username) < 3:
            raise forms.ValidationError("Username must be at least 3 characters long.")
        return username
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if len(phone_number) != 13 or not phone_number.startswith('+250'):
            raise forms.ValidationError('Please provide a valid Rwandan phone number starting with "+250".')
        return phone_number

    def clean_password1(self):
        password = self.cleaned_data['password1']
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        return password

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        return password2
    

class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(
        label='Old Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your old password'})
    )
    new_password = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your new password'})
    )
    confirm_new_password = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm your new password'})
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_new_password = cleaned_data.get('confirm_new_password')
        
        if new_password and confirm_new_password and new_password != confirm_new_password:
            raise forms.ValidationError("The new passwords don't match. Please try again.")
        
        return cleaned_data
    


class UserProfileUpdate(forms.ModelForm):
    phone_number = forms.CharField(disabled=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'phone_number'})
    )
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone_number", "address"]


class UserProfileUpdateAdmin(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone_number = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    is_active = forms.BooleanField(label='Is Active', required=False, widget=forms.CheckboxInput(attrs={'class': 'checkbox-class'}))
    is_verified = forms.BooleanField(label='Is Verified', required=False, widget=forms.CheckboxInput(attrs={'class': 'checkbox-class'}))
    is_superuser = forms.BooleanField(label='Is Superuser', required=False, widget=forms.CheckboxInput(attrs={'class': 'checkbox-class'}))
    address = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    id_card = forms.FileField(required=False,widget=forms.FileInput(attrs={'class': 'form-control'}))
    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email", "phone_number", "is_active", "is_verified", "is_superuser" , "address", "id_card"]



class UserUpdateProfileImageForm(forms.ModelForm):
    avatar = forms.ImageField(
        widget=forms.FileInput(attrs={'class': 'form-control', 'id': 'image',})
    )

    class Meta:
        model = User
        fields = ["avatar"]



class TransactionUploadSlipForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["upload_bank_slip"]


