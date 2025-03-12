from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.db.models import Q
from django.db.models.functions import Lower
from .models import Product, Category, Review
from .forms import ProductForm, ReviewForm


def all_products(request):
    """ 
    A view to render all products in our store
    """

    products = Product.objects.all()
    query = None
    categories = None
    sort = None
    direction = None

    if request.GET:
        if 'sort' in request.GET:
            sortkey = request.GET['sort']
            sort = sortkey
            if sortkey == 'name':
                sortkey = 'lower_name'
                products = products.annotate(lower_name=Lower('name'))
            if sortkey == 'category':
                sortkey = 'category__name'

            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}'
            products = products.order_by(sortkey)

        if 'category' in request.GET:
            categories = request.GET['category'].split(',')
            products = products.filter(category__name__in=categories)
            categories = Category.objects.filter(name__in=categories)

    if request.GET:
        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(request, "You didn't enter any search criteria!")
                return redirect(reverse('products'))           
            queries = Q(name__icontains=query) | Q(description__icontains=query)
            products = products.filter(queries)

    current_sorting = f'{sort}_{direction}'
    context = {
        'products': products,
        'search_term': query,
        'current_categories': categories,
        'current_sorting': current_sorting,
    }

    return render(request, 'products/products.html', context)


def product_detail(request, product_id):
    """A view to render the product detail page"""
    product = get_object_or_404(Product, id=product_id)
    reviews = Review.objects.filter(product=product, approved=True)  # Only show approved reviews
    form = None

    if request.user.is_authenticated:
        existing_review = Review.objects.filter(user=request.user, product=product).first()
        if not existing_review:
            form = ReviewForm()
        # If a review exists, we’ll use it to show the "awaiting approval" message in the template

    context = {
        'product': product,
        'reviews': reviews,
        'form': form,
    }
    return render(request, 'products/product_detail.html', context)


@login_required(login_url='/accounts/login/')
def add_product(request):
    """ A view for store owner to add products to the store """

    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can add products')
        return redirect(reverse('home'))
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, 'Successfully added product!')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(request, 'Failed to add product. Please ensure the form is valid')
    else:
        form = ProductForm()

    template = 'products/add_product.html'
    context = {
        'form': form
    }

    return render(request, template, context)


@login_required(login_url='/accounts/login/')
def edit_product(request, product_id):
    """ A view for store owner to add products to the store """

    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can edit products')
        return redirect(reverse('home'))   
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        """ A view for store owner to update products in the store """  
        form = ProductForm(request.POST, request.FILES, instance=product)

        if form.is_valid():
            product = form.save()
            messages.success(request, 'Successfully updated product!')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(request, 'Failed to update product. Please ensure the form is valid')
    else:
        form = ProductForm(instance=product)
        messages.info(request, f'You are editing {product.name}')

    template = 'products/edit_product.html'
    context = {
        'form': form,
        'product': product,
    }

    return render(request, template, context)


@login_required(login_url='/accounts/login/')
def delete_product(request, product_id):
    """ A view for store owner to delete products in the store """

    product = get_object_or_404(Product, id=product_id)
    product.delete()
    messages.success(request, 'Product successfully deleted!')
    return redirect('/')


def submit_review(request, product_id):
    """A view to handle submitting or updating a product review"""
    product = get_object_or_404(Product, id=product_id)
    url = request.META.get("HTTP_REFERER", reverse('product_detail', args=[product_id]))

    if request.method == "POST":
        try:
            # Check for an existing review (approved or not, due to unique_together)
            review = Review.objects.get(user=request.user, product=product)
            # Update existing review
            review_form = ReviewForm(request.POST, instance=review)
            if review_form.is_valid():
                review_form.save()
                messages.success(request, "Your review has been successfully updated")
                return redirect(url)
            else:
                messages.error(request, "Failed to update review. Please ensure the form is valid.")
        except Review.DoesNotExist:
            # Create a new review
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                review = review_form.save(commit=False)
                review.user = request.user
                review.product = product
                review.name = request.user.username  # Set name to username
                review.ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
                review.save()
                messages.success(request, "Your review has been submitted and is awaiting approval. Thank you!")
                return redirect('product_detail', product_id=product.id)
            else:
                messages.error(request, "Failed to add review. Please ensure the form is valid.")

    # For GET or invalid form, redirect to product_detail
    return redirect('product_detail', product_id=product.id)