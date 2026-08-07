from decimal import Decimal

from django.conf import settings
from stripe import StripeClient

client = StripeClient(settings.STRIPE_API_KEY)


def create_stripe_product(product_name: str) -> dict:
    product = client.v1.products.create({"name": product_name})
    return product.to_dict()


def create_stripe_price(product_id: str, amount: Decimal) -> dict:
    price = client.v1.prices.create(
        {
            "currency": "rub",
            "unit_amount": int(amount * 100),
            "product": product_id,
        }
    )
    return price.to_dict()


def create_stripe_session(price_id: str) -> dict:
    session = client.v1.checkout.sessions.create(
        {
            "success_url": settings.STRIPE_SUCCESS_URL,
            "cancel_url": settings.STRIPE_CANCEL_URL,
            "mode": "payment",
            "line_items": [
                {
                    "price": price_id,
                    "quantity": 1,
                }
            ],
        }
    )
    return session.to_dict()
