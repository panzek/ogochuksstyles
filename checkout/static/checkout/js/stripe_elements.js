/*
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment
    CSS from here: https://docs.stripe.com/js  
*/


var stripePublicKey = $('#id_stripe_public_key').text().slice(1, -1);
var clientSecret = $('#id_client_secret').text().slice(1, -1);
var stripe = Stripe(stripePublicKey);

const appearance = {
    theme: 'flat',
    variables: {
        colorPrimary: '#0570de',
        colorBackground: '#ffffff',
        colorText: '#30313d',
        colorDanger: '#df1b41',
        fontFamily: 'Ideal Sans, system-ui, sans-serif',
        spacingUnit: '2px',
        borderRadius: '4px',
    }
};

const elements = stripe.elements({ clientSecret, appearance });

// Define options for payment Element
const paymentElementOptions = {
    layout: 'auto'
};

// Create and mount the Payment Element
const paymentElement = elements.create('payment', paymentElementOptions);
paymentElement.mount('#payment-element');

// Handle real-time validation errors on the payment element
paymentElement.addEventListener('change', function (event) {
    var errorDiv = document.getElementById('card-errors');
    if (event.error) {
        var html = `
            <span class="icon" role="alert">
                <i class="fas fa-times"></i>
            </span>
            <span>${event.error.message}</span>
        `;
        $(errorDiv).html(html);
    } else {
        errorDiv.textContent = '';
    }
});

// Handle form submission
var form = document.getElementById('payment-form');

var form = document.getElementById('payment-form');
form.addEventListener('submit', async function (ev) {
    ev.preventDefault();

    // Disable button to prevent multiple submissions
    $('#submit-button').attr('disabled', true);
    $('#payment-form').fadeToggle(100);
    $('#loading-overlay').fadeToggle(100);

    var saveInfo = Boolean($('#id-save-info').attr('checked'));
    var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
    var postData = {
        'csrfmiddlewaretoken': csrfToken,
        'client_secret': clientSecret,
        'save_info': saveInfo,
        'full_name': $.trim(form.full_name.value),
        'email': $.trim(form.email.value),
        'phone_number': $.trim(form.phone_number.value),
        'country': $.trim(form.country.value),
        'postcode': $.trim(form.postcode.value),
        'town_or_city': $.trim(form.town_or_city.value),
        'street_address1': $.trim(form.street_address1.value),
        'street_address2': $.trim(form.street_address2.value),
        'county': $.trim(form.county.value),
    };

    var url = '/checkout/cache_checkout_data/';

    const confirmParams = {
        return_url: 'https://ogochuksstyles.com/checkout/checkout_success/',
        payment_method_data: {
            billing_details: {
                name: $.trim(form.full_name.value),
                phone: $.trim(form.phone_number.value),
                email: $.trim(form.email.value),
                address: {
                    line1: $.trim(form.street_address1.value),
                    line2: $.trim(form.street_address2.value),
                    city: $.trim(form.town_or_city.value),
                    state: $.trim(form.county.value),
                    country: $.trim(form.country.value),
                },
            },
        },
        shipping: {
            name: $.trim(form.full_name.value),
            phone: $.trim(form.phone_number.value),
            address: {
                line1: $.trim(form.street_address1.value),
                line2: $.trim(form.street_address2.value),
                city: $.trim(form.town_or_city.value),
                state: $.trim(form.county.value),
                postal_code: $.trim(form.postcode.value),
                country: $.trim(form.country.value),
            },
        },
    };

    console.log("Calling stripe.confirmPayment with:", {
        elements: elements instanceof Object ? "[Elements object]" : elements,
        confirmParams: JSON.stringify(confirmParams, null, 2)
    });

    try {
        await $.post(url, postData).promise();
        const result = await stripe.confirmPayment({
            elements,
            confirmParams
        });

        if (result.error) {
            var errorDiv = document.getElementById('card-errors');
            var html = `
                <span class="icon" role="alert">
                    <i class="fas fa-times"></i>
                </span>
                <span>${result.error.message}</span>`;
            $(errorDiv).html(html);
            $('#payment-form').fadeToggle(100);
            $('#loading-overlay').fadeToggle(100);
            $('#submit-button').attr('disabled', false);
        } else {
            console.log("Payment succeeded, redirecting via Stripe...");
        }
    } catch (error) {
        console.error("Error during payment confirmation:", error);
        location.reload();
    }
});