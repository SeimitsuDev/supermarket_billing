# To transfer data in valid format
class CartItemModel:
    def __init__(self, product, qty, discount_amt):
        self.product = product
        self.qty = qty
        self.discount_amt = discount_amt
        self.total_amt = (self.product.selling_price * self.qty) - self.discount_amt
