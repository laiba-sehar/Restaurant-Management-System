from django.urls import path
from .views import menu_list, menu_detail, reservation_create, order_create, inventory_list, inventory_update, available_tables, reservation_list, reservation_cancel, order_list, order_detail, order_status_update


urlpatterns = [
    path('menu/', menu_list),
    path('menu/<int:menu_id>/', menu_detail),
    path('reservations/', reservation_create),
    path('reservations/list/', reservation_list),
    path('reservations/<int:reservation_id>/cancel/', reservation_cancel),
    path('orders/', order_create),
    path('inventory/', inventory_list),
    path('inventory/<int:inventory_id>/', inventory_update),
    path('tables/available/', available_tables),
    path('orders/list/', order_list),
    path('orders/<int:order_id>/', order_detail),
    path(
    'orders/<int:order_id>/status/',
    order_status_update
),

]