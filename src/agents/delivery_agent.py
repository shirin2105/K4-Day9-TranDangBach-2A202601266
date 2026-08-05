from datetime import datetime
import pandas as pd

class DeliveryAgent:
    """Agent 3A: Investigates delivery timestamps and seller handoff variances."""

    def investigate(self, order_data: dict, items_data: list) -> dict:
        if not order_data:
            return {}

        delivered_at = order_data.get("order_delivered_customer_date")
        estimated_at = order_data.get("order_estimated_delivery_date")
        carrier_handoff_at = order_data.get("order_delivered_carrier_date")

        # Format ISO timestamp string helpers
        def format_ts(ts):
            if pd.isna(ts) or not ts:
                return None
            return str(ts)

        delivery_variance_hours = None
        if delivered_at and estimated_at and not pd.isna(delivered_at) and not pd.isna(estimated_at):
            dt_del = pd.to_datetime(delivered_at)
            dt_est = pd.to_datetime(estimated_at)
            delivery_variance_hours = round((dt_del - dt_est).total_seconds() / 3600.0, 2)

        seller_handoff_analysis = []
        late_handoff_seller_ids = []

        if carrier_handoff_at and not pd.isna(carrier_handoff_at):
            dt_carrier = pd.to_datetime(carrier_handoff_at)
            
            # Map items to seller limits
            for item in items_data:
                seller_id = item.get("seller_id")
                limit_at = item.get("shipping_limit_date")
                if limit_at and not pd.isna(limit_at):
                    dt_limit = pd.to_datetime(limit_at)
                    h_var = round((dt_carrier - dt_limit).total_seconds() / 3600.0, 2)
                    is_late = h_var > 0
                    
                    seller_handoff_analysis.append({
                        "seller_id": seller_id,
                        "shipping_limit_at": format_ts(limit_at),
                        "handoff_variance_hours": h_var,
                        "late_handoff": is_late
                    })
                    if is_late and seller_id not in late_handoff_seller_ids:
                        late_handoff_seller_ids.append(seller_id)

        return {
            "delivered_at": format_ts(delivered_at),
            "estimated_delivery_at": format_ts(estimated_at),
            "carrier_handoff_at": format_ts(carrier_handoff_at),
            "delivery_variance_hours": delivery_variance_hours,
            "seller_handoff_analysis": seller_handoff_analysis,
            "late_handoff_seller_ids": late_handoff_seller_ids
        }
