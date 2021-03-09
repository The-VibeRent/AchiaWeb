import django_filters
from .models import *
from django.shortcuts import render
from django import forms

class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name',lookup_expr='icontains')
    price = django_filters.NumberFilter()
    price__gt = django_filters.NumberFilter(field_name='price', lookup_expr='gt')
    price__lt = django_filters.NumberFilter(field_name='price', lookup_expr='lt')
    category = django_filters.ModelMultipleChoiceFilter(queryset=Category.objects.all(),widget=forms.CheckboxSelectMultiple)
    fit = django_filters.ModelMultipleChoiceFilter(queryset=Size.objects.all(),widget=forms.CheckboxSelectMultiple)
    release_year = django_filters.NumberFilter(field_name='release_date', lookup_expr='year')
    release_year__gt = django_filters.NumberFilter(field_name='release_date', lookup_expr='year__gt')
    release_year__lt = django_filters.NumberFilter(field_name='release_date', lookup_expr='year__lt')

    class Meta:
        model = Item
        fields = ['name','price','release_date']

def search(request):
    item_list = Item.objects.all()
    user_filter = ProductFilter(request.GET, queryset=item_list)
    return render(request, 'collection.html', {'filter': user_filter})
