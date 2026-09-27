from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView)
from PySide6.QtGui import QColor
from services.inventory_service import InventoryService

class InventoryView(QWidget):
    def __init__(self):
        super().__init__()
        self.table = None
        self.inventory_service = InventoryService()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        title = QLabel("Inventory Status")
        title.setObjectName("TitleLabel")
        layout.addWidget(title)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Barcode", "Product", "Stock", "Reorder Level", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        
        from PySide6.QtWidgets import QAbstractItemView
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        layout.addWidget(self.table)
        
    def showEvent(self, event):
        super().showEvent(event)
        self.load_inventory()

    def load_inventory(self):
        products = list(self.inventory_service.products_coll.find({}))
        self.table.setRowCount(len(products))
        for i, p in enumerate(products):
            qty = p.get("qty", 0)
            reorder = p.get("reorder_level", 10)
            
            self.table.setItem(i, 0, QTableWidgetItem(p.get("barcode", "")))
            self.table.setItem(i, 1, QTableWidgetItem(p.get("product_name", "")))
            self.table.setItem(i, 2, QTableWidgetItem(str(qty)))
            self.table.setItem(i, 3, QTableWidgetItem(str(reorder)))
            
            status_item = QTableWidgetItem()
            if qty <= 0:
                status_item.setText("Out of Stock")
                status_item.setForeground(QColor("#dc2626"))
            elif qty <= reorder:
                status_item.setText("Low Stock")
                status_item.setForeground(QColor("#ca8a04"))
            else:
                status_item.setText("In Stock")
                status_item.setForeground(QColor("#16a34a"))
                
            self.table.setItem(i, 4, status_item)
