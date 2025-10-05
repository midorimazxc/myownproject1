from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import Avg

class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Guitar(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='guitars')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=15, decimal_places=2)
    image = models.ImageField(upload_to='guitars/', blank=True, null=True)

    def get_average_rating(self):
        avg = self.reviews.aggregate(Avg('rating'))['rating__avg']
        return(round(avg, 1)) if avg else 0


    def __str__(self):
        return self.name

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_total(self):
        return sum(item.get_subtotal() for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    guitar = models.ForeignKey(Guitar, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def get_subtotal(self):
        return self.guitar.price * self.quantity

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=12)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    guitar = models.ForeignKey(Guitar, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

class Review(models.Model):
    guitar = models.ForeignKey(Guitar, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    rating = models.PositiveIntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)