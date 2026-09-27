from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QFormLayout, QComboBox, QMessageBox, QDoubleSpinBox, QSpinBox)
from services.inventory_service import InventoryService

class ProductView(QWidget):
    def __init__(self):
        super().__init__()
        self.table = None
        self.cmb_category = None
        self.spn_price = None
        self.txt_name = None
        self.spn_qty = None
        self.txt_barcode = None
        self.inventory_service = InventoryService()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        title = QLabel("Product Management")
        title.setObjectName("TitleLabel")
        layout.addWidget(title)

        # Top form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        self.txt_barcode = QLineEdit()
        self.txt_barcode.setMinimumHeight(45)
        self.txt_name = QLineEdit()
        self.txt_name.setMinimumHeight(45)
        
        self.cmb_category = QComboBox()
        self.cmb_category.addItems(["Bakery", "Dairy", "Pantry", "Beverages", "Snacks", "Personal Care", "Home Care"])
        self.cmb_category.setMinimumHeight(45)
        
        self.spn_price = QDoubleSpinBox()
        self.spn_price.setMaximum(99999)
        self.spn_price.setMinimumHeight(45)
        
        self.spn_qty = QSpinBox()
        self.spn_qty.setMaximum(9999)
        self.spn_qty.setMinimumHeight(45)
        
        form_layout.addRow("Barcode / ID:", self.txt_barcode)
        form_layout.addRow("Product Name:", self.txt_name)
        form_layout.addRow("Category:", self.cmb_category)
        form_layout.addRow("Selling Price (₹):", self.spn_price)
        form_layout.addRow("Quantity:", self.spn_qty)
        
        layout.addLayout(form_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_add = QPushButton("Add Product")
        btn_update = QPushButton("Update Product")
        btn_delete = QPushButton("Delete Product")
        btn_clear = QPushButton("Clear Form")
        
        btn_delete.setObjectName("DangerButton")
        btn_clear.setObjectName("OutlineButton")
        
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_update)
        btn_layout.addWidget(btn_delete)
        btn_layout.addWidget(btn_clear)
        layout.addLayout(btn_layout)
        
        # Connect signals
        btn_add.clicked.connect(self.add_product)
        btn_update.clicked.connect(self.update_product)
        btn_delete.clicked.connect(self.delete_product)
        btn_clear.clicked.connect(self.clear_form)

        # Table
        layout.addSpacing(10)
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Barcode", "Name", "Category", "Price", "Stock"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        
        from PySide6.QtWidgets import QAbstractItemView
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        self.table.itemClicked.connect(self.populate_form)
        layout.addWidget(self.table)
        
    def showEvent(self, event):
        super().showEvent(event)
        self.load_products()

    def clear_form(self):
        self.txt_barcode.clear()
        self.txt_name.clear()
        self.spn_price.setValue(0)
        self.spn_qty.setValue(0)
        
    def populate_form(self, item):
        row = item.row()
        self.txt_barcode.setText(self.table.item(row, 0).text())
        self.txt_name.setText(self.table.item(row, 1).text())
        self.cmb_category.setCurrentText(self.table.item(row, 2).text())
        self.spn_price.setValue(float(self.table.item(row, 3).text().replace('₹ ', '')))
        self.spn_qty.setValue(int(self.table.item(row, 4).text()))

    def load_products(self):
        products = list(self.inventory_service.products_coll.find({}))
        self.table.setRowCount(len(products))
        for i, p in enumerate(products):
            self.table.setItem(i, 0, QTableWidgetItem(p.get("barcode", "")))
            self.table.setItem(i, 1, QTableWidgetItem(p.get("product_name", "")))
            self.table.setItem(i, 2, QTableWidgetItem(p.get("category", "")))
            self.table.setItem(i, 3, QTableWidgetItem(f"₹ {p.get('selling_price', 0)}"))
            self.table.setItem(i, 4, QTableWidgetItem(str(p.get("qty", 0))))

    def add_product(self):
        barcode = self.txt_barcode.text().strip()
        if not barcode or not self.txt_name.text().strip():
            QMessageBox.warning(self, "Error", "Barcode and Name are required")
            return
            
        if self.inventory_service.products_coll.find_one({"barcode": barcode}):
            QMessageBox.warning(self, "Error", "Product with this barcode already exists")
            return
            
        doc = {
            "barcode": barcode,
            "product_name": self.txt_name.text().strip(),
            "category": self.cmb_category.currentText(),
            "selling_price": self.spn_price.value(),
            "qty": self.spn_qty.value(),
            "reorder_level": 10,
            "purchase_price": self.spn_price.value() * 0.8
        }
        self.inventory_service.products_coll.insert_one(doc)
        self.load_products()
        self.clear_form()
        QMessageBox.information(self, "Success", "Product added.")

    def update_product(self):
        barcode = self.txt_barcode.text().strip()
        if not barcode: return
        self.inventory_service.products_coll.update_one(
            {"barcode": barcode},
            {"$set": {
                "product_name": self.txt_name.text().strip(),
                "category": self.cmb_category.currentText(),
                "selling_price": self.spn_price.value(),
                "qty": self.spn_qty.value()
            }}
        )
        self.load_products()
        self.clear_form()
        QMessageBox.information(self, "Success", "Product updated.")
        
    def delete_product(self):
        barcode = self.txt_barcode.text().strip()
        if not barcode: return
        self.inventory_service.products_coll.delete_one({"barcode": barcode})
        self.load_products()
        self.clear_form()
        QMessageBox.information(self, "Success", "Product deleted.")
