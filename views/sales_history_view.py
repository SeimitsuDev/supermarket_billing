from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView)
from services.inventory_service import InventoryService

class SalesHistoryView(QWidget):
    def __init__(self):
        super().__init__()
        self.table = None
        self.inventory_service = InventoryService()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        title = QLabel("Sales History")
        title.setObjectName("TitleLabel")
        layout.addWidget(title)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Bill No", "Date", "Customer", "Pay Mode", "Grand Total"])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        
        from PySide6.QtWidgets import QAbstractItemView
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        layout.addWidget(self.table)
        
    def showEvent(self, event):
        super().showEvent(event)
        self.load_history()

    def load_history(self):
        bills = list(self.inventory_service.db['bills'].find({}).sort("_id", -1))
        self.table.setRowCount(len(bills))
        for i, b in enumerate(bills):
            self.table.setItem(i, 0, QTableWidgetItem(b.get("bill_no", "")))
            self.table.setItem(i, 1, QTableWidgetItem(b.get("date", "")))
            self.table.setItem(i, 2, QTableWidgetItem(b.get("cust_name", "")))
            self.table.setItem(i, 3, QTableWidgetItem(b.get("pay_mode", "")))
            self.table.setItem(i, 4, QTableWidgetItem(f"₹ {b.get('grand_total', 0):.2f}"))
