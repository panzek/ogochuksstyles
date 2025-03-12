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
    price = models.DecimalField(max_digits=6, decimal_places=2)
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
            null=True,
            blank=True
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

