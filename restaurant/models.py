from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class menuItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)

    inventory = models.OneToOneField(
        'Inventory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='menu_item'
    )

    def __str__(self):
        return self.name
        
class Table(models.Model):
    number=models.PositiveIntegerField(unique=True)
    capacity=models.PositiveIntegerField()
    is_available=models.BooleanField(default=True)

    def __str__(self):
        return f"Table {self.number} - Capacity: {self.capacity}"

class Reservation(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reservations"
    )
    table = models.ForeignKey(
        Table,
        on_delete=models.CASCADE,
        related_name="reservations"
    )
    reservation_date = models.DateField()
    reservation_time = models.TimeField()
    number_of_guests = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.user.username} - Table {self.table.number} on {self.reservation_date} at {self.reservation_time}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('preparing', 'Preparing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders"
    )
    table = models.ForeignKey(
        Table,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )
    menu_item = models.ForeignKey(
        menuItem,
        on_delete=models.CASCADE,
        related_name="order_items"
    )
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.menu_item.name} x {self.quantity}"

class Inventory(models.Model):
    item_name = models.CharField(max_length=200)
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    unit = models.CharField(max_length=50)
    reorder_level = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return self.item_name