import logging
from utils.db_client import DBClient

class AuthService:
    def login(self, username, password):
        try:
            db = DBClient.get_db()

            if username == "admin" and password == "admin123":
                logging.info(f"User {username} logged in successfully")
                return True
            else:
                logging.warning(f"Failed login attempt for user: {username}")
                return False
        except Exception as e:
            logging.error(f"DB Error during login: {e}")
            raise Exception("Database connection failed. Please ensure MongoDB is running.")
