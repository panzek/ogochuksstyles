from django.contrib import messages
from django.shortcuts import render, redirect, reverse, HttpResponse, get_object_or_404
from products.models import Product


def view_cart(request):
    """ A view to render the cart contents page """

    return render(request, 'cart/cart.html')


def _validate_stock(request, product, quantity, size=None, cart=None, item_id=None):
    """
    Helper function to validate stock availability.
    Returns True if the stock is valid, False otherwise.
    """
    if product.stock <= 0:
        messages.error(request, f"Sorry, {product.name} is out of stock.")
        return False

    if size:
        # For products with sizes, check stock for the specific size
        if item_id in cart and 'items_by_size' in cart[item_id]:
            if size in cart[item_id]['items_by_size']:
                total_quantity = cart[item_id]['items_by_size'][size] + quantity
            else:
                total_quantity = quantity
        else:
            total_quantity = quantity
    else:
        # For products without sizes, check total stock
        if item_id in cart:
            total_quantity = cart[item_id] + quantity
        else:
            total_quantity = quantity

    if total_quantity > product.stock:
        messages.error(request, f"Sorry, only {product.stock} units of {product.name} are available.")
        return False

    return True


def add_to_cart(request, item_id):
    """ A view to add items to the shopping cart with stock management """

    product = get_object_or_404(Product, pk=item_id)
    quantity = int(request.POST.get('quantity'))
    redirect_url = request.POST.get('redirect_url')
    size = None
    if 'product_size' in request.POST:
        size = request.POST['product_size']

    cart = request.session.get('cart', {})

    # Validate stock before adding to cart
    if not _validate_stock(request, product, quantity, size, cart, item_id):
        return redirect(redirect_url)

    if size:
        # For products with sizes
        if item_id in cart:
            if 'items_by_size' in cart[item_id]:
                if size in cart[item_id]['items_by_size']:
                    cart[item_id]['items_by_size'][size] += quantity
                else:
                    cart[item_id]['items_by_size'][size] = quantity
            else:
                cart[item_id]['items_by_size'] = {size: quantity}
        else:
            cart[item_id] = {'items_by_size': {size: quantity}}
        messages.success(request, f'Added size {size.upper()} {product.name} to your cart')
    else:
        # For products without sizes
        if item_id in cart:
            cart[item_id] += quantity
        else:
            cart[item_id] = quantity
        messages.success(request, f'Added {product.name} to your shopping cart')

    # Decrement the stock count
    product.stock -= quantity
    product.save()

    request.session['cart'] = cart
    return redirect(redirect_url)


def adjust_cart(request, item_id):
    """
    Adjust the quantity of the specified product to the specified amount
    """

    product = get_object_or_404(Product, pk=item_id)
    quantity = int(request.POST.get('quantity'))
    size = None
    if 'product_size' in request.POST:
        size = request.POST['product_size']
    cart = request.session.get('cart', {})

    if size:
        if quantity > 0:
            cart[item_id]['items_by_size'][size] = quantity
            messages.success(request, f'Updated size {size.upper()} {product.name} quantity to {cart[item_id]["items_by_size"][size]}')
        else:
            del cart[item_id]['items_by_size'][size]
            if not cart[item_id]['items_by_size']:
                cart.pop(item_id)
                messages.success(request, f'Removed size {size.upper()} {product.name} from your cart')
    else:
        if quantity > 0:
            cart[item_id] = quantity
            messages.success(request, f'Updated {product.name} quantity to {cart[item_id]}')
        else:
            cart.pop(item_id)
            messages.success(request, f'Removed {product.name} from your cart')

    request.session['cart'] = cart
    return redirect(reverse('view_cart'))


def remove_from_cart(request, item_id):
    """ A view to remove items from shopping cart and restore stock """

    try:
        product = get_object_or_404(Product, pk=item_id)
        size = None
        if 'product_size' in request.POST:
            size = request.POST['product_size']
        cart = request.session.get('cart', {})

        if size:
            quantity = cart[item_id]['items_by_size'][size]
            del cart[item_id]['items_by_size'][size]
            # Restore stock
            product.stock += quantity
            product.save()
            messages.success(request, f'Removed size {size.upper()} {product.name} from your cart (restored {quantity} to stock)')
            # clean up if no sizes left
            if not cart[item_id]['items_by_size']:
                cart.pop(item_id)
        else:
            quantity = cart[item_id]
            cart.pop(item_id)
            # Restore stock
            product.stock += quantity
            product.save()
            messages.success(request, f'Removed {product.name} from your cart (restored {quantity} to stock)')

        request.session['cart'] = cart
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(request, f'Error removing item: {e}')
        return HttpResponse(status=500)
