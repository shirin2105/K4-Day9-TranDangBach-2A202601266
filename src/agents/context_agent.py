from src.data_loader import DataLoader

class ContextAgent:
    """Agent 3C: Retrieves customer history, product details, seller list and category names."""

    def __init__(self):
        self.db = DataLoader()

    def investigate(self, order_id: str, customer_id: str, items_data: list) -> dict:
        customer_info = self.db.get_customer(customer_id)
        cust_unique_id = customer_info.get("customer_unique_id") if customer_info else None
        
        related_orders = []
        if cust_unique_id:
            all_orders = self.db.get_customer_history(cust_unique_id)
            related_orders = [oid for oid in all_orders if oid != order_id]

        product_ids = []
        category_names = []
        seller_ids = []

        for item in items_data:
            pid = item.get("product_id")
            sid = item.get("seller_id")
            if pid and pid not in product_ids:
                product_ids.append(pid)
                prod = self.db.get_product(pid)
                if prod:
                    cat = prod.get("product_category_name")
                    if cat and cat not in category_names:
                        category_names.append(cat)

            if sid and sid not in seller_ids:
                seller_ids.append(sid)

        return {
            "customer_context": {
                "customer_unique_id": cust_unique_id,
                "related_order_ids": related_orders
            },
            "product_context": {
                "product_ids": product_ids,
                "category_names": category_names
            },
            "seller_ids": seller_ids
        }
