from celery import shared_task
from django.core.mail import send_mail
from .models import Order
from django.utils.timezone import now, timedelta

@shared_task
def send_periodic_order_status_updates():
    """
    Checks for order status changes every hour and notifies users.
    """
    one_hour_ago = now() - timedelta(hours=1)
    orders = Order.objects.filter(updated_at__gte=one_hour_ago)

    for order in orders:
        subject = f"Order #{order.id} Status Update"
        message = f"Your order (ID: {order.id}) status is now: {order.status}."
        
        send_mail(subject, message, "noreply@yourstore.com", [order.user.email])
    
    return f"Sent status updates for {orders.count()} orders."
