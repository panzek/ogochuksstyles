
from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django_resized import ResizedImageField


class Category(models.Model):
    class Meta:
        verbose_name_plural = 'Categories'

    name = models.CharField(max_length=250)
    friendly_name = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return self.name

    def get_friendly_name(self):
        return self.friendly_name


class Product(models.Model):
    """
    Product model
    """

    category = models.ForeignKey(
            Category,
            null=True,
            blank=True,
            on_delete=models.SET_NULL
        )
    sku = models.CharField(max_length=250, null=True, blank=True)
    name = models.CharField(max_length=250)
    description = models.TextField()
    stock = models.IntegerField(default=0)
    has_sizes = models.BooleanField(default=False, blank=True)
    regular_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        help_text="Full price before any discount"
        )
    discount_percent = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="e.g. 25.00 = 25% off, 100.00 = free"
        )
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        editable=False, 
        )
    rating = models.DecimalField(
            max_digits=6,
            decimal_places=2,
            null=True,
            blank=True
        )
    image_url = models.URLField(max_length=1024, null=True, blank=True)
    image = ResizedImageField(
            size=[600, 800],
            crop=['middle', 'center'],
            quality=75,
            upload_to='product_image/',
            force_format='WEBP',
            null=True,
            blank=True
        )

    def save(self, *args, **kwargs):
        base = self.regular_price or Decimal('0.00')
        if self.discount_percent and self.discount_percent > 0:
            discount_amount = Decimal(self.discount_percent) / Decimal('100')
            self.price = (base * (1 - discount_amount)).quantize(Decimal('0.01'))
        else:
            self.price = base
            self.discount_percent = None
        super().save(*args, **kwargs)
        
    def is_on_sale(self):
        return self.discount_percent is not None and self.discount_percent > 0
    is_on_sale.boolean = True
    
    def get_discount_percentage(self):
        if self.is_on_sale():
            return self.discount_percent
        return Decimal('0.00')
        
    def __str__(self):
        return self.name


class Review(models.Model):
    """
    Review Model
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(
            User,
            null=True,
            blank=False,
            on_delete=models.CASCADE
        )
    name = models.CharField(max_length=100, null=False, blank=False)
    title = models.CharField(max_length=250, null=False, blank=False)
    review = models.TextField(max_length=250, null=False, blank=False)
    rating = models.DecimalField(
            max_digits=6,
            decimal_places=2,
            default=False
        )
    ip = models.GenericIPAddressField(
            protocol="IPv4",
            null=True,
            blank=True,
            default="0.0.0.0"
        )
    status = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    approved = models.BooleanField(default=False, blank=True)

    class Meta:
        unique_together = ('user', 'product')  # Ensures only one review per user-product pair
        ordering = ["created_on"]

    def __str__(self):
        return f"Review {self.review} by {self.name}"
