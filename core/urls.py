from django.urls import path,include
from .views import *
from rest_framework import routers
from .viewset import ItemViewSet
router = routers.DefaultRouter()
router.register('item', ItemViewSet)

app_name = 'core'

urlpatterns = [
    path('api/',include(router.urls)),
    path('', HomeView.as_view(), name='home'),
    path('collection/', CollectionView.as_view(), name='collection'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('product/<slug>/', ItemDetailView, name='product'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('add-coupon/', AddCouponView.as_view(), name='add-coupon'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('remove-item-from-cart/<slug>/', remove_single_item_from_cart,
         name='remove-single-item-from-cart'),
    #path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),
    path('request-refund/', RequestRefundView.as_view(), name='request-refund'),

    path('cancel/', CancelView.as_view(), name='cancel'),
    path('success/', SuccessView.as_view(), name='success'),
    path('create-checkout-session/', CreateCheckoutSessionView.as_view(), name='create-checkout-session')
]