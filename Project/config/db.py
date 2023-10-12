from pymongo import MongoClient

class Database:
    def __init__(self, url):
        self.client = MongoClient(url)
        self.db = self.client["my_database"]  # Ganti nama database sesuai dengan kebutuhan

db = Database("mongodb://localhost:27017")  # Ganti URL sesuai dengan kebutuhan