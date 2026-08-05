import pandas as pd
from typing import Dict
from src.config import DATA_DIR

class DataLoader:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataLoader, cls).__new__(cls)
            cls._instance._load_data()
        return cls._instance

    def _load_data(self):
        self.orders = pd.read_csv(DATA_DIR / "olist_orders_dataset.csv")
        self.customers = pd.read_csv(DATA_DIR / "olist_customers_dataset.csv")
        self.order_items = pd.read_csv(DATA_DIR / "olist_order_items_dataset.csv")
        self.order_payments = pd.read_csv(DATA_DIR / "olist_order_payments_dataset.csv")
        self.order_reviews = pd.read_csv(DATA_DIR / "olist_order_reviews_dataset.csv")
        self.products = pd.read_csv(DATA_DIR / "olist_products_dataset.csv")
        self.sellers = pd.read_csv(DATA_DIR / "olist_sellers_dataset.csv")
        self.translations = pd.read_csv(DATA_DIR / "product_category_name_translation.csv")
        
        # Build category translation dictionary
        self.cat_map = dict(zip(self.translations['product_category_name'], self.translations['product_category_name_english']))

    def get_order(self, order_id: str) -> Dict:
        row = self.orders[self.orders['order_id'] == order_id]
        if row.empty:
            return None
        return row.iloc[0].to_dict()

    def get_customer(self, customer_id: str) -> Dict:
        row = self.customers[self.customers['customer_id'] == customer_id]
        if row.empty:
            return None
        return row.iloc[0].to_dict()

    def get_customer_history(self, customer_unique_id: str) -> list:
        custs = self.customers[self.customers['customer_unique_id'] == customer_unique_id]
        c_ids = custs['customer_id'].tolist()
        related = self.orders[self.orders['customer_id'].isin(c_ids)]['order_id'].tolist()
        return related

    def get_order_items(self, order_id: str) -> list:
        items = self.order_items[self.order_items['order_id'] == order_id]
        return items.to_dict('records')

    def get_order_payments(self, order_id: str) -> list:
        payments = self.order_payments[self.order_payments['order_id'] == order_id]
        return payments.to_dict('records')

    def get_order_reviews(self, order_id: str) -> list:
        reviews = self.order_reviews[self.order_reviews['order_id'] == order_id]
        return reviews.to_dict('records')

    def get_product(self, product_id: str) -> Dict:
        row = self.products[self.products['product_id'] == product_id]
        if row.empty:
            return None
        res = row.iloc[0].to_dict()
        cat_pt = res.get('product_category_name')
        res['category_english'] = self.cat_map.get(cat_pt, cat_pt)
        return res
