# Product model will save as it is in the database

class ProductModel:
    def __init__(self, prod_id, barcode, product_name, category, purchase_price, selling_price, qty, reorder_level, gst_rate):
        self.prod_id = prod_id
        self.barcode = barcode
        self.product_name = product_name
        self.category = category
        self.purchase_price = purchase_price
        self.selling_price = selling_price
        self.qty = qty
        self.reorder_level = reorder_level
        self.gst_rate = gst_rate

    def to_dict(self):
        return {
            "prod_id": self.prod_id,
            "barcode": self.barcode,
            "product_name": self.product_name,
            "category": self.category,
            "purchase_price": self.purchase_price,
            "selling_price": self.selling_price,
            "qty": self.qty,
            "reorder_level": self.reorder_level,
            "gst_rate": self.gst_rate
        }