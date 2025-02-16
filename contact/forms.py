import re
from django import forms
from contact.models import Contact
from django_recaptcha.fields import ReCaptchaField
from django.core.exceptions import ValidationError


class ContactForm(forms.ModelForm):
    """
    A form for customers to send messages to the store owner.
    """

    recaptcha = ReCaptchaField()
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))

    class Meta:
        model = Contact
        fields = ('name', 'email', 'subject', 'message', 'recaptcha')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            'name': 'Enter your name here',
            'email': 'Enter your email address',  
            'subject': 'Enter your message subject',  
            'message': 'Enter your message here',
        }

        self.fields['name'].widget.attrs['autofocus'] = True
        for field in self.fields:
            if field in placeholders:
                self.fields[field].widget.attrs['placeholder'] = placeholders[field]
                self.fields[field].widget.attrs['class'] = 'form-control input-primary rounded max-w-full'

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()  # Strip leading/trailing spaces
        if not re.match(r'^[a-zA-Z\s\'-]+$', name):  # Allows letters, spaces, hyphens, and apostrophes
            raise ValidationError("Name should contain only letters and spaces.")
        if len(name) < 3:
            raise ValidationError("Name should be at least 3 characters long.")
        return name

    def clean_message(self):
        message = self.cleaned_data.get('message', '').strip()  # Strip unnecessary spaces
        if len(message) < 10:
            raise ValidationError("Message should be at least 10 characters long.")
        return message

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()  # Convert to lowercase
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            raise ValidationError("Invalid email format. Please enter a valid email address.")
        return email
