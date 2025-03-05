from django.db import models
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
    has_sizes = models.BooleanField(default=False, null=True, blank=True)
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
            quality=75,
            upload_to='product_image/',
            force_format='WEBP',
            null=True,
            blank=True
        )

    def __str__(self):
        return self.name
