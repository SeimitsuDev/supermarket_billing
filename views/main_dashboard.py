from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QGridLayout, QLabel, QFrame, QPushButton, QGraphicsDropShadowEffect, QStackedWidget)
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt
from utils.constants import WINDOW_WIDTH, WINDOW_HEIGHT
from services.inventory_service import InventoryService

class DashboardCard(QFrame):
    def __init__(self, title, value):
        super().__init__()
        self.setObjectName("DashboardCard")
        self.setMinimumHeight(150)
        
        # Apply formal soft shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 15))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        lbl_title = QLabel(title)
        lbl_title.setObjectName("CardTitle")
        lbl_title.setAlignment(Qt.AlignCenter)
        
        lbl_value = QLabel(str(value))
        lbl_value.setObjectName("CardValue")
        lbl_value.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_value)
        self.setLayout(layout)

class MainDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.login = None
        self.overview_page = None
        self.sales_page = None
        self.inventory_page = None
        self.about = None
        self.product_page = None
        self.pos_page = None
        self.content_stack = None
        self.btn_theme = None
        self.setWindowTitle("Supermarket Billing - Dashboard")
        self.resize(1100, 750)
        self.inventory_service = InventoryService()
        self.is_dark_mode = True
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # --- Sidebar Navigation (Dark Slate) ---
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(240)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(15, 30, 15, 30)
        sidebar_layout.setSpacing(10)
        
        brand_lbl = QLabel("SUPERMARKET\nBILLING")
        brand_lbl.setAlignment(Qt.AlignCenter)
        brand_lbl.setStyleSheet("font-size: 18px; font-weight: 800; color: #ffffff; margin-bottom: 30px; letter-spacing: 1px;")
        sidebar_layout.addWidget(brand_lbl)
        
        # Nav Buttons
        nav_buttons = [
            ("Dashboard Overview", self.show_overview),
            ("New Bill (POS)", self.open_pos_billing),
            ("Products", self.open_product_mgmt),
            ("Inventory", self.open_inventory),
            ("Sales History", self.open_sales_history),
            ("About", self.open_about),
        ]
        
        for text, handler in nav_buttons:
            btn = QPushButton(text)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #94a3b8;
                    text-align: left;
                    padding-left: 15px;
                    border: none;
                    font-size: 15px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    color: #ffffff;
                    background-color: #334155;
                    border-radius: 6px;
                }
            """)
            btn.setMinimumHeight(45)
            btn.clicked.connect(handler)
            sidebar_layout.addWidget(btn)
            
        sidebar_layout.addStretch()
        
        self.btn_theme = QPushButton("Light Mode")
        self.btn_theme.setStyleSheet("""
            QPushButton { background-color: transparent; border: 1px solid #475569; color: #cbd5e1; border-radius: 6px; font-weight: 600; }
            QPushButton:hover { background-color: #334155; color: white; }
        """)
        self.btn_theme.setMinimumHeight(45)
        self.btn_theme.clicked.connect(self.toggle_theme)
        sidebar_layout.addWidget(self.btn_theme)
        
        btn_logout = QPushButton("Logout")
        btn_logout.setStyleSheet("""
            QPushButton { background-color: transparent; border: 1px solid #dc2626; color: #ef4444; border-radius: 6px; font-weight: 600; }
            QPushButton:hover { background-color: #dc2626; color: white; }
        """)
        btn_logout.setMinimumHeight(45)
        btn_logout.clicked.connect(self.logout)
        sidebar_layout.addWidget(btn_logout)
        
        # --- Main Content Area (Light Gray) ---
        self.content_stack = QStackedWidget()
        
        # Page 0: Overview
        self.overview_page = QWidget()
        self.setup_overview_page()
        self.content_stack.addWidget(self.overview_page)
        
        # Page 1: POS
        from views.pos_billing_view import POSBillingView
        self.pos_page = POSBillingView()
        self.content_stack.addWidget(self.pos_page)
        
        # Page 2: Products
        from views.product_view import ProductView
        self.product_page = ProductView()
        self.content_stack.addWidget(self.product_page)
        
        # Page 3: Inventory
        from views.inventory_view import InventoryView
        self.inventory_page = InventoryView()
        self.content_stack.addWidget(self.inventory_page)
        
        # Page 4: Sales
        from views.sales_history_view import SalesHistoryView
        self.sales_page = SalesHistoryView()
        self.content_stack.addWidget(self.sales_page)
        
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.content_stack)
        
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def setup_overview_page(self):
        layout = QVBoxLayout(self.overview_page)
        layout.setContentsMargins(40, 40, 40, 40)
        
        title = QLabel("Dashboard Overview")
        title.setObjectName("TitleLabel")
        layout.addWidget(title)
        
        grid_layout = QGridLayout()
        grid_layout.setSpacing(25)
        
        stats = self.inventory_service.get_dashboard_stats()
        
        if stats:
            c1_val = str(stats.get("total_products", 0))
            c2_val = str(stats.get("today_bills", 0))
            c3_val = f"₹ {stats.get('todays_sales', 0):,.2f}"
            c4_val = str(stats.get("low_stock_items", 0))
            c5_val = str(stats.get("total_categories", 0))
            c6_val = str(stats.get("total_customers", 0))
        else:
            c1_val = c2_val = c3_val = c4_val = c5_val = c6_val = "Error"
            
        card1 = DashboardCard("Total Products", c1_val)
        card2 = DashboardCard("Today's Bills", c2_val)
        card3 = DashboardCard("Today's Sales", c3_val)
        card4 = DashboardCard("Low Stock Items", c4_val)
        card5 = DashboardCard("Total Categories", c5_val)
        card6 = DashboardCard("Total Customers", c6_val)
        
        grid_layout.addWidget(card1, 0, 0)
        grid_layout.addWidget(card2, 0, 1)
        grid_layout.addWidget(card3, 0, 2)
        grid_layout.addWidget(card4, 1, 0)
        grid_layout.addWidget(card5, 1, 1)
        grid_layout.addWidget(card6, 1, 2)
        
        layout.addLayout(grid_layout)
        layout.addStretch()

    def show_overview(self):
        self.content_stack.setCurrentIndex(0)

    def open_pos_billing(self):
        self.content_stack.setCurrentIndex(1)

    def open_product_mgmt(self):
        self.content_stack.setCurrentIndex(2)

    def open_inventory(self):
        self.content_stack.setCurrentIndex(3)

    def open_sales_history(self):
        self.content_stack.setCurrentIndex(4)

    def open_about(self):
        from views.about_dialog import AboutDialog
        self.about = AboutDialog()
        self.about.exec()

    def logout(self):
        from views.login_view import LoginView
        self.login = LoginView()
        self.login.show()
        self.close()

    def toggle_theme(self):
        import os
        from PySide6.QtWidgets import QApplication
        
        app = QApplication.instance()
        self.is_dark_mode = not self.is_dark_mode
        
        if self.is_dark_mode:
            self.btn_theme.setText("Light Mode")
            theme_file = 'style_dark.qss'
        else:
            self.btn_theme.setText("Dark Mode")
            theme_file = 'style_light.qss'
            
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        qss_path = os.path.join(str(base_dir), 'assets', 'styles', theme_file)
        
        if os.path.exists(qss_path):
            with open(qss_path, 'r') as f:
                app.setStyleSheet(f.read())
