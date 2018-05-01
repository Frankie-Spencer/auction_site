from django.conf.urls import url
from django.contrib import admin
from django.conf.urls import include, url

from registerapp.views import create_auction, ban_auction, \
                              all_auctions, show_auction, delete_auction, edit_auction, \
                                bid_auction, bid_history
from Register.views import authenticate, login, logout, register_user, view_user_profile, \
                            edit_user_profile, \
                           reset_password

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.contrib.auth.views import login
admin.autodiscover()
from rest_framework.urlpatterns import format_suffix_patterns
from api.APIviews import (AuctionListAPIView,
                          # AuctionSearchAPIView,
                          # BidListAPIView,
                          BidCreateAPIView)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', all_auctions, name='all_auctions'),
    url(r'^accounts/login/$', login, {'template_name': 'login.html'}),
    url(r'^accounts/auth/$', authenticate, name='authenticate'),
    url(r'^accounts/logout/$', logout, name='logout'),
    url(r'^accounts/registeruser/$', register_user, name='registeruser'),
    url(r'^accounts/userprofile/$', view_user_profile, name='user_profile'),
    url(r'^accounts/userprofile/edit/$', edit_user_profile, name='edit_user_profile'),
    url(r'^accounts/userprofile/reset-password/$', reset_password, name='reset_password'),

    # urls for auctions
    url(r'^auctions/create/$', create_auction, name='create_auction'),
    # url(r'^(?P<auction_id>\d+)/$', save_auction, name='save_auction'),
    url(r'^auctions/$', all_auctions, name='all_auctions'),
    url(r'^showauction/(?P<auction_id>\d+)/$', show_auction, name='show_auction'),
    url(r'^deleteauction/(?P<auction_id>\d+)/$', delete_auction, name='delete_auction'),
    url(r'^editauction/(?P<auction_id>\d+)/$', edit_auction,  name='edit_auction'),
    # url(r'^saveauction/(?P<auction_id>\d+)/$', save_auction, name='save_auction'),
    url(r'^banauction/(?P<auction_id>\d+)/$', ban_auction, name='ban_auction'),

    url(r'^bidauction/(?P<auction_id>\d+)/$', bid_auction, name='bid_auction'),
    url(r'^bidhistory/(?P<auction_id>\d+)/$', bid_history, name='bid_history'),

    url(r'^api/auctions/', AuctionListAPIView.as_view()),
    url(r'^api/bid/', BidCreateAPIView.as_view()),

    # Examples:
    # url(r'^$', 'Register.views.home', name='home'),
    # url(r'^Register/', include('Register.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
]
urlpatterns = format_suffix_patterns(urlpatterns)


