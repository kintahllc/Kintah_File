from django.conf import settings
import stripe

secret_key = settings.STRIPE_SECRET_KEY
stripe.api_key = secret_key

def create_stripe_product_and_price(product_name, unit_price, currency, interval, interval_count=1):
    try:
        # Create a product in Stripe
        product = stripe.Product.create(name=product_name)

        # Create a price for this product
        price = stripe.Price.create(
            unit_amount=int(unit_price * 100),  # Price in cents
            currency=currency,
            product=product.id,
            recurring={'interval': interval, 'interval_count': interval_count},
            billing_scheme='per_unit'
        )

        return product.id, price.id
    except stripe.error.StripeError as e:
        # Handle any Stripe API errors
        print(f"Stripe Error: {e}")
        return None, None

def create_stripe_customer(email, name):
    """Create a customer in Stripe and return the customer ID."""
    customer = stripe.Customer.create(
        email=email,
        name=name,
    )
    return customer.id

def create_subscription(customer_id, price_id):
    """Create a subscription to the price with a specific price ID for a customer."""
    subscription = stripe.Subscription.create(
        customer=customer_id,
        items=[{'price': price_id}],
        payment_behavior='default_incomplete',  # Allow incomplete payments
        expand=['latest_invoice.payment_intent']
    )
    return subscription



def create_payment_intent(customer_id, amount, currency, payment_method):
    """Create a PaymentIntent for collecting upfront payment."""
    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Convert to cents
            currency=currency,
            customer=customer_id,
            payment_method=payment_method.id,
            confirm=True,
            description='Payment for Analytics Services',
            return_url = 'https://example.com/success/'



        )
        return payment_intent
    except stripe.error.StripeError as e:
        # Handle any Stripe API errors
        print(f"Stripe Error: {e}")
        return str(e)