from datetime import datetime
import pandas as pd

class DeliveryAgent:
    """Agent 3A: Investigates delivery timestamps and seller handoff variances."""

    def investigate(self, order_data: dict, items_data: list) -> dict:
        def format_ts(ts):
            if ts is None or pd.isna(ts) or str(ts).strip().lower() in ["nan", "nat", "none", ""]:
                return None
            return str(ts)

        if not order_data or not items_data:
            return {
                "delivered_at": format_ts(order_data.get("order_delivered_customer_date")) if order_data else None,
                "estimated_delivery_at": format_ts(order_data.get("order_estimated_delivery_date")) if order_data else None,
                "carrier_handoff_at": format_ts(order_data.get("order_delivered_carrier_date")) if order_data else None,
                "delivery_variance_hours": None,
                "seller_handoff_analysis": [],
                "late_handoff_seller_ids": []
            }

        delivered_at = order_data.get("order_delivered_customer_date")
        estimated_at = order_data.get("order_estimated_delivery_date")
        carrier_handoff_at = order_data.get("order_delivered_carrier_date")

        def format_ts(ts):
            if ts is None or pd.isna(ts) or str(ts).strip().lower() in ["nan", "nat", "none", ""]:
                return None
            return str(ts)

        delivery_variance_hours = None
        if delivered_at and estimated_at and not pd.isna(delivered_at) and not pd.isna(estimated_at):
            dt_del = pd.to_datetime(delivered_at)
            dt_est = pd.to_datetime(estimated_at)
            delivery_variance_hours = round((dt_del - dt_est).total_seconds() / 3600.0, 2)

        seller_handoff_analysis = []
        late_handoff_seller_ids = []

        dt_carrier = pd.to_datetime(carrier_handoff_at) if carrier_handoff_at and not pd.isna(carrier_handoff_at) else None
        
        seller_limits = {}
        for item in items_data:
            sid = item.get("seller_id")
            limit_at = item.get("shipping_limit_date")
            if sid and limit_at and not pd.isna(limit_at):
                if sid not in seller_limits or limit_at < seller_limits[sid]:
                    seller_limits[sid] = limit_at

        for sid, limit_at in seller_limits.items():
            dt_limit = pd.to_datetime(limit_at)
            h_var = round((dt_carrier - dt_limit).total_seconds() / 3600.0, 2) if dt_carrier is not None else None
            is_late = h_var > 0 if h_var is not None else False
            
            seller_handoff_analysis.append({
                "seller_id": sid,
                "shipping_limit_at": format_ts(limit_at),
                "handoff_variance_hours": h_var,
                "late_handoff": is_late
            })
            if is_late and sid not in late_handoff_seller_ids:
                late_handoff_seller_ids.append(sid)

        return {
            "delivered_at": format_ts(delivered_at),
            "estimated_delivery_at": format_ts(estimated_at),
            "carrier_handoff_at": format_ts(carrier_handoff_at),
            "delivery_variance_hours": delivery_variance_hours,
            "seller_handoff_analysis": seller_handoff_analysis,
            "late_handoff_seller_ids": late_handoff_seller_ids
        }
