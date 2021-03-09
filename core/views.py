import random
import string

import stripe
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views.generic import ListView, DetailView, View
from django.http import JsonResponse, HttpResponse
from django.views.generic import TemplateView

from .forms import *
from .models import *

stripe.api_key = settings.STRIPE_SECRET_KEY


def products(request):
    context = {
        'items': Item.objects.all()
    }
    return render(request, "products.html", context)


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid

class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        device = self.request.COOKIES['device']
        customer = Customer.objects.get(device=device)
        order = Order.objects.get(customer=customer, ordered=False)
        YOUR_DOMAIN = "http://192.168.43.159:8000"
        checkout_session = stripe.checkout.Session.create(
            billing_address_collection='auto',
            shipping_address_collection={'allowed_countries': ['IN'],},
            payment_method_types=['card'],
            line_items = order.get_list(),
            metadata={
                'id':str(customer.device),
            },
            mode='payment',
            success_url=YOUR_DOMAIN + '/success/',
            cancel_url=YOUR_DOMAIN + '/order-summary/',
        )
        return JsonResponse({
            'id': checkout_session.id
        })

def payment_success(request):
    device = request.COOKIES['device']
    customer = Customer.objects.get(device=device)
    order = Order.objects.get(customer=customer,ordered=False)
    order.items.ordered=True
    order.ordered=True
    order.save()
    messages.success(request, "Your orderd is successfully placed. You will recive a Mail shortly!")
    return redirect('core:home')

def payment_cancel(request):
    messages.error(request, "Your orderd is intruppted. May be due to network issues.")
    return redirect('core:order-summary')

class HomeView(ListView):
    model = Item
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context.update({
            'order': OrderItem.objects.all(),
            'primary': Item.objects.all().filter(keywords='P',)[:4],
            'secondary': Item.objects.all().filter(keywords='S')[:4],
            'danger': Item.objects.all().filter(keywords='D')[:4],
            'banner': Banner.objects.all()[:3],
        })
        return context

    def get_queryset(self):
        return Item.objects.all()


class CollectionView(ListView):
    model = Item
    template_name = "collection.html"

    def get_context_data(self, **kwargs):
        context = super(CollectionView, self).get_context_data(**kwargs)
        context.update({
            'order': OrderItem.objects.all()
        })
        return context

    def get_queryset(self):
        return Item.objects.all()


class OrderSummaryView(View):
    def get(self, *args, **kwargs):
        try:
            device = self.request.COOKIES['device']
            customer = Customer.objects.get(device=device)
            order = Order.objects.get(customer=customer, ordered=False)
            context = {
                'object': order,
                'STRIPE_PUBLIC_KEY':settings.STRIPE_PUBLIC_KEY
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")


def ItemDetailView(request, slug):
    item = get_object_or_404(Item, slug=slug)
    comments = item.comments.filter(active=True)
    new_comment = None
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.item = item
            # Save the comment to the database
            new_comment.save()
    else:
        comment_form = CommentForm()
    return render(request, 'product.html', {'slug': slug, 'object': item, 'comment': comments, 'new_comment': new_comment, 'comment_form': comment_form})


def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    try:
        customer = request.user.customer
    except:
        device = request.COOKIES['device']
        customer, created = Customer.objects.get_or_create(device=device)

    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        customer=customer,
        ordered=False
    )
    order_qs = Order.objects.filter(customer=customer, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect("core:order-summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            customer=customer, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect("core:order-summary")


def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    try:
        customer = request.user.customer
    except:
        device = request.COOKIES['device']
        customer, created = Customer.objects.get_or_create(device=device)

    order_qs = Order.objects.filter(
        customer=customer,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                customer=customer,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, "This item was removed from your cart.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)


def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    try:
        customer = request.user.customer
    except:
        device = request.COOKIES['device']
        customer, created = Customer.objects.get_or_create(device=device)

    order_qs = Order.objects.filter(
        customer=customer,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                customer=customer,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)
