from django.db.models.signals import post_save
from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.shortcuts import reverse
from django_countries.fields import CountryField

from django.contrib.auth.models import User



LABEL_CHOICES = (
	('P', 'primary'),
	('S', 'secondary'),
	('D', 'danger')
)

ADDRESS_CHOICES = (
	('B', 'Billing'),
	('S', 'Shipping'),
)
CONDITION_CHOICES = (
	('N', 'New'),
	('U', 'Used'),
)

COLOR_CHOICES = (
	('R', 'Red'),
	('B', 'Blue'),
)


class Customer(models.Model):
	user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
	name = models.CharField(max_length=200, null=True, blank=True)
	email = models.CharField(max_length=200, null=True, blank=True)
	phone = models.IntegerField(blank=True,null=True)
	device = models.CharField(max_length=200, null=True, blank=True)
	stripe_customer_id = models.CharField(max_length=200,null=True,blank=True)
	one_click_purchasing = models.BooleanField(default=False)


	def __str__(self):
		if self.name:
			name = self.name
		else:
			name = self.device
		return str(name)

class Banner(models.Model):
	quote=models.CharField(max_length=10)
	image=models.ImageField(upload_to='banners/')
	hastag1=models.CharField(max_length=20,default='Fresh')
	hastag2=models.CharField(max_length=20,default='Trendy')



class Category(models.Model):
    name = models.CharField(max_length=200)

    class Meta:  
        verbose_name_plural = "categories"     

    def __str__(self):                           
        return self.name

class Size(models.Model):
    size = models.IntegerField()
	
    def __str__(self):                           
        return str(self.size)

class Item(models.Model):
	id = models.IntegerField(primary_key=True)
	category = models.ForeignKey(Category,on_delete=models.SET_NULL , null=True, blank=True)
	name = models.CharField(max_length=100)
	rating = models.IntegerField(default=2)
	image = models.ImageField(upload_to='uploads/')
	description = models.TextField()
	fit = models.ForeignKey(Size,on_delete=models.SET_NULL , null=True, blank=True)
	condition = models.CharField(choices=CONDITION_CHOICES,max_length=1,blank=True, null=True)
	color = models.CharField(choices=COLOR_CHOICES,max_length=1,blank=True, null=True)
	price = models.FloatField()
	keywords = models.CharField(choices=LABEL_CHOICES, max_length=1)
	discount_price = models.FloatField(blank=True, null=True)
	release_date = models.DateField(auto_now_add=True,null=True)
	slug = models.SlugField()

	def __str__(self):
		return self.name

	def get_absolute_url(self):
		return reverse("core:product", kwargs={
			'slug': self.slug
		})

	def get_add_to_cart_url(self):
		return reverse("core:add-to-cart", kwargs={
			'slug': self.slug
		})

	def get_remove_from_cart_url(self):
		return reverse("core:remove-from-cart", kwargs={
			'slug': self.slug
		})
		
	def get_price(self):
		if self.discount_price:
			return self.discount_price
		else:
			return self.price

class Comment(models.Model):
	item = models.ForeignKey(Item,on_delete=models.CASCADE,related_name='comments')
	name = models.CharField(max_length=50 , primary_key=True)
	email = models.EmailField(null=True)
	body = models.TextField()
	created_on = models.DateTimeField(auto_now_add=True)
	active = models.BooleanField(default=True)

	class Meta:
		ordering = ['created_on']

	def __str__(self):
		return 'Comment {} by {}'.format(self.body, self.name)


class OrderItem(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
	ordered = models.BooleanField(default=False)
	item = models.ForeignKey(Item, on_delete=models.CASCADE)
	quantity = models.IntegerField(default=1)

	def __str__(self):
		return f"{self.quantity} of {self.item.name}"

	def get_total_item_price(self):
		return self.quantity * self.item.price

	def get_total_discount_item_price(self):
		return self.quantity * self.item.discount_price

	def get_amount_saved(self):
		return self.get_total_item_price() - self.get_total_discount_item_price()

	def get_final_price(self):
		if self.item.discount_price:
			return self.get_total_discount_item_price()
		return self.get_total_item_price()


class Order(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
	ref_code = models.CharField(max_length=20, blank=True, null=True)
	items = models.ManyToManyField(OrderItem)
	start_date = models.DateTimeField(auto_now_add=True)
	ordered_date = models.DateTimeField()
	ordered = models.BooleanField(default=False)
	payment = models.BooleanField(default=False)
	being_delivered = models.BooleanField(default=False)
	received = models.BooleanField(default=False)
	refund_requested = models.BooleanField(default=False)
	refund_granted = models.BooleanField(default=False)

	def __str__(self):
		if self.customer.name:
			return self.customer.name
		else:
			return self.customer.device

	def get_total(self):
		total = 0
		for order_item in self.items.all():
			total += order_item.get_final_price()
		return total

	def get_list(self):
		list_item=[]
		for item in self.items.all():
			if item.ordered==False:
				dic = {'price_data': {'currency': 'inr','unit_amount': int(item.item.get_price()*100),'product_data': {'name': str(item.item.name),},},'quantity': int(item.quantity),}
				#'images': ['https:localhost:8000'+str(item.item.image.url)],
				list_item.append(dic)
		return list_item
