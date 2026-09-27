from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class AboutDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        self.resize(300, 150)
        layout = QVBoxLayout()
        lbl = QLabel("Supermarket Billing System\n\nPersonal Project\nDeveloped using PySide6 and MongoDB.")
        lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl)
        self.setLayout(layout)
