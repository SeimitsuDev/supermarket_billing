import logging
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QCheckBox, QGraphicsDropShadowEffect, QFrame)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor
from services.auth_service import AuthService

class LoginView(QWidget):
    def __init__(self):
        super().__init__()
        self.dashboard = None
        self.btn_exit = None
        self.btn_clear = None
        self.btn_login = None
        self.chk_show_pass = None
        self.txt_password = None
        self.txt_username = None
        self.lbl_status = None
        self.setObjectName("LoginWidget")
        self.setWindowTitle("Supermarket Billing - Login")
        self.setFixedSize(450, 500)
        self.auth_service = AuthService()
        self.init_ui()


    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        
        # Create a central frame for the form to apply shadow
        form_frame = QFrame()
        form_frame.setObjectName("FormFrame")
        
        # Apply Formal Drop Shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 10)
        form_frame.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(form_frame)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(15)

        # Typography Logo
        title_lbl = QLabel("🛒 SCAN & GO")
        title_lbl.setAlignment(Qt.AlignCenter)
        title_lbl.setStyleSheet("font-size: 28px; font-weight: 900; margin-bottom: 0px; padding: 0px;")
        
        subtitle_lbl = QLabel("SUPERMARKET BILLING")
        subtitle_lbl.setAlignment(Qt.AlignCenter)
        subtitle_lbl.setStyleSheet("font-size: 12px; font-weight: bold; margin-bottom: 20px; letter-spacing: 2px;")
        
        layout.addWidget(title_lbl)
        layout.addWidget(subtitle_lbl)

        # Status Label (Success/Error)
        self.lbl_status = QLabel("")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        self.lbl_status.hide()
        layout.addWidget(self.lbl_status)

        # Username
        self.txt_username = QLineEdit()
        self.txt_username.setPlaceholderText("Username (admin)")
        self.txt_username.setMinimumHeight(45)
        layout.addWidget(self.txt_username)

        # Password
        self.txt_password = QLineEdit()
        self.txt_password.setPlaceholderText("Password (admin123)")
        self.txt_password.setEchoMode(QLineEdit.Password)
        self.txt_password.setMinimumHeight(45)
        layout.addWidget(self.txt_password)

        # Show password
        self.chk_show_pass = QCheckBox("Show Password")
        self.chk_show_pass.stateChanged.connect(self.toggle_password)
        layout.addWidget(self.chk_show_pass)

        # Buttons
        self.btn_login = QPushButton("Login")
        self.btn_login.setMinimumHeight(45)
        
        btn_layout = QHBoxLayout()
        self.btn_clear = QPushButton("Clear")
        self.btn_clear.setObjectName("OutlineButton")
        self.btn_clear.setMinimumHeight(40)
        
        self.btn_exit = QPushButton("Exit")
        self.btn_exit.setObjectName("OutlineButton")
        self.btn_exit.setMinimumHeight(40)
        
        btn_layout.addWidget(self.btn_clear)
        btn_layout.addWidget(self.btn_exit)

        self.btn_login.clicked.connect(self.handle_login)
        self.btn_clear.clicked.connect(self.handle_clear)
        self.btn_exit.clicked.connect(self.close)

        layout.addWidget(self.btn_login)
        layout.addLayout(btn_layout)

        main_layout.addWidget(form_frame)
        self.setLayout(main_layout)

        logging.info("The Login View has been initialized")

    def toggle_password(self):
        if self.chk_show_pass.isChecked():
            self.txt_password.setEchoMode(QLineEdit.Normal)
        else:
            self.txt_password.setEchoMode(QLineEdit.Password)

    def show_message(self, msg, is_error=False):
        self.lbl_status.setText(msg)
        if is_error:
            self.lbl_status.setObjectName("ErrorLabel")
        else:
            self.lbl_status.setObjectName("SuccessLabel")
        self.lbl_status.setStyleSheet(self.lbl_status.styleSheet()) 
        self.lbl_status.show()

    def handle_login(self):
        username = self.txt_username.text().strip()
        password = self.txt_password.text().strip()
        
        if not username or not password:
            self.show_message("Please enter username and password.", is_error=True)
            return

        self.btn_login.setEnabled(False)
        self.btn_login.setText("Logging in...")

        try:
            if self.auth_service.login(username, password):
                self.show_message("Login successful! Redirecting...", is_error=False)
                QTimer.singleShot(1000, self.open_dashboard)
            else:
                self.show_message("Invalid username or password.", is_error=True)
                self.btn_login.setEnabled(True)
                self.btn_login.setText("Login")

        except Exception as e:
            logging.error(e)
            self.show_message(str(e), is_error=True)
            self.btn_login.setEnabled(True)
            self.btn_login.setText("Login")

    # Used to stop showing login page and display dashboard
    def handle_clear(self):
        self.txt_username.clear()
        self.txt_password.clear()
        self.lbl_status.hide()

    def open_dashboard(self):
        from views.main_dashboard import MainDashboard
        self.dashboard = MainDashboard()
        self.dashboard.show()
        self.close()
