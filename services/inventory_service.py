import logging
import datetime
from utils.db_client import DBClient

class InventoryService:
    def __init__(self):
        self.db = DBClient.get_db()
        self.products_coll = self.db['products']
        self.categories_coll = self.db['categories']
        
        # Auto seed dummy data if empty
        if self.products_coll.count_documents({}) == 0:
            self._seed_dummy_data_mongo()

    def _seed_dummy_data_mongo(self):
        logging.info("Seeding dummy product data to MongoDB...")
        seed_products = [
            {"prod_id": "P001", "barcode": "1001", "product_name": "Whole Wheat Bread", "category": "Bakery", "purchase_price": 30.0, "selling_price": 40.0, "qty": 50, "reorder_level": 10, "gst_rate": 5},
            {"prod_id": "P002", "barcode": "1002", "product_name": "Toned Milk 1L", "category": "Dairy", "purchase_price": 50.0, "selling_price": 65.0, "qty": 100, "reorder_level": 20, "gst_rate": 5},
            {"prod_id": "P003", "barcode": "1003", "product_name": "Amul Butter 500g", "category": "Dairy", "purchase_price": 200.0, "selling_price": 260.0, "qty": 40, "reorder_level": 10, "gst_rate": 12},
            {"prod_id": "P004", "barcode": "1007", "product_name": "Basmati Rice 5kg", "category": "Pantry", "purchase_price": 400.0, "selling_price": 450.0, "qty": 8, "reorder_level": 20, "gst_rate": 5}, # low stock example
            {"prod_id": "P005", "barcode": "1024", "product_name": "Coca Cola 1.25L", "category": "Beverages", "purchase_price": 50.0, "selling_price": 65.0, "qty": 80, "reorder_level": 20, "gst_rate": 18}
        ]
        self.products_coll.insert_many(seed_products)
        
        categories = [{"cat_id": "C01", "cat_name": "Bakery", "desc": ""}, 
                      {"cat_id": "C02", "cat_name": "Dairy", "desc": ""}, 
                      {"cat_id": "C03", "cat_name": "Pantry", "desc": ""}, 
                      {"cat_id": "C04", "cat_name": "Beverages", "desc": ""}]
        if self.categories_coll.count_documents({}) == 0:
            self.categories_coll.insert_many(categories)
            
        customers_coll = self.db['customers']
        if customers_coll.count_documents({}) == 0:
            customers_coll.insert_many([
                {"cust_id": "CUST001", "cust_name": "John Doe", "phone": "9876543210", "email": "john@test.com", "address": "123 Main St"}
            ])
            
        bills_coll = self.db['bills']
        if bills_coll.count_documents({}) == 0:
            today_str = datetime.datetime.now().strftime("%Y-%m-%d")
            bills_coll.insert_many([
                {"bill_no": "B001", "date": today_str, "cust_name": "John Doe", "pay_mode": "UPI", "items": [], "subtotal": 100, "discount": 10, "gst": 5, "grand_total": 95},
                {"bill_no": "B002", "date": today_str, "cust_name": "Cash Customer", "pay_mode": "Cash", "items": [], "subtotal": 200, "discount": 0, "gst": 10, "grand_total": 210}
            ])
            
        logging.info("Seeding complete.")

    def get_dashboard_stats(self):
        """Fetches aggregated statistics for the main dashboard."""
        try:
            total_products = self.products_coll.count_documents({})
            low_stock_items = self.products_coll.count_documents({"$expr": {"$lte": ["$qty", "$reorder_level"]}})
            total_categories = self.categories_coll.count_documents({})
            
            bills_coll = self.db['bills']
            today_str = datetime.datetime.now().strftime("%Y-%m-%d")
            today_bills = bills_coll.count_documents({"date": {"$regex": f"^{today_str}"}})
            
            pipeline = [
                {"$match": {"date": {"$regex": f"^{today_str}"}}},
                {"$group": {"_id": None, "total_sales": {"$sum": "$grand_total"}}}
            ]
            sales_result = list(bills_coll.aggregate(pipeline))
            todays_sales = sales_result[0]["total_sales"] if sales_result else 0
            
            customers_coll = self.db['customers']
            total_customers = customers_coll.count_documents({})
            
            return {
                "total_products": total_products,
                "low_stock_items": low_stock_items,
                "total_categories": total_categories,
                "today_bills": today_bills,
                "todays_sales": todays_sales,
                "total_customers": total_customers
            }
        except Exception as e:
            logging.error(f"Error fetching dashboard stats: {e}")
            return None