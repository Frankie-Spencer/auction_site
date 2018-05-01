from django import forms
from registerapp.models import Auction, Bid
from django.forms import ValidationError
from decimal import Decimal


class DateInput(forms.DateTimeInput):
    input_type = 'date'


class AuctionCreateForm(forms.ModelForm):
    class Meta:
        model = Auction
        fields = ['title', 'description', 'min_price', 'deadline']
        exclude = ['seller', 'timestamp', 'state']
        widgets = {
            'deadline': DateInput(attrs={'type': 'date'}),
        }

        def save(self, commit=True):
            auction = super(AuctionCreateForm, self).save(commit=False)
            if commit:
                auction.save()
                return auction


class AuctionEditForm(forms.ModelForm):
    class Meta:
        model = Auction
        fields = ['description']

        def save(self, commit=True):
            auction = super(AuctionEditForm, self).save(commit=False)
            # auction.description = self.cleaned_data['description']
            if commit:
                auction.save()
                return auction


class BidForm(forms.ModelForm):
    # auctionlastupdate = forms.DateTimeField(widget=forms.HiddenInput(),required=True)
    class Meta:
        model = Bid
        fields = ['bid_amount']
        exclude = ['bidder', 'auction', 'timestamp']

        def save(self, commit=True):
            bid = super(BidForm, self).save(commit=False)
            # bid.price = self.cleaned_data['price']
            if commit:
                bid.save()
                return bid

