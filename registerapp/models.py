from django.db import models
from django.contrib.auth.models import User
#import validations
from django.core.urlresolvers import reverse
from django.forms import DateTimeInput
import math
import datetime
from decimal import Decimal
# from registerapp.tasks import end_auction
# from celery.contrib.abortable import AbortableAsyncResult


# Create your models here.
class Auction(models.Model):
    seller = models.ForeignKey(User, null=True)
    title = models.CharField(max_length=255, null=True, blank=False)
    description = models.TextField(null=True, blank=True)
    min_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=False)
    timestamp = models.DateTimeField(auto_now_add=True, null=True, blank=True, editable=False)
    deadline = models.DateTimeField(null=True, blank=False)
    task_id = models.CharField(max_length=36, default='')
    STATE_CHOICES = [
        ('active', 'active'),
        ('banned', 'banned'),
        ('due', 'due'),
        ('adjudicated', 'adjudicated'),
    ]
    state = models.CharField(max_length=20, null=True, blank=True)

    def __unicode__(self):
        return self.title

    def __str__(self):
        return self.title


    '''
    def start_timer(self):
        old_task = AbortableAsyncResult(self.task_id)
        old_task.abort()
        task = end_auction.apply_async((self,), countdown=self.get_time_left())
        self.task_id = task.id
        self.save()
        return self
    '''


    @classmethod
    def exists(cls, id):
        return len(cls.objects.filter(id=id)) > 0

    def get_current_max_bid_amount(self):
        if Bid.exists(auction=self):
            max([bid.bid_amount for bid in self.get_all_bids()])
            return max([bid.bid_amount for bid in self.get_all_bids()])
        else:
            return round((self.min_price - Decimal(0.01)), 2)

    current_max_bid_amount = property(get_current_max_bid_amount)

    def get_all_bids(self):
        if Bid.exists(auction=self):
            return Bid.objects.filter(auction=self)

    all_bids = property(get_all_bids)

    def get_current_max_bid_obj(self):
        if Bid.exists(auction=self):
            bids = Bid.objects.filter(auction=self)
            max_bid = self.get_current_max_bid_amount()
            return self.get_all_bids().filter(bid_amount=max_bid).first()
        else:
            return None

    current_max_bid_obj = property(get_current_max_bid_obj)

    def get_time_left(self):
        deadline = self.deadline
        return int(math.floor((deadline.replace(tzinfo=None) - datetime.datetime.now()).total_seconds()))

    time_left = property(get_time_left)

    class Meta:
        ordering = ["deadline"]


    '''
    class Meta:
        ordering = ('-timestamp')
    '''

class Bid(models.Model):
    bidder = models.ForeignKey(User)
    auction = models.ForeignKey(Auction)
    bid_amount = models.DecimalField(max_digits=8, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    @classmethod
    def exists(cls, auction):
        return len(cls.objects.filter(auction=auction)) > 0\

    def __str__(self):
        return str(self.bid_amount)
