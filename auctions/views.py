from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from datetime import datetime
from django.utils import timezone

from .models import (
    Auction,
    Bid,
    Category,
    User)

from .forms import (
    AuctionForm,
    BidForm,
    CommentForm
)



def index(request):
    active_auctions = Auction.objects.filter(
        ended_manually=False,
        end_time__gte=datetime.now()
    )

    categories = Category.objects.all()

    return render(request, "auctions/auction_list.html", {
        "auctions": active_auctions,
        "title" : "Active Auctions",
        "categories": categories
    })


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        categories = Category.objects.all()
        return render(request, "auctions/login.html", { 'categories' : categories })


@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            categories = Category.objects.all()
            return render(request, "auctions/register.html", {
                "message" : "Passwords must match.",
                'categories' : categories
            })

        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message" : "Username already taken.",
                'categories' : categories
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        categories = Category.objects.all()
        return render(request, "auctions/register.html", { 'categories' : categories })


def auction(request, id):
    try:
        auction = Auction.objects.get(id=id)
    except:
        return HttpResponse("Entry does not exist")


    categories = Category.objects.all()
    context = {}
    context["auction"] = auction
    context['categories'] = categories

    if auction.is_finshed():
        context["ended"] = True
        return render(request, "auctions/auction.html", context)

    context["ended"] = False

    time_remaining = auction.end_time - timezone.now()
    context["days"] = time_remaining.days
    context["hours"] = int(time_remaining.seconds / 3600)
    context["minutes"] = int(time_remaining.seconds / 60 - (context["hours"] * 60))
    context["bid_form"] = BidForm()
    context["comment_form"] = CommentForm()

    return render(request, "auctions/auction.html", context)


@login_required
def auction_bid(request, id):
    bid_form = BidForm(request.POST or None)

    if bid_form.is_valid():
        auction = Auction.objects.get(id=id)
        user = request.user
        new_bid = bid_form.save(commit=False)
        current_bids = Bid.objects.filter(auction=auction)
        is_highest_bid = all(new_bid.amount > n.amount for n in current_bids)
        is_valid_first_bid = new_bid.amount >= auction.start_bid

        if is_highest_bid and is_valid_first_bid:
            new_bid.auction = auction
            new_bid.user = request.user
            new_bid.save()

    url = reverse('auction', kwargs={'id': id})
    return HttpResponseRedirect(url)


@login_required
def auction_close(request, id):
    auction = Auction.objects.get(id=id)
    if request.user == auction.user:
        auction.ended_manually = True
        auction.save()

    url = reverse('auction', kwargs={'id': id} )
    return HttpResponseRedirect(url)


@login_required
def auction_comment(request, id):
    comment_form = CommentForm(request.POST or None)

    # add comment to database
    if comment_form.is_valid():
        new_comment = comment_form.save(commit=False)
        new_comment.auction = Auction.objects.get(id=id)
        new_comment.user = request.user
        new_comment.save()

    url = reverse('auction', kwargs={'id': id})
    return HttpResponseRedirect(url)


def category(request, name):
    category = Category.objects.get(name=name)
    auctions = Auction.objects.filter(
        category=category,
        ended_manually=False,
        end_time__gte=datetime.now()
    )
    categories = Category.objects.all()
    return render(request, "auctions/auction_list.html", {
        "auctions" : auctions,
        "title" : category.name,
         'categories' : categories
    })


@login_required
def create_listing(request):
    form = AuctionForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        new_listing = form.save(commit=False)
        new_listing.user = request.user
        new_listing.save()

        url = reverse('auction', kwargs={'id': new_listing.id})
        return HttpResponseRedirect(url)

    else:
        categories = Category.objects.all()
        return render(request, "auctions/create_listing.html", {
            'form': form,
            'categories' : categories
        })


@login_required
def watch_auction(request, id):
    if request.method == "POST":
        auction = Auction.objects.get(id=id)
        watchlist = request.user.watchlist
        if auction in watchlist.all():
            watchlist.remove(auction)
        else:
            watchlist.add(auction)

    url = reverse('auction', kwargs={'id': id})
    return HttpResponseRedirect(url)


@login_required
def watchlist(request):
    categories = Category.objects.all()
    return render(request, "auctions/auction_list.html", {
        "auctions" : request.user.watchlist.all(),
        "title" : "Watchlist",
        'categories' : categories
    })

@login_required
def my_auctions(request):
    auctions = Auction.objects.filter(
        user=request.user
    )

    categories = Category.objects.all()
    return render(request, "auctions/my_auction_list.html", {
        "auctions": auctions,
        "title" : "My Auctions",
        "categories": categories
    })