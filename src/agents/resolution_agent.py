import json

class ResolutionAgent:
    """Agent 6: Formulates final investigation summary and calculates confidence score."""

    def synthesize(self, case_id: str, order_id: str, triage_res: dict, delivery_res: dict, financial_res: dict, context_res: dict, policy_res: dict) -> dict:
        primary_issue = policy_res.get("primary_issue")
        
        # Determine confidence score based on policy clarity
        confidence = 0.95 if primary_issue in ["canceled_order_paid", "unavailable_order_paid", "late_delivery_seller", "late_delivery_logistics", "valid_split_payment"] else 0.90
        
        summary = (
            f"Case {case_id} for order {order_id} analyzed under EC_POLICY_V2. "
            f"Primary issue identified as {primary_issue} with root cause {policy_res.get('root_cause_code')}. "
            f"Refund type: {policy_res.get('refund_type')} ({policy_res.get('refund_amount_brl')} BRL)."
        )

        return {
            "summary": summary,
            "confidence": confidence
        }
