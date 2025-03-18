from django.db import models
from django.contrib.auth.models import User

class ShoeCategory(models.Model):
    name = models.CharField(max_length=250)
    def __str__(self):
        return self.name
    

class Product(models.Model):    
    name= models.CharField(max_length=250)
    price= models.IntegerField()
    offerprice= models.IntegerField()
    color= models.CharField(max_length=250)
    image= models.ImageField(upload_to='product/')
    image1= models.ImageField(upload_to='product/',null=False, default='')
    image2= models.ImageField(upload_to='product/',null=False, default='')
    image3= models.ImageField(upload_to='product/',null=False, default='')
    image4= models.ImageField(upload_to='product/',null=False, default='')
    image5= models.ImageField(upload_to='product/',null=False, default='')
    size= models.CharField(max_length=250)
    description= models.TextField()
    shoe_category= models.ForeignKey(ShoeCategory, on_delete=models.CASCADE,null=True)
    priority = models.IntegerField(default=0)#ITEM SEASON WISE CHANGE EG: CHRISMAS, DIWALI. ONAM
    stock= models.PositiveIntegerField()
    def __str__(self):
        return self.name


class Cart(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)#product delete order should be keep thats why SET_NULL
    quantity= models.IntegerField(default=1)
    totalprice=models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return self.product
    


