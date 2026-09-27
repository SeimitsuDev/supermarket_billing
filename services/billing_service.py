from models.cart_item import CartItemModel
import datetime

class BillingService:
    def __init__(self, inventory_service):
        self.current_cart = []
        self._inventory_service = inventory_service
        self.gst_rate = 0.05  # 5% GST default
        self.apply_gst = True

    def add_to_cart(self, barcode: str, quantity: int) -> bool:
        # Fetch from MongoDB via inventory service
        product_doc = self._inventory_service.products_coll.find_one({"barcode": barcode})
        if not product_doc or product_doc.get("qty", 0) < quantity:
            return False

        # convert product_doc to a CartItem
        class MockProduct:
            def __init__(self, doc):
                self.doc = doc
                self.selling_price = doc.get("selling_price", 0)
                
            def get(self, key, default=None):
                return self.doc.get(key, default)

        p = MockProduct(product_doc)
        item = CartItemModel(p, quantity, 0)
        
        # Check if already in cart to increment qty
        for existing in self.current_cart:
            if existing.product.get('barcode') == barcode:
                existing.qty += quantity
                existing.total_amt = (existing.product.selling_price * existing.qty) - existing.discount_amt
                return True
                
        self.current_cart.append(item)
        return True

    def calculate_totals(self) -> dict:
        subtotal = sum(item.total_amt for item in self.current_cart)
        gst = subtotal * self.gst_rate if self.apply_gst else 0
        return {
            "subtotal": subtotal,
            "gst": gst,
            "total": subtotal + gst
        }
        
    def generate_bill(self, pay_mode: str) -> str:
        if not self.current_cart:
            return None
            
        totals = self.calculate_totals()
        bill_no = f"B{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        today_str = datetime.datetime.now().strftime("%Y-%m-%d")
        
        items_data = []
        for item in self.current_cart:
            items_data.append({
                "product_name": item.product.get('product_name'),
                "qty": item.qty,
                "price": item.product.selling_price,
                "amount": item.total_amt
            })
            
            # Reduce inventory stock
            self._inventory_service.products_coll.update_one(
                {"barcode": item.product.get('barcode')},
                {"$inc": {"qty": -item.qty}}
            )
            
        bill_doc = {
            "bill_no": bill_no,
            "date": today_str,
            "cust_name": "Walk-in Customer",
            "pay_mode": pay_mode,
            "items": items_data,
            "subtotal": totals["subtotal"],
            "discount": 0,
            "gst": totals["gst"],
            "grand_total": totals["total"]
        }
        
        self._inventory_service.db['bills'].insert_one(bill_doc)
        return bill_no