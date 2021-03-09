from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from .models import *

class ItemResource(resources.ModelResource):
    class Meta:
        model = Item


def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)


make_refund_accepted.short_description = 'Update orders to refund granted'


class OrderAdmin(admin.ModelAdmin):
    list_display = ['customer',
                    'ordered',
                    'being_delivered',
                    'received',
                    'refund_requested',
                    'refund_granted',
                    'payment',
                    ]
    list_display_links = [
        'customer',
        'payment',
    ]
    list_filter = ['ordered',
                   'being_delivered',
                   'received',]
    search_fields = [
        'user__username',
        'ref_code'
    ]
    actions = [make_refund_accepted]




@admin.register(Item)
class ItemAdmin(ImportExportModelAdmin):
    pass

admin.site.register(Banner)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Customer)
admin.site.register(Comment)
admin.site.register(Category)
admin.site.register(Size)