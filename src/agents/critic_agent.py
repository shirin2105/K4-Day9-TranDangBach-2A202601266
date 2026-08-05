class CriticAgent:
    """Agent 5: Validates policy adjudication decision, formatting rules and evidence IDs."""

    def review(self, order_id: str, items_data: list, payments_data: list, policy_res: dict) -> dict:
        is_valid = True
        feedback = []

        # Check evidence ID formatting and existence
        evidence_ids = policy_res.get("evidence_ids", [])
        expected_order_ev = f"order:{order_id}"
        if expected_order_ev not in evidence_ids:
            is_valid = False
            feedback.append(f"Missing {expected_order_ev} in evidence_ids.")

        for item in items_data:
            expected_item_ev = f"item:{order_id}:{item.get('order_item_id')}"
            if expected_item_ev not in evidence_ids:
                is_valid = False
                feedback.append(f"Missing {expected_item_ev} in evidence_ids.")

        for pay in payments_data:
            expected_pay_ev = f"payment:{order_id}:{pay.get('payment_sequential')}"
            if expected_pay_ev not in evidence_ids:
                is_valid = False
                feedback.append(f"Missing {expected_pay_ev} in evidence_ids.")

        root_cause = policy_res.get("root_cause_code")
        if root_cause and f"policy:{root_cause}" not in evidence_ids:
            is_valid = False
            feedback.append(f"Missing policy:{root_cause} in evidence_ids.")

        return {
            "is_valid": is_valid,
            "feedback": feedback
        }
