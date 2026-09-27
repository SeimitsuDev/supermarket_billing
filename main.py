import sys
import os
import logging
from PySide6.QtWidgets import QApplication
from views.login_view import LoginView
from utils.db_client import DBClient

def setup_logging():
    logging.basicConfig(filename='app_debug.log', level=logging.INFO, 
                        format='%(asctime)s - %(levelname)s - %(message)s')

def load_stylesheet(app):
    qss_path = os.path.join(str(os.path.dirname(__file__)), 'assets', 'styles', 'style_dark.qss')
    if os.path.exists(qss_path):
        with open(qss_path, 'r') as f:
            app.setStyleSheet(f.read())
    else:
        logging.warning("Stylesheet not found at " + qss_path)

def main():
    setup_logging()
    logging.info("Application started")
    
    app = QApplication(sys.argv)
    load_stylesheet(app)
    
    # The actual failure will be caught on login button click so the user sees a visual error.
    try:
        DBClient.get_db()
    except Exception as e:
        logging.error(f"Failed initial DB connection: {e}")
    
    login_window = LoginView()
    login_window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
