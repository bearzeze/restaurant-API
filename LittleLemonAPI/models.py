from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Category(models.Model):
    slug = models.SlugField(max_length=255)
    title = models.CharField(max_length=255)
    
    def __str__(self):
        return self.title
    

class MenuItem(models.Model):
    title = models.CharField(max_length=50, db_index=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, db_index=True)
    featured = models.BooleanField(db_index=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    
    def __str__(self):
        return f"{self.category.title}: {self.title}"


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    
    @property
    def unit_price(self):
        return self.menuitem.price
    
    @property
    def price(self):
        return self.menuitem.price * self. quantity
    
    def __str__(self) -> str:
        return f"{self.user.username} -> {self.menuitem.title}"

    class Meta:
        unique_together = ('menuitem', 'user')


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    delivery_crew = models.ForeignKey(User, on_delete=models.CASCADE, related_name='delivery_crew', null=True)
    status = models.BooleanField(db_index=True, default=False)
    total = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    date = models.DateTimeField(db_index=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    
    class Meta:
        unique_together = ('order', 'menuitem')
        
    def __str__(self):
        return f"{self.quantity} x {self.menuitem.title}"
