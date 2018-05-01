from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from registerapp.models import Auction, Bid
from django.db import models
from django.forms import ValidationError
from decimal import Decimal
from django.core.mail import send_mail
from django.contrib.auth.models import User
from rest_framework import generics
import django_filters.rest_framework


class AuctionListSerializer(ModelSerializer):

    class Meta:
        model = Auction
        fields = ['title',
                  'description',
                  'min_price',
                  'deadline',
                  'seller',
                  'timestamp',
                  'state'
                  ]


class BidCreateSerializer(ModelSerializer):
    # bidder = User
    # bidder = models.ForeignKey(User)
    # auction = models.ForeignKey(Auction)
    bidder = serializers.CharField()

    class Meta:
        model = Bid
        fields = ['auction',
                  'bid_amount',
                  'bidder']
        # extra_kwargs = {'bidder': {'read_only': True}}
        # read_only_fields = ['bidder']

    def validate(self, data):
        loggeduser = self.context['request'].user
        bidder = data['bidder']
        bid_amount = data['bid_amount']
        auction = data['auction']
        auction = Auction.objects.get(id=auction.id)
        bid_accepted = round((auction.current_max_bid_amount + Decimal(0.01)), 2)

        if str(loggeduser) != str(bidder):
            raise ValidationError('You are not an authorized user, please login or register via the homepage')

        elif loggeduser == auction.seller:
            raise ValidationError('This is your own auction!')

        elif auction.current_max_bid_obj is not None and str(auction.current_max_bid_obj.bidder) == str(bidder):
            user_current_bid = auction.current_max_bid_obj.bid_amount
            raise ValidationError('You presently owns the highest bid of ' + str(user_current_bid))

        elif bid_amount < bid_accepted:
            raise ValidationError('Your bid must be ' + str(bid_accepted) + ' or higher')

        user_email = loggeduser.email
        user_name = loggeduser.first_name
        bid_receiver_email = auction.seller.email
        bid_receiver_name = auction.seller.first_name

        send_mail('A bid has been placed!',
                  'Hi ' + str(user_name) + ' !, ' +
                  'you have placed a bid for the auction ' + str(auction.title) + '.',
                  'noreplay@yaas.com', [user_email], fail_silently=False)

        send_mail('A bid has been received!',
                  'Hi ' + str(bid_receiver_name) + ' !, ' +
                  'you have received a bid for the auction ' + str(auction.title) + '.',
                  'noreplay@yaas.com', [bid_receiver_email], fail_silently=False)

        return data
