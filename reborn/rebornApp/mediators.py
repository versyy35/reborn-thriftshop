from .models import Order, Payment
from .payment_strategies import PaymentStrategy

class CheckoutMediator:
    def __init__(self, cart, buyer, payment_strategy: PaymentStrategy, payment_details: dict, shipping_address: str):
        self.cart = cart
        self.buyer = buyer
        self.payment_strategy = payment_strategy
        self.payment_details = payment_details
        self.shipping_address = shipping_address

    def checkout(self):
        try:
            orders = Order.create_orders_from_cart(self.cart, self.shipping_address)
        except ValueError as e:
            raise e

        if not orders:
            raise ValueError("No orders were created.")

        for order in orders:
            success, transaction_id = self.payment_strategy.process_payment(
                amount=order.total,
                payment_details=self.payment_details
            )

            if success:
                payment = Payment.objects.create(
                    order=order,
                    amount=order.total,
                    method='credit_card',
                    status='completed',
                    transaction_id=transaction_id
                )
                order.status = 'pending'
                order.save()
            else:
                Payment.objects.create(
                    order=order,
                    amount=order.total,
                    method='credit_card',
                    status='failed'
                )
                raise Exception(f"Payment failed for Order #{order.id}")

        return orders
