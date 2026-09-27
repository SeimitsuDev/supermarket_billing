from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QLineEdit, QPushButton, QTableWidget, 
                               QTableWidgetItem, QHeaderView, QComboBox, QCheckBox, QCompleter, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt, QStringListModel
from PySide6.QtGui import QColor
from services.billing_service import BillingService
from services.inventory_service import InventoryService
from PySide6.QtWidgets import QMessageBox

class POSBillingView(QWidget):
    def __init__(self):
        super().__init__()
        self.lbl_gst = None
        self.cmb_payment = None
        self.chk_gst = None
        self.completer = None
        self.lbl_grand_total = None
        self.lbl_subtotal = None
        self.btn_checkout = None
        self.cart_table = None
        self.lbl_discount = None
        self.txt_barcode = None
        self.inventory_service = InventoryService()
        self.billing_service = BillingService(self.inventory_service)
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # --- Left Side: Search & Cart ---
        left_layout = QVBoxLayout()
        
        title_lbl = QLabel("Point of Sale (POS)")
        title_lbl.setStyleSheet("font-size: 24px; font-weight: 700; margin-bottom: 10px;")
        left_layout.addWidget(title_lbl)

        # Search Bar
        search_layout = QHBoxLayout()
        self.txt_barcode = QLineEdit()
        self.txt_barcode.setPlaceholderText("Search by Name or Barcode...")
        self.txt_barcode.setMinimumHeight(45)
        self.txt_barcode.returnPressed.connect(self.add_item_to_cart)
        
        # Setup Completer for Dropdown Suggestions
        self.completer = QCompleter()
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchContains)
        
        popup = self.completer.popup()
        popup.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        
        # Rely on global QSS for popup styling (QListView)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 25))
        shadow.setOffset(0, 5)
        popup.setGraphicsEffect(shadow)
        
        self.txt_barcode.setCompleter(self.completer)
        
        btn_add = QPushButton("Add Item")
        btn_add.setMinimumHeight(45)
        btn_add.setFixedWidth(100)
        btn_add.clicked.connect(self.add_item_to_cart)
        
        search_layout.addWidget(self.txt_barcode)
        search_layout.addWidget(btn_add)
        left_layout.addLayout(search_layout)

        # Cart Table (Styling handled by global QSS)
        self.cart_table = QTableWidget(0, 5)
        self.cart_table.setHorizontalHeaderLabels(["S.No", "Product", "Qty", "Price", "Amount"])
        self.cart_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.cart_table.verticalHeader().setVisible(False)
        
        from PySide6.QtWidgets import QAbstractItemView
        self.cart_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        left_layout.addWidget(self.cart_table)
        
        # Cart Actions
        cart_actions_layout = QHBoxLayout()
        btn_clear_cart = QPushButton("Clear Cart")
        btn_clear_cart.setObjectName("OutlineButton")
        btn_clear_cart.clicked.connect(self.clear_cart)
        cart_actions_layout.addWidget(btn_clear_cart)
        cart_actions_layout.addStretch()
        left_layout.addLayout(cart_actions_layout)

        # --- Right Side: Billing Summary ---
        right_panel = QWidget()
        right_panel.setObjectName("RightPanel")
        right_panel.setFixedWidth(320)
        
        # Apply formal shadow to the right panel
        panel_shadow = QGraphicsDropShadowEffect()
        panel_shadow.setBlurRadius(15)
        panel_shadow.setColor(QColor(0, 0, 0, 15))
        panel_shadow.setOffset(0, 4)
        right_panel.setGraphicsEffect(panel_shadow)
        
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(25, 25, 25, 25)
        
        summary_title = QLabel("Bill Summary")
        summary_title.setStyleSheet("font-size: 18px; font-weight: 700; margin-bottom: 15px;")
        right_layout.addWidget(summary_title)
        
        # Totals
        self.lbl_subtotal = QLabel("Subtotal: ₹ 0.00")
        self.lbl_discount = QLabel("Discount: ₹ 0.00")
        self.lbl_gst = QLabel("GST (5%): ₹ 0.00")
        self.lbl_grand_total = QLabel("Total: ₹ 0.00")
        self.lbl_grand_total.setStyleSheet("font-size: 24px; font-weight: 800; color: #16a34a; margin-top: 15px;")
        
        for lbl in [self.lbl_subtotal, self.lbl_discount, self.lbl_gst]:
            lbl.setStyleSheet("font-size: 14px; margin-bottom: 5px;")
            right_layout.addWidget(lbl)
            
        right_layout.addWidget(self.lbl_grand_total)
        
        # GST Toggle and Payment Mode
        right_layout.addSpacing(20)
        
        self.chk_gst = QCheckBox("Apply GST (5%)")
        self.chk_gst.setChecked(True)
        self.chk_gst.stateChanged.connect(self.toggle_gst)
        right_layout.addWidget(self.chk_gst)
        
        right_layout.addSpacing(10)
        right_layout.addWidget(QLabel("Payment Mode:"))
        self.cmb_payment = QComboBox()
        self.cmb_payment.addItems(["Cash", "UPI", "Card"])
        self.cmb_payment.setMinimumHeight(40)
        right_layout.addWidget(self.cmb_payment)
        
        right_layout.addStretch()
        
        # Checkout Button
        self.btn_checkout = QPushButton("Complete Bill")
        self.btn_checkout.setObjectName("SuccessButton")
        self.btn_checkout.setMinimumHeight(50)
        self.btn_checkout.clicked.connect(self.checkout)
        right_layout.addWidget(self.btn_checkout)
        
        main_layout.addLayout(left_layout)
        main_layout.addWidget(right_panel)

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_completer_data()

    def refresh_completer_data(self):
        products = list(self.inventory_service.products_coll.find({}, {"barcode": 1, "product_name": 1}))
        suggestion_list = []
        for p in products:
            suggestion_list.append(f"{p.get('barcode', '')} - {p.get('product_name', '')}")
        model = QStringListModel(suggestion_list)
        self.completer.setModel(model)

    def toggle_gst(self):
        self.billing_service.apply_gst = self.chk_gst.isChecked()
        self.refresh_cart_ui()

    def add_item_to_cart(self):
        text = self.txt_barcode.text().strip()
        if not text:
            return
        barcode = text.split(" - ")[0].strip()
        success = self.billing_service.add_to_cart(barcode, 1)
        if success:
            self.refresh_cart_ui()
            self.txt_barcode.clear()
        else:
            QMessageBox.warning(self, "Not Found", "Product not found or out of stock!")

    def refresh_cart_ui(self):
        cart_items = self.billing_service.current_cart
        self.cart_table.setRowCount(len(cart_items))
        
        for i, item in enumerate(cart_items):
            self.cart_table.setItem(i, 0, QTableWidgetItem(str(i+1)))
            self.cart_table.setItem(i, 1, QTableWidgetItem(item.product.get('product_name', 'Unknown')))
            self.cart_table.setItem(i, 2, QTableWidgetItem(str(item.qty)))
            self.cart_table.setItem(i, 3, QTableWidgetItem(f"₹ {item.product.get('selling_price', 0)}"))
            self.cart_table.setItem(i, 4, QTableWidgetItem(f"₹ {item.total_amt}"))
            
        totals = self.billing_service.calculate_totals()
        self.lbl_subtotal.setText(f"Subtotal: ₹ {totals['subtotal']:.2f}")
        gst_text = f"GST (5%): ₹ {totals['gst']:.2f}" if self.billing_service.apply_gst else "GST (0%): ₹ 0.00"
        self.lbl_gst.setText(gst_text)
        self.lbl_grand_total.setText(f"Total: ₹ {totals['total']:.2f}")

    def clear_cart(self):
        self.billing_service.current_cart = []
        self.refresh_cart_ui()

    def checkout(self):
        if not self.billing_service.current_cart:
            QMessageBox.warning(self, "Empty Cart", "Cannot checkout an empty cart.")
            return
        pay_mode = self.cmb_payment.currentText()
        bill_no = self.billing_service.generate_bill(pay_mode)
        if bill_no:
            # Fetch the completed bill document to generate the receipt
            bill_data = self.inventory_service.db['bills'].find_one({"bill_no": bill_no})
            
            from views.bill_dialog import BillDialog
            dialog = BillDialog(bill_data, self)
            dialog.exec()
            
            self.clear_cart()
        else:
            QMessageBox.critical(self, "Error", "Failed to generate bill.")
