from django.shortcuts import render, redirect, get_object_or_404 
from django.conf import settings
from profiles.forms import UserProfileForm
from profiles.models import UserProfile
from cart.contexts import cart_contents

from django.http import HttpResponse
from django.views.decorators.http import require_POST
from .models import Order, OrderLineItem
from .forms import OrderForm
from products.models import Product  
from django.contrib import messages
import stripe
import json

@require_POST
def cache_checkout_data(request):
    try:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        client_secret = request.POST.get('client_secret')
        pid = client_secret.split('_secret')[0]

        # Modify Payment Intent with metadata
        stripe.PaymentIntent.modify(pid, metadata={
            'cart': json.dumps(request.session.get('cart', {})),
            'save_info': request.POST.get('save_info'),
            'username': str(request.user if request.user.is_authenticated else 'Anonymous'),
        })

        # Create the order
        form_data = {
            'full_name': request.POST.get('full_name'),
            'email': request.POST.get('email'),
            'phone_number': request.POST.get('phone_number'),
            'country': request.POST.get('country'),
            'postcode': request.POST.get('postcode'),
            'town_or_city': request.POST.get('town_or_city'),
            'street_address1': request.POST.get('street_address1'),
            'street_address2': request.POST.get('street_address2'),
            'county': request.POST.get('county'),
        }
        order_form = OrderForm(form_data)
        if order_form.is_valid():
            order = order_form.save(commit=False)
            order.stripe_pid = pid
            order.original_cart = json.dumps(request.session.get('cart', {}))
            order.save()

            # Create order line items
            cart = request.session.get('cart', {})
            for item_id, item_data in cart.items():
                try:
                    product = Product.objects.get(id=item_id)
                    if isinstance(item_data, int):
                        order_line_item = OrderLineItem(
                            order=order,
                            product=product,
                            quantity=item_data,
                        )
                        order_line_item.save()
                    else:
                        for size, quantity in item_data['items_by_size'].items():
                            order_line_item = OrderLineItem(
                                order=order,
                                product=product,
                                quantity=quantity,
                                product_size=size,
                            )
                            order_line_item.save()
                except Product.DoesNotExist:
                    order.delete()
                    return HttpResponse(content="Product not found", status=400)

            request.session['save_info'] = request.POST.get('save_info') == 'true'
            return HttpResponse(status=200)
        else:
            return HttpResponse(content="Invalid form data", status=400)

    except stripe.error.StripeError as e:
        messages.error(request, f"Stripe error: {str(e)}")
        return HttpResponse(content=str(e), status=400)
    except Exception as e:
        messages.error(request, 'Sorry, your payment cannot be processed right now. Please try again later.')
        return HttpResponse(content=str(e), status=400)


def checkout(request):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    # Handle GET request (display form)
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "There is no item in your shopping cart at the moment")
        return redirect('products')  

    current_cart = cart_contents(request)
    total = current_cart['grand_total']
    stripe_total = round(total * 100)

    # Create Payment Intent
    stripe.api_key = stripe_secret_key
    intent = stripe.PaymentIntent.create(
        amount=stripe_total,
        currency=settings.STRIPE_CURRENCY,
        automatic_payment_methods={"enabled": True},
    )

    # Pre-fill form for authenticated users
    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=request.user)
            order_form = OrderForm(initial={
                'full_name': profile.user.get_full_name(),
                'email': profile.user.email,
                'phone_number': profile.phone_number,
                'country': profile.country,
                'postcode': profile.postcode,
                'town_or_city': profile.town_or_city,
                'street_address1': profile.street_address1,
                'street_address2': profile.street_address2,
                'county': profile.county,
            })
        except UserProfile.DoesNotExist:
            order_form = OrderForm()
    else:
        order_form = OrderForm()

    if not stripe_public_key:
        messages.warning(request, 'Stripe public key is missing. \
            Did you forget to set it in your environment?')

    context = {
        'order_form': order_form,
        'stripe_public_key': stripe_public_key,
        'client_secret': intent.client_secret,
    }

    return render(request, 'checkout/checkout.html', context)


def checkout_success(request):
    """
    Handle successful checkouts after Stripe redirect
    """
    # Get payment_intent from query parameters
    payment_intent_id = request.GET.get('payment_intent')
    if not payment_intent_id:
        return render(request, 'checkout/checkout_error.html', {'error': 'Missing payment intent'})

    # Find the order linked to this payment_intent
    order = get_object_or_404(Order, stripe_pid=payment_intent_id)  
    order_number = order.order_number

    save_info = request.session.get('save_info')

    if request.user.is_authenticated:
        profile = UserProfile.objects.get(user=request.user)
        # Attach the user's profile to the order
        order.user_profile = profile
        order.save()

        # Save the user's info
        if save_info:
            profile_data = {
                'phone_number': order.phone_number,
                'country': order.country,
                'postcode': order.postcode,
                'town_or_city': order.town_or_city,
                'street_address1': order.street_address1,
                'street_address2': order.street_address2,
                'county': order.county,
            }
            user_profile_form = UserProfileForm(profile_data, instance=profile)
            if user_profile_form.is_valid():
                user_profile_form.save()

    messages.success(request, f'Order successfully processed! \
        Your order number is {order_number}. A confirmation \
        email will be sent to {order.email}.')

    if 'cart' in request.session:
        del request.session['cart']

    context = {
        'order': order,
    }

    return render(request, 'checkout/checkout_success.html', context)