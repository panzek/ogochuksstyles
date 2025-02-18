from django.shortcuts import render, redirect
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.conf import settings
import smtplib
from .forms import ContactForm


def contact(request):
    """
    A view to render form in template
    """

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            customer_message = form.save()
            contact_email = customer_message.email
            contact_subject = customer_message.subject
            contact_message = customer_message.message

            # Handle SMTP Exceptions
            try:
                send_mail(
                    contact_subject,
                    contact_message,
                    contact_email,
                    ['info@ogochuksstyles.com',
                        settings.DEFAULT_FROM_EMAIL],
                )
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            except smtplib.SMTPException as e:
                return HttpResponse(f"SMTP error occurred: {str(e)}")
            except Exception as e:
                return HttpResponse(f"An error occurred: {str(e)}")

            # redirect to a new url
            return redirect("/thank_you")

        else:
            # if form is not valid, re-render the form with errors
            template = 'contact/contact.html'
            context = {
                'form': form,
            }
            return render(request, template, context)
    else:
        form = ContactForm()

        template = 'contact/contact.html'
        context = {
            'form': form,
        }

    return render(request, template, context)


def about(request):
    """
    A view to render an About page
    """

    context = {}
    return render(request, 'home/about.html', context)
