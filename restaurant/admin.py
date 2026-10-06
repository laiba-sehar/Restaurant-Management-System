from django.contrib import admin
from .models import menuItem, Table, Reservation, Order, OrderItem, Inventory

admin.site.register(menuItem)
admin.site.register(Table)
admin.site.register(Reservation)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Inventory)