from django.shortcuts import render
from django.shortcuts import get_list_or_404
from rest_framework.generics import (ListAPIView,
                                     CreateAPIView)

from registerapp.models import Auction, Bid
from .serializers import (AuctionListSerializer,
                          #AuctionSearchSerializer,
                          #BidListSerializer,
                          BidCreateSerializer)



class AuctionListAPIView(ListAPIView):

    serializer_class = AuctionListSerializer

    def get_queryset(self, *args, **kwargs):
        queryset_list = Auction.objects.all()
        # username = self.request.query_params.get('username', None)
        query = self.request.GET.get('q')
        if query:
            queryset_list = queryset_list.filter(title__icontains=query).order_by('-timestamp')
        return queryset_list


class BidCreateAPIView(CreateAPIView):
    queryset = Bid.objects.all()
    serializer_class = BidCreateSerializer




