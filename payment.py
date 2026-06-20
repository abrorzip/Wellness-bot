import hashlib
import time
import requests
from config import (
    PAYME_MERCHANT_ID, PAYME_SECRET_KEY,
    CLICK_MERCHANT_ID, CLICK_SECRET_KEY,
    COURSE_PRICE
)


class PaymePayment:
    def __init__(self):
        self.merchant_id = PAYME_MERCHANT_ID
        self.secret_key = PAYME_SECRET_KEY
    
    def create_payment(self, amount, order_id, return_url):
        return f"https://paycom.uz/{self.merchant_id}?amount={amount}&account[order_id]={order_id}"
    
    def verify_payment(self, params):
        try:
            sign_string = f"{params['merchant_trans_id']}{params['amount']}{self.secret_key}{params.get('account[order_id]', '')}{params['transaction_time']}"
            expected_sign = hashlib.md5(sign_string.encode()).hexdigest()
            return params.get("sign") == expected_sign
        except Exception:
            return False


class ClickPayment:
    def __init__(self):
        self.merchant_id = CLICK_MERCHANT_ID
        self.secret_key = CLICK_SECRET_KEY
        self.api_url = "https://api.click.uz/v1/merchant"
    
    def generate_token(self, amount, order_id):
        try:
            timestamp = int(time.time())
            sign_string = f"{self.merchant_id}{amount}{order_id}{self.secret_key}{timestamp}"
            sign = hashlib.md5(sign_string.encode()).hexdigest()
            
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            payload = {
                "merchant_id": self.merchant_id,
                "amount": amount,
                "order_id": order_id,
                "sign": sign
            }
            
            response = requests.post(
                f"{self.api_url}/generate_token",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("token"):
                    return f"https://pay.click.uz/{data['token']}"
            
            return None
        except Exception as e:
            print(f"Click token generation error: {e}")
            return None
    
    def create_payment(self, amount, order_id, return_url):
        return self.generate_token(amount, order_id)
    
    def verify_payment(self, params):
        try:
            sign_string = f"{params.get('merchant_trans_id', '')}{params.get('amount', 0)}{self.secret_key}"
            expected_sign = hashlib.md5(sign_string.encode()).hexdigest()
            return params.get("sign") == expected_sign
        except Exception:
            return False


def create_course_payment(user_id, payment_method="payme"):
    order_id = f"wellness_{user_id}_{int(time.time())}"
    amount = COURSE_PRICE
    
    if payment_method == "payme":
        payment = PaymePayment()
        return payment.create_payment(amount, order_id, f"https://your-domain.com/payment/callback?order_id={order_id}")
    elif payment_method == "click":
        payment = ClickPayment()
        return payment.create_payment(amount, order_id, f"https://your-domain.com/payment/callback?order_id={order_id}")
    
    return None


def verify_course_payment(params, payment_method="payme"):
    if payment_method == "payme":
        payment = PaymePayment()
        return payment.verify_payment(params)
    elif payment_method == "click":
        payment = ClickPayment()
        return payment.verify_payment(params)
    
    return False
