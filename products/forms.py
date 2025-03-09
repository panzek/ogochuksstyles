from django import forms
from .widgets import CustomClearableFileInput
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from crispy_bootstrap5.bootstrap5 import FloatingField

from .models import Product, Category, Review


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

    image = forms.ImageField(
            label='Image', 
            required=False, 
            widget=CustomClearableFileInput
        )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = Category.objects.all()
        friendly_names = [(c.id, c.get_friendly_name()) for c in categories]

        self.fields['category'].choices = friendly_names
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'border-black rounded-0'


class ReviewForm(forms.ModelForm):
    """
    A form for customers to submit product ratings and reviews.
    """

    class Meta:
        model = Review
        fields = ('name', 'title', 'review', 'rating')

        labels = {
            'name': 'Enter your full name',
            'title': 'Enter review title', 
            'review': 'Write your review', 
            'rating': 'Rate the product',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False  # Prevents crispy form from rending form tags
        self.helper.layout = Layout(
            FloatingField("name"),
            FloatingField("title"),
            FloatingField("review"),
            FloatingField("rating"),
        )
