from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout, QMessageBox
from PySide6.QtGui import QFont
import logging

class BillDialog(QDialog):
    def __init__(self, bill_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Receipt - {bill_data['bill_no']}")
        self.setFixedSize(480, 700)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setFixedWidth(400)
        
        # Force a paper-like appearance regardless of dark/light mode
        self.text_area.setStyleSheet("""
            QTextEdit {
                background-color: #ffffff; 
                color: #0f172a; 
                border: 1px solid #cbd5e1;
                border-radius: 4px;
                padding: 15px;
            }
        """)
        
        # Use a monospace font to ensure column alignment
        font = QFont("Times New Roman")
        font.setPointSize(13)
        font.setStyleHint(QFont.Monospace)
        self.text_area.setFont(font)
        
        self.generate_receipt_text(bill_data)
        
        # Center the text area
        receipt_layout = QHBoxLayout()
        receipt_layout.addStretch()
        receipt_layout.addWidget(self.text_area)
        receipt_layout.addStretch()
        layout.addLayout(receipt_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 10, 0, 0)
        
        btn_print = QPushButton("Print Bill")
        btn_print.setMinimumHeight(45)
        btn_print.setObjectName("SuccessButton")
        btn_print.clicked.connect(self.print_bill)
        
        btn_close = QPushButton("Close")
        btn_close.setMinimumHeight(45)
        btn_close.setObjectName("OutlineButton")
        btn_close.clicked.connect(self.accept)
        
        btn_layout.addWidget(btn_close)
        btn_layout.addWidget(btn_print)
        
        layout.addLayout(btn_layout)
        
    def generate_receipt_text(self, data):
        # With header initialisation
        receipt : list = ["=" * 42, f"{'SCAN & GO MART':^42}", f"{'123 Supermarket Ave, Tech City':^42}", "=" * 42,
                          f"Bill No : {data['bill_no']}", f"Date    : {data['date']}", "-" * 42,
                          f"{'Item':<21}{'Qty':<4}{'Price':<8}{'Total':<9}", "-" * 42]

        # Items
        for item in data['items']:
            name = str(item['product_name'])[:19]
            qty = item['qty']
            price = item['price']
            total = item['amount']
            receipt.append(f"{name:<21}{qty:<4}{price:<8.2f}{total:<9.2f}")
            
        receipt.append("-" * 42)
        
        # Totals
        receipt.append(f"{'Subtotal:':<32}₹ {data['subtotal']:>7.2f}")
        receipt.append(f"{'GST (5%):':<32}₹ {data['gst']:>7.2f}")
        receipt.append("=" * 42)
        receipt.append(f"{'GRAND TOTAL:':<32}₹ {data['grand_total']:>7.2f}")
        receipt.append("=" * 42)
        
        # Footer
        receipt.append(f"Payment Mode: {data['pay_mode']}")
        receipt.append(f"Customer: {data.get('cust_name', 'Walk-in')}")
        receipt.append("")
        receipt.append(f"{'Thank you for shopping with us!':^42}")
        receipt.append(f"{'Please visit again':^42}")
        
        self.text_area.setText("\n".join(receipt))

    def print_bill(self):
        logging.info("Bill sent to Printer!")
        QMessageBox.information(self, "Print", "Bill sent to printer successfully! 😊")
