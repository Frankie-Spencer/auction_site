from django.template.context_processors import csrf
from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404, redirect
from registerapp.forms import AuctionCreateForm, AuctionEditForm, BidForm
from registerapp.models import Auction, Bid
from datetime import datetime, timezone, timedelta
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from decimal import Decimal
import schedule
# from background_task import background


def base(request):
    loggeduser = request.user
    return render(request, 'base.html', {'aloggeduser': loggeduser})


def all_auctions(request):
    auctions = Auction.objects.filter().exclude(state='banned').order_by('-timestamp')
    loggeduser = request.user

    query = request.GET.get('q')

    if query:

        auctions = auctions.filter(title__icontains=query).order_by('-timestamp')
        if not auctions.exists():
            errmsg = "No matches found"
            return render(request, 'auctions.html', {'errmsg_search': errmsg})

    paginator = Paginator(auctions, 5)
    page_request_var = "page"
    page = request.GET.get(page_request_var)
    try:
        auctions = paginator.page(page)
    except PageNotAnInteger:
        auctions = paginator.page(1)
    except EmptyPage:
        auctions = paginator.page(paginator)

    return render(request, 'auctions.html', {'auctions': auctions,

                                             'loggeduser': loggeduser})


@login_required
def create_auction(request, auction_id=None):
    auction = None
    errmsg = ''
    if request.user.is_authenticated():
        if auction_id:
            auction = get_object_or_404(Auction, id=auction_id)
        if request.method == 'POST':
            form = AuctionCreateForm(request.POST)
            if form.is_valid():
                auction = form.save(commit=False)
                today = datetime.today()
                end_date = today + timedelta(days=3)
                if end_date < auction.deadline:
                    if auction.min_price is not None:
                        auction.seller = request.user
                        auction.state = 'active'
                        auction.save()

                        user_email = str(request.user.email)
                        user_name = str(request.user.first_name)

                        send_mail('An auction is created!',
                                  'Hi' + user_name + ' !, ' +
                                  'you have made an auction named ' + str(auction.title) + '.',
                                  'noreplay@yaas.com', [user_email], fail_silently=False)
                        messages.success(request, 'Your auction is created successfully!')
                        return redirect('/showauction/' + auction.id)
                    else:
                        errmsg = "Please set a starting bid"
                else:
                    errmsg = "Deadline must be at least 3 days from now"
            else:
                errmsg = "Please correct your inputs."
        else:
            form = AuctionCreateForm(request.POST)

    else:
        messages.success(request, 'Please login to create an auction!')
        return redirect('/accounts/login/')

    return render(request, 'create_auction.html', {'form': form,
                                                   'username': request.user,
                                                   'errmsg': errmsg})

'''
@background(schedule=10)
def due_schedule(task_id):
    auction = Auction.objects.get(id=task_id)
    #time.sleep(5)
    auction.state = 'due'
    auction.save()
'''


def show_auction(request, auction_id):
        auction = Auction.objects.get(id=auction_id)
        timeleft = auction.deadline - datetime.now()
        hoursleft = (str(timeleft)[:-13])
        loggeduser = request.user
        current_bid = auction.current_max_bid_obj
        make_changes = (loggeduser == auction.seller) == True
        args = {'auction_title': auction.title,
                'auction_id': auction.id,
                'auction_created': auction.timestamp,
                'auction_deadline': auction.deadline,
                'auction_description': auction.description,
                'auction_price': auction.min_price,
                'time_left': hoursleft + ' hours',
                'seller': auction.seller,
                'logged_user': loggeduser,
                'make_changes': make_changes,
                'current_bid': current_bid}

        if auction.state == 'banned':
            messages.success(request, 'This auction is banned')
            return render(request, 'view_auction.html', args)

        else:
            return render(request, 'view_auction.html', args)


@login_required
def delete_auction(request, auction_id):
    errmsg = ""
    if auction_id:
        auction_to_delete = get_object_or_404(Auction, id=auction_id)
        if auction_to_delete.user == request.user:
            auction_to_delete.delete()
            return redirect('/auctions/')
        else:
            messages.success(request, 'Unauthorized user!')
            return redirect('/auctions/')


