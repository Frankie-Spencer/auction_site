# from registerapp.models import Auction, Bid
import requests
import csv
import datetime
import time
import schedule


def api_read_test():
    rates_api = requests.get('http://127.0.0.1:8000/api/auctions/?format=json')
    data = rates_api.json()
    # print(data)
    for item in data:
        title = item['title']
        description = item['description']
        min_price = item['min_price']
        deadline = item['deadline']
        print(title, min_price)


# api_read_test()

def api_search_test():
    search = 'test 4'
    rates_api = requests.get('http://127.0.0.1:8000/api/auctions/?format=json&q='+search)
    data = rates_api.json()
    # print(data)
    for item in data:
        title = item['title']
        description = item['description']
        min_price = item['min_price']
        deadline = item['deadline']
        print(title, min_price)

api_search_test()


'''
def all_auctions():
    auctions = Auction.objects.filter().exclude(state='banned').order_by('-timestamp')
    print(auctions)

all_auctions()
'''