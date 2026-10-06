from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import permission_classes
from django.db import transaction
# Create your views here.
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .models import menuItem, Table, Reservation, Order, OrderItem, Inventory
from .serializers import MenuItemSerializer, ReservationSerializer, OrderSerializer, OrderItemSerializer, InventorySerializer


@api_view(['GET'])
def menu_list(request):
    menu_items = menuItem.objects.all()
    serializer = MenuItemSerializer(menu_items, many=True)

    return Response(serializer.data)

@api_view(['GET'])
def menu_detail(request,menu_id):
    menu_item=get_object_or_404(menuItem, id=menu_id)
    serializer=MenuItemSerializer(menu_item)

    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reservation_create(request):
    serializer = ReservationSerializer(
        data=request.data,
        context={'request': request}
    )

    if serializer.is_valid():
        reservation = serializer.save(user=request.user)

        return Response(
            ReservationSerializer(reservation).data,
            status=201
        )

    return Response(serializer.errors, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reservation_list(request):

    reservations = Reservation.objects.filter(
        user=request.user
    ).order_by('reservation_date', 'reservation_time')

    serializer = ReservationSerializer(
        reservations,
        many=True
    )

    return Response(serializer.data)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def reservation_cancel(request, reservation_id):

    reservation = get_object_or_404(
        Reservation,
        id=reservation_id,
        user=request.user
    )

    reservation.delete()

    return Response(
        {
            "message": "Reservation cancelled successfully."
        },
        status=200
    )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def order_create(request):

    table_id = request.data.get('table')
    items = request.data.get('items')

    if not items:
        return Response(
            {"error": "Please provide at least one item."},
            status=400
        )

    table = None

    if table_id:
        table = get_object_or_404(Table, id=table_id)

    stock_alerts = []

    with transaction.atomic():

        order = Order.objects.create(
            user=request.user,
            table=table
        )

        total = 0

        for item in items:

            menu_item = get_object_or_404(
                menuItem,
                id=item['menu_item']
            )

            quantity = item['quantity']

            # Check menu item availability
            if not menu_item.is_available:
                return Response(
                    {
                        "error": f"{menu_item.name} is currently unavailable."
                    },
                    status=400
                )

            # Check inventory exists
            if not menu_item.inventory:
                return Response(
                    {
                        "error": f"No inventory is configured for {menu_item.name}."
                    },
                    status=400
                )

            inventory = menu_item.inventory

            # Check enough stock
            if inventory.quantity < quantity:
                return Response(
                    {
                        "error": (
                            f"Not enough stock for {menu_item.name}. "
                            f"Available: {inventory.quantity}"
                        )
                    },
                    status=400
                )

            # Calculate total
            item_total = menu_item.price * quantity
            total += item_total

            # Create OrderItem
            OrderItem.objects.create(
                order=order,
                menu_item=menu_item,
                quantity=quantity
            )

            # Reduce inventory
            inventory.quantity -= quantity
            inventory.save()

            # Check reorder level
            if inventory.quantity <= inventory.reorder_level:
                stock_alerts.append(
                    f"{inventory.item_name} is low in stock. "
                    f"Remaining: {inventory.quantity} {inventory.unit}. "
                    f"Reorder level: {inventory.reorder_level} {inventory.unit}."
                )

        # Save total
        order.total = total
        order.save()

    return Response(
        {
            "message": "Order placed successfully.",
            "order": OrderSerializer(order).data,
            "stock_alerts": stock_alerts
        },
        status=201
    )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_list(request):

    orders = Order.objects.filter(
        user=request.user
    ).order_by('-created_at')

    serializer = OrderSerializer(
        orders,
        many=True
    )

    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_detail(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    order_data = OrderSerializer(order).data

    items = OrderItem.objects.filter(
        order=order
    )

    items_data = OrderItemSerializer(
        items,
        many=True
    ).data

    order_data['items'] = items_data

    return Response(order_data)   

@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def order_status_update(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id
    )

    new_status = request.data.get('status')

    valid_statuses = [
        'pending',
        'preparing',
        'completed',
        'cancelled'
    ]

    # Check status value
    if new_status not in valid_statuses:
        return Response(
            {
                "error": "Invalid status."
            },
            status=400
        )

    # Prevent changing completed or cancelled orders
    if order.status in ['completed', 'cancelled']:
        return Response(
            {
                "error": f"Order is already {order.status}."
            },
            status=400
        )

    # Prevent completed order from going back to pending
    if order.status == 'preparing' and new_status == 'pending':
        return Response(
            {
                "error": "A preparing order cannot go back to pending."
            },
            status=400
        )

    order.status = new_status
    order.save()

    return Response(
        {
            "message": "Order status updated successfully.",
            "order": OrderSerializer(order).data
        },
        status=200
    )    

@api_view(['GET'])
@permission_classes([IsAdminUser])
def inventory_list(request):

    inventory_items = Inventory.objects.all()

    serializer = InventorySerializer(
        inventory_items,
        many=True
    )

    return Response(serializer.data)

@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def inventory_update(request, inventory_id):

    inventory = get_object_or_404(
        Inventory,
        id=inventory_id
    )

    serializer = InventorySerializer(
        inventory,
        data=request.data,
        partial=True
    )

    if serializer.is_valid():
        serializer.save()

        return Response(
            serializer.data,
            status=200
        )

    return Response(
        serializer.errors,
        status=400
    )

@api_view(['GET'])
def available_tables(request):

    reservation_date = request.query_params.get('date')
    reservation_time = request.query_params.get('time')
    guests = request.query_params.get('guests')

    # Check required parameters
    if not reservation_date or not reservation_time or not guests:
        return Response(
            {
                "error": "Please provide date, time, and number of guests."
            },
            status=400
        )

    # Convert guests to integer
    try:
        guests = int(guests)
    except ValueError:
        return Response(
            {
                "error": "Guests must be a number."
            },
            status=400
        )

    # Find tables already reserved
    reserved_table_ids = Reservation.objects.filter(
        reservation_date=reservation_date,
        reservation_time=reservation_time
    ).values_list(
        'table_id',
        flat=True
    )

    # Find tables that:
    # 1. Are generally available
    # 2. Are not already reserved
    # 3. Have enough capacity
    available_tables = Table.objects.filter(
        is_available=True,
        capacity__gte=guests
    ).exclude(
        id__in=reserved_table_ids
    )

    data = []

    for table in available_tables:
        data.append({
            "id": table.id,
            "table_number": table.table_number,
            "capacity": table.capacity
        })

    return Response(data)