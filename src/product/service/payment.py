class PaymentService:
    @staticmethod
    def confirm_payment(payment_key: str, amount: int) -> bool:
        # 외부 API 호출 -> 결제 검증
        if payment_key and amount:
            return True
        return False


payment_service = PaymentService()
