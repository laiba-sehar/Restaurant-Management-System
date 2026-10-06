from rest_framework import serializers
from .models import menuItem, Table, Reservation, Order, OrderItem, Inventory


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = menuItem
        fields = '__all__'

class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = '__all__'


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = [
            'id',
            'user',
            'table',
            'reservation_date',
            'reservation_time',
            'number_of_guests',
        ]
        read_only_fields = ['id', 'user']

    def validate(self, data):
        request = self.context['request']
        user = request.user

        table = data['table']
        reservation_date = data['reservation_date']
        reservation_time = data['reservation_time']
        number_of_guests = data['number_of_guests']

        # Check table capacity
        if number_of_guests > table.capacity:
            raise serializers.ValidationError(
                f"This table can only accommodate {table.capacity} guests."
            )

        # Check if table is available
        if not table.is_available:
            raise serializers.ValidationError(
                "This table is currently unavailable."
            )

        # Check whether table is already reserved
        existing_reservation = Reservation.objects.filter(
            table=table,
            reservation_date=reservation_date,
            reservation_time=reservation_time
        ).exists()

        if existing_reservation:
            raise serializers.ValidationError(
                "This table is already reserved for this date and time."
            )

        return data
    




class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'table',
            'status',
            'total',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'user',
            'status',
            'total',
            'created_at',
        ]

class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = '__all__'