@login_required
def edit_auction(request, auction_id=None):
    if User.is_authenticated:
        auction = get_object_or_404(Auction, id=auction_id)
        if request.method == 'POST':
            form = AuctionEditForm(request.POST, instance=auction)
            if form.is_valid():
                auction = form.save(commit=False)
                auction.seller = request.user
                auction.save()
                messages.success(request, 'Auction description successfully edited!')
                return redirect('/showauction/'+auction_id)
        else:
            form = AuctionEditForm(instance=auction)

        return render(request, "edit_auction.html", {'form': form,
                                                     'auction': auction})


@login_required
def ban_auction(request, auction_id):
    banned_auction = Auction.objects.get(id=auction_id)
    banned_auction.state = 'banned'
    banned_auction.save()
    email = str(request.banned_auction.seller.email)

    send_mail('Your auction is banned!', 'Hi ' + str(banned_auction.seller) + ' !, ' +
              'Your auction' + str(banned_auction.title) + ' is banned.',
              'noreplay@yaas.com', [email], fail_silently=False)
    messages.success(request, 'Auction banned successfully!')
    return redirect('/auctions/')


@login_required
def bid_auction(request, auction_id):
    errmsg = ''
    loggeduser = request.user

    if Auction.exists(auction_id):
        if User.is_authenticated:
            auction = Auction.objects.get(id=auction_id)
            bid_accepted = round((auction.current_max_bid_amount + Decimal(0.01)), 2)
            bids = Bid.objects.filter(auction_id=auction_id).order_by('-timestamp')
            args = {'auction_title': auction.title,
                    'bids': bids,
                    'errmsg': errmsg}

            if loggeduser == auction.seller:
                messages.success(request, 'This is your own auction!')
                return render(request, "bid_auction.html", args)

            elif auction.current_max_bid_obj is not None and auction.current_max_bid_obj.bidder == loggeduser:
                user_current_bid = auction.current_max_bid_obj.bid_amount
                messages.success(request, 'You presently owns the highest bid of ' + str(user_current_bid))
                return render(request, "bid_auction.html", args)

            elif request.method == 'POST':
                form = BidForm(request.POST)
                if form.is_valid():
                    bid = form.save(commit=False)
                    if bid.bid_amount < bid_accepted:
                        errmsg = ('Your bid must be ' + str(bid_accepted) + ' or higher')
                    else:
                        bid.bidder = loggeduser
                        bid.auction = auction
                        # bid.timestamp = datetime.now()
                        bid.save()

                        user_email = request.user.email
                        user_name = request.user.first_name

                        send_mail('A bid has been placed!',
                                  'Hi ' + str(user_name) + ' !, ' +
                                  'you have placed a bid for the auction ' + str(auction.title) + '.',
                                  'noreplay@yaas.com', [user_email], fail_silently=False)

                        messages.success(request, 'Your bid successfully placed!')
                        return redirect('/bidauction/'+auction_id)

                return render(request, "bid_auction.html", {'form': form,
                                                            'auction_title': auction.title,
                                                            'bids': bids,
                                                            'bid_accepted': bid_accepted,
                                                            'errmsg': errmsg})
            else:
                messages.success(request, 'Some error occurred, please try again!')
                return redirect('/bidauction/'+auction_id)
        else:
            messages.success(request, 'Please login to create an auction!')
            return redirect('/accounts/login/')
    else:
        messages.success(request, 'Auction does not exits!')
        return redirect('/auctions/')


def bid_history(request, auction_id):
    bids = Bid.objects.filter(auction_id=auction_id).order_by('-timestamp')
    return render(request, "bid_history.html", {'bids': bids})


'''
class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


@csrf_exempt
def auction_list(request, auction_id):

    if request.method == 'GET':
        auction = Auction.objects.get(id=auction_id)
        serializer = AuctionSerializer(auction, many=True)
        return JSONResponse(serializer.data)

def search_auction(request):
    auctions = Auction.objects.all().order_by('-timestamp')
    searchtitle = request.GET.get('searchtitle','')

    return render(request, "search_auction.html",{'auctions':auctions,'searchtitle':searchtitle,},)

'''