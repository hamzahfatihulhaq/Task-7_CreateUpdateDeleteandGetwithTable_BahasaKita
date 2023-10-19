import os
import tornado.web
import uuid
from AES_utils import decrypt_data
from Handlers.socketHanlder import ProgressWebSocket
from datetime import datetime
from config.db import db
import pandas as pd

class UploadHandler(tornado.web.RequestHandler):
    async def post(self):
        try:
            uploaded_file = self.request.files['file'][0]
            file_content = uploaded_file['body']

            if not uploaded_file['filename'].endswith('.csv'):
                raise tornado.web.HTTPError(400,reason="File must be in .csv format")

            # Membuat ID unik
            unique_id = self.create_unique_id()
            verify_collection = db.db["DataVerify"]

            time = datetime.now()
            times = [f"{time.year}:{time.month}:{time.day}", f"{time.hour}:{time.minute}:{time.second}"]
            
            json_data = {
                    "_id" : unique_id,
                    "date" :  times[0],
                    "time" : times[1]
                }
            verify_collection.insert_one(json_data)
            
            # Inisialisasi progres WebSocket
            def progress_callback(progress):
                for instance in ProgressWebSocket.instances:
                    instance.send_progress(progress)

            # decrypted_data = await decrypt_data(file_content, progress_callback)
            status = await decrypt_data(file_content, times, progress_callback)
            
            if status is False:
                raise tornado.web.HTTPError(500,reason="Key incorrect or message corrupted")

            for instance in ProgressWebSocket.instances:
                instance.send_complete()
            # Simpan file terenkripsi

            # self.write({"message": "Proses selesai"})

            tables = self.create_tabel(json_data)
            # print(tables)
            self.write(tables)
        
        except tornado.web.HTTPError as e:
            self.set_status(e.status_code)
            self.write({"error": str(e.reason)})

    def create_tabel(self, json_data):
        page= int(self.get_argument("page",1))
        items_per_page = int(self.get_argument("items_per_page", 10))

        data_collection = db.db["DataSample"]
        query = {
            "date" :  json_data['date'],
            "time" : json_data['time']
        }
        skip = (page - 1) * items_per_page  # Hitung berapa data yang akan dilewati
        valid_data = data_collection.find(query).skip(skip).limit(items_per_page)

        df = pd.DataFrame(list(valid_data))
        data_json = df.to_json(orient="records")

        return {"records": data_json}


    def create_unique_id(self):
        # Kode untuk membuat ID unik di sini, misalnya dengan modul uuid
        unique_id = str(uuid.uuid4())  # Membuat UUID versi 4 (random)
        return unique_id
    