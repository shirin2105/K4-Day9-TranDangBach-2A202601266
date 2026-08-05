class ClaimTriageAgent:
    """Agent 2: Analyzes customer request message and determines claim intent/type."""

    def analyze(self, customer_request: dict) -> dict:
        message = customer_request.get("message", "").lower()
        
        # Categorize claim type based on keywords
        if any(w in message for w in ["trễ", "chậm", "muộn", "late", "delay", "chưa nhận"]):
            claim_type = "delivery_delay"
        elif any(w in message for w in ["hủy", "cancellation", "canceled", "cancel"]):
            claim_type = "cancellation"
        elif any(w in message for w in ["tiền", "thanh toán", "payment", "price", "charge", "chênh lệch"]):
            claim_type = "payment_dispute"
        else:
            claim_type = "general_investigation"
            
        return {
            "claim_type": claim_type,
            "raw_message": message
        }
