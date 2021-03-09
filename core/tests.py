
list_item=[]
for item in self.items.all():
    dic = {'price_data': {'currency': 'inr','unit_amount': int(item.price*100),'product_data': {'name': str(item.name),'images': [str(item.image.url)],},},'quantity': 1,}
    list_item.append(dic)
print(list_item)