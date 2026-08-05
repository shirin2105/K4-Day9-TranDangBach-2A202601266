import pandas as pd

class FinancialAgent:
    """Agent 3B: Reconciles payments vs expected item prices and freight values."""

    def investigate(self, items_data: list, payments_data: list) -> dict:
        if not items_data:
            return {
                "currency": "BRL",
                "item_total_brl": None,
                "freight_total_brl": None,
                "expected_total_brl": None,
                "payment_total_brl": round(sum(p.get("payment_value", 0.0) for p in payments_data), 2) if payments_data else 0.0,
                "difference_brl": None,
                "reconciled": None,
                "payment_types": list(set(p.get("payment_type") for p in payments_data if p.get("payment_type")))
            }

        item_total = sum(i.get("price", 0.0) for i in items_data)
        freight_total = sum(i.get("freight_value", 0.0) for i in items_data)
        expected_total = item_total + freight_total
        payment_total = sum(p.get("payment_value", 0.0) for p in payments_data)
        
        diff = payment_total - expected_total
        reconciled = abs(diff) <= 0.10

        payment_types = list(dict.fromkeys(p.get("payment_type") for p in payments_data if p.get("payment_type")))

        return {
            "currency": "BRL",
            "item_total_brl": round(item_total, 2),
            "freight_total_brl": round(freight_total, 2),
            "expected_total_brl": round(expected_total, 2),
            "payment_total_brl": round(payment_total, 2),
            "difference_brl": round(diff, 2),
            "reconciled": reconciled,
            "payment_types": payment_types
        }
