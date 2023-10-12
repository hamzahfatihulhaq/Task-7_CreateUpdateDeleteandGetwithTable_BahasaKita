import os
import tornado.web
from AES_utils import encrypt_data
from Handlers.socketHanlder import ProgressWebSocket
from config.db import db
import uuid
import time
# import numpy as np

BATCH_SIZE = int(1 * 1024 * 1024)

class DownloadHandler(tornado.web.RequestHandler):
    async def get(self, filename):
        # Lakukan pengecekan id di sini, misalnya dari database atau sesuai logika aplikasi Anda
        valid_id = self.check_id_validity(filename)
        print(valid_id)
        if valid_id and "error" not in valid_id :
            # Baca file terenkripsi
            data_collection = db.db["DataSample"]
            print("berhasil")
            query = {
                "date" :  valid_id['date'],
                "time" : valid_id['time']
            }
            # Kirim data terdekripsi ke browser

            valid_data = data_collection.find(query)
            data_list = []
            header = ["UUID", "Word", "Description"]
            
            data_list.append(header)
            for data in valid_data:
                data_list.append([value for key, value in data.items() if key != 'date' and key != 'time'])
            
            data_list = [
                [f'{item};\r\n' if i == len(sublist) - 1 else f'{item};' for i, item in enumerate(sublist)]
                for sublist in data_list
            ]
            
            data_list = [item for sublist in data_list for item in sublist]

            
            # Encode setiap string dalam list ke dalam format UTF-8
            data_list = [item.encode('utf-8') for item in data_list]
            start_time = time.time()

            chunked_data =[]
            for chunk in self.chunk_data(b''.join(data_list)):
                # Proses atau kirim chunk ke tujuan Anda di sini
                chunked_data.append(chunk)
            
            print(time.time() - start_time)
            
            # Dekripsi file
            def progress_callback(progress):
                for instance in ProgressWebSocket.instances:
                    instance.send_progress(progress)

            start_time = time.time()
            encrypted_data = await encrypt_data(chunked_data, progress_callback)
            print(time.time() - start_time)

            for instance in ProgressWebSocket.instances:
                instance.send_complete()

            filename = filename+'.csv'
            # Set header agar browser mengenali kontennya sebagai file
            self.set_header('Content-Type', 'application/octet-stream')
            self.set_header('Content-Disposition', f'attachment; filename={filename}')
            
            # Kirim data terdekripsi ke browser
            self.write(encrypted_data)

        else:
            self.set_status(404)
            self.write({"error": "File not found"})

    def check_id_validity(self, filename):
        try:
            if str(uuid.UUID(filename)) == filename:
                verify_collection = db.db["DataVerify"]
                verify = verify_collection.find_one({"_id": filename})

                if verify:
                    serialized_dict = {key: value for key, value in verify.items() if key != '_id'}
                    return serialized_dict
            # else:
            return None
        except Exception as e:
            return {"error": "Invalid audio ID format"}

    def chunk_data(self, data, chunk_size=1024 * 1024):  # 1MB
        data_length = len(data)
        num_chunks = (data_length + chunk_size - 1) // chunk_size  # Hitung jumlah chunk
        print(num_chunks)
        for i in range(num_chunks):
            start = i * chunk_size
            end = min((i + 1) * chunk_size, data_length)
            chunk = data[start:end]
            yield chunk
