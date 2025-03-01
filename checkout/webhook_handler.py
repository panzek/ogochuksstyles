from django.http import HttpResponse
from .models import Order, OrderLineItem
from profiles.models import UserProfile
from products.models import Product
import stripe
import json


class StripeWH_Handler:
    def __init__(self, request):
        self.request = request

    def handle_payment_intent_succeeded(self, event):
        """Handle the payment_intent.succeeded webhook from Stripe"""
        intent = event.data.object
        pid = intent.id

        try:
            order = Order.objects.get(stripe_pid=pid)
            self._send_confirmation_email(order)
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | SUCCESS: Verified order already in database',
                status=200)
        except Order.DoesNotExist:
            cart = intent.metadata.get('cart')
            save_info = intent.metadata.get('save_info')
            username = intent.metadata.get('username')

            try:
                stripe_charge = stripe.Charge.retrieve(intent.latest_charge)
                billing_details = stripe_charge.billing_details
                shipping_details = intent.shipping or {}
                grand_total = round(stripe_charge.amount / 100, 2)

                if shipping_details and shipping_details.address:
                    for field, value in shipping_details.address.items():
                        if value == "":
                            shipping_details.address[field] = None

                profile = None
                if username and username != 'AnonymousUser':
                    profile = UserProfile.objects.get(user__username=username)
                    if save_info == 'true' and shipping_details:
                        profile.phone_number = shipping_details.phone or ''
                        profile.country = shipping_details.address.get('country', '')
                        profile.postcode = shipping_details.address.get('postal_code', '')
                        profile.town_or_city = shipping_details.address.get('city', '')
                        profile.street_address1 = shipping_details.address.get('line1', '')
                        profile.street_address2 = shipping_details.address.get('line2', '')
                        profile.county = shipping_details.address.get('state', '')
                        profile.save()

                order = Order.objects.create(
                    full_name=shipping_details.get('name', billing_details.name),
                    user_profile=profile,
                    email=billing_details.email,
                    phone_number=shipping_details.get('phone', billing_details.phone),
                    country=shipping_details.address.get('country', '') if shipping_details else '',
                    postcode=shipping_details.address.get('postal_code', '') if shipping_details else '',
                    town_or_city=shipping_details.address.get('city', '') if shipping_details else '',
                    street_address1=shipping_details.address.get('line1', '') if shipping_details else '',
                    street_address2=shipping_details.address.get('line2', '') if shipping_details else '',
                    county=shipping_details.address.get('state', '') if shipping_details else '',
                    grand_total=grand_total,
                    original_cart=cart or '{}',
                    stripe_pid=pid,
                )

                if cart:
                    for item_id, item_data in json.loads(cart).items():
                        product = Product.objects.get(id=item_id)
                        if isinstance(item_data, int):
                            OrderLineItem.objects.create(
                                order=order,
                                product=product,
                                quantity=item_data,
                            )
                        else:
                            for size, quantity in item_data['items_by_size'].items():
                                OrderLineItem.objects.create(
                                    order=order,
                                    product=product,
                                    quantity=quantity,
                                    product_size=size,
                                )

                self._send_confirmation_email(order)
                return HttpResponse(
                    content=f'Webhook received: {event["type"]} | SUCCESS: Created order in webhook',
                    status=200)
            except Exception as e:
                return HttpResponse(
                    content=f'Webhook received: {event["type"]} | ERROR: {e}',
                    status=500)

    def handle_payment_intent_payment_failed(self, event):
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)
