class PolicyAgent:
    """Agent 4: Policy Adjudicator applying EC_POLICY_V2 rules strictly."""

    def adjudicate(self, order_data: dict, items_data: list, payments_data: list, delivery_res: dict, financial_res: dict, context_res: dict) -> dict:
        status = order_data.get("order_status") if order_data else None
        payment_total = financial_res.get("payment_total_brl", 0.0)
        freight_total = financial_res.get("freight_total_brl", 0.0) or 0.0
        del_var = delivery_res.get("delivery_variance_hours")
        late_sellers = delivery_res.get("late_handoff_seller_ids", [])
        
        primary_issue = None
        responsible_parties = []
        refund_type = "none"
        refund_amount_brl = 0.0
        root_cause_code = ""
        actions = []

        # 1. Primary issue matching (Strict priority)
        if status == "canceled" and payment_total > 0:
            primary_issue = "canceled_order_paid"
            responsible_parties.append({"party_type": "platform", "party_id": "OLIST_PLATFORM"})
            refund_type = "full_refund"
            refund_amount_brl = payment_total
            root_cause_code = "ORDER_CANCELED_AFTER_PAYMENT"
            actions.append("issue_full_refund")
            
        elif status == "unavailable" and payment_total > 0:
            primary_issue = "unavailable_order_paid"
            responsible_parties.append({"party_type": "platform", "party_id": "OLIST_PLATFORM"})
            refund_type = "full_refund"
            refund_amount_brl = payment_total
            root_cause_code = "ORDER_UNAVAILABLE_AFTER_PAYMENT"
            actions.append("issue_full_refund")

        elif del_var is not None and del_var > 0 and len(late_sellers) > 0:
            primary_issue = "late_delivery_seller"
            for sid in late_sellers:
                responsible_parties.append({"party_type": "seller", "party_id": sid})
            refund_type = "freight_refund"
            refund_amount_brl = freight_total
            root_cause_code = "SELLER_HANDOFF_AFTER_LIMIT"
            actions.append("refund_freight")

        elif del_var is not None and del_var > 0 and len(late_sellers) == 0:
            primary_issue = "late_delivery_logistics"
            responsible_parties.append({"party_type": "logistics_provider", "party_id": "LOGISTICS_PROVIDER"})
            refund_type = "freight_refund"
            refund_amount_brl = freight_total
            root_cause_code = "CARRIER_DELIVERED_AFTER_ESTIMATE"
            actions.append("refund_freight")

        elif len(payments_data) >= 2 and financial_res.get("reconciled") is True:
            primary_issue = "valid_split_payment"
            refund_type = "none"
            refund_amount_brl = 0.0
            root_cause_code = "MULTIPLE_PAYMENTS_RECONCILED"
            actions.append("explain_valid_split_payment")

        else:
            primary_issue = "unsupported_late_claim"
            refund_type = "none"
            refund_amount_brl = 0.0
            root_cause_code = "DELIVERY_WITHIN_ESTIMATE"
            actions.append("reject_late_refund")

        # 2. Secondary issues (Exact order)
        secondary_issues = []
        if len(items_data) >= 2:
            secondary_issues.append("multi_item_order")
        
        all_sellers = list(dict.fromkeys(i.get("seller_id") for i in items_data if i.get("seller_id")))
        if len(all_sellers) >= 2:
            secondary_issues.append("multi_seller_order")

        if len(payments_data) >= 2:
            secondary_issues.append("split_payment")

        related_orders = context_res.get("customer_context", {}).get("related_order_ids", [])
        if len(related_orders) > 0:
            secondary_issues.append("repeat_customer")

        cats = context_res.get("product_context", {}).get("category_names", [])
        if len(cats) >= 2:
            secondary_issues.append("multiple_categories")

        # 3. Supplemental Actions
        if primary_issue == "late_delivery_seller":
            actions.append("review_seller_handoff")
        elif primary_issue == "late_delivery_logistics":
            actions.append("review_carrier_delay")

        if primary_issue in ["canceled_order_paid", "unavailable_order_paid"]:
            actions.append("verify_refund_completion")

        if len(all_sellers) >= 2:
            actions.append("coordinate_multi_seller_case")

        if len(payments_data) >= 2 and primary_issue != "valid_split_payment":
            actions.append("verify_payment_allocation")

        # 4. Evidence IDs
        order_id = order_data.get("order_id") if order_data else ""
        evidence_ids = [f"order:{order_id}"]
        
        for item in items_data:
            evidence_ids.append(f"item:{order_id}:{item.get('order_item_id')}")

        for pay in payments_data:
            evidence_ids.append(f"payment:{order_id}:{pay.get('payment_sequential')}")

        for party in responsible_parties:
            if party.get("party_type") == "seller":
                evidence_ids.append(f"seller:{party.get('party_id')}")

        if root_cause_code:
            evidence_ids.append(f"policy:{root_cause_code}")

        case_status = "action_required" if refund_type != "none" or primary_issue in ["canceled_order_paid", "unavailable_order_paid", "late_delivery_seller", "late_delivery_logistics"] else "resolved"

        return {
            "primary_issue": primary_issue,
            "secondary_issues": secondary_issues,
            "case_status": case_status,
            "root_cause_code": root_cause_code,
            "responsible_parties": responsible_parties,
            "refund_type": refund_type,
            "refund_amount_brl": round(refund_amount_brl, 2),
            "actions": actions,
            "evidence_ids": evidence_ids
        }
