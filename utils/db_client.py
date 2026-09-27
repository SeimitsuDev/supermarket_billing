from pymongo import MongoClient
import logging
from dotenv import load_dotenv
import os

load_dotenv()

class DBClient:
    _instance = None

    @classmethod
    def get_db(cls):
        # Logic: I am using and system_config collection having only one document to find that is the database initialised for
        if cls._instance is None:
            try:
                # connect and ping
                client = MongoClient(os.getenv("MONGODB_URI"), serverSelectionTimeoutMS=2000)

                # for trial that database is working adminCommand in mongoose
                client.admin.command('ping')
                # Client has all list of database only taking desired
                database_name : str = str(os.getenv("DB_NAME"))
                cls._instance = client[database_name]

                # As per our logic we are using system_config collections first document to find is it initialised or not to fill it with dummy data
                if "system_config" not in cls._instance.list_collection_names():
                    print(cls._instance.list_collection_names())

                    collection_name = "system_config"
                    collection = cls._instance.get_collection(collection_name)

                    collection.insert_one({"status": "initialised"})
                    print("test data loaded")
                logging.info("Connected to MongoDB successfully.")
            except Exception as e:
                logging.error(f"Error in db: {e}")
                raise e
        return cls._instance



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        filename="test_utils.log",
                        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",)
    DBClient.get_db()