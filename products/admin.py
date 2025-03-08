from django.contrib import admin
from .models import Product, Category, Review

# Register your models here.


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'sku',
        'name',
        'category',
        'price',
        'rating',
        'image',
    )

    ordering = ('sku',)


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'friendly_name',
        'name',
    )

from testimonials.models import Testimonial

# Register models here.
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """ Add Review model to admin page"""
    list_filter = ('created_on', 'updated_on', 'approved',)
    list_display = ('name', 'review', 'created_on', 'updated_on', 'approved', 'user',)
    search_fields = ('name', 'review',)
    actions = ['approve_testimonials']

    def approve_reviews(self, request, queryset):
        queryset.update(approved=True)

admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
