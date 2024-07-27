from django import forms
from auctions.models import *
from django.utils import timezone

class AuctionForm(forms.ModelForm):
    class Meta:
        model = Auction
        fields = ['staff', 'start_at', 'end_at']

    def clean(self):
        cleaned_data = super().clean()
        start_at = cleaned_data.get('start_at')
        end_at = cleaned_data.get('end_at')

        if start_at and end_at:
            if end_at < start_at:
                self.add_error('end_at', "End date cannot be before start date.")

        now = timezone.now()
        if start_at and start_at < now:
            self.add_error('start_at', "Auction can't be in the past.")

        return cleaned_data


class ItemCreateForm(forms.ModelForm):
    class Meta:
        model = CapturedVehicle
        fields = ["owner_name","vehicle_name","plate_number","location","captured_on","charged_amount"]

class AddVehicleToAuctionForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ["reverse_price","primary_image"]

class ItemUpdateForm(forms.ModelForm):
    class Meta:
        model = CapturedVehicle
        fields = ["owner_name","vehicle_name","plate_number","location","captured_on","charged_amount"]

class SpecificationUpdateForm(forms.ModelForm):
    class Meta:
        model = Specification
        fields = ["brand","model","year","engine","max_torque","fuel_capacity","power"]