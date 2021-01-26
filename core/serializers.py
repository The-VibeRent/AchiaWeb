from rest_framework import serializers
from .models import Item

class ItemSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model=Item
        fields=['id','category','name','rating','image','description','size','condition','color','price','keywords','discount_price']
