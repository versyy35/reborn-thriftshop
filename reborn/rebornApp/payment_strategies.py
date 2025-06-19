from abc import ABC, abstractmethod
import random
import string

class PaymentStrategy(ABC):
    @abstractmethod
    def process_payment(self, amount: float, payment_details: dict) -> (bool, str):
        pass

class CreditCardPaymentStrategy(PaymentStrategy):
    def process_payment(self, amount: float, payment_details: dict) -> (bool, str):
        print(f"Processing RM {amount} via Credit Card...")
        
        card_number = payment_details.get('card_number')
        if not card_number:
             raise ValueError("Credit card number is required.")
        
        transaction_id = 'CC_' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
        print(f"Successfully processed payment. Transaction ID: {transaction_id}")
        return True, transaction_id

class PayPalPaymentStrategy(PaymentStrategy):
    def process_payment(self, amount: float, payment_details: dict) -> (bool, str):
        print(f"Redirecting to PayPal for a payment of RM {amount}...")
        email = payment_details.get('email')
        if not email:
            raise ValueError("PayPal email is required.")

        transaction_id = 'PP_' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
        print(f"Successfully processed PayPal payment. Transaction ID: {transaction_id}")
        return True, transaction_id

def get_payment_strategy(method: str) -> PaymentStrategy:
    if method == 'credit_card':
        return CreditCardPaymentStrategy()
    elif method == 'paypal':
        return PayPalPaymentStrategy()
    else:
        raise ValueError(f"Unknown payment method: {method}")
