from django import template
from core.models import Order,Customer

register = template.Library()


@register.filter
def cart_item_count(user):
    try:
        device = self.request.COOKIES['device']
        customer = Customer.objects.get(device=device)
        order = Order.objects.get(customer = customer, ordered=False)
        return order[0].items.count()
    except:
        return 0
