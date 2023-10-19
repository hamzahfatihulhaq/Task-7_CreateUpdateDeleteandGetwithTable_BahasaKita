import tornado.web
import uuid
from config.db import db
import pandas as pd
import json
import bson

class GetDataHandler(tornado.web.RequestHandler):
    async def get(self, data_id):
        page= int(self.get_argument("page",1))
        items_per_page = int(self.get_argument("items_per_page", 10))

        valid_id = self.check_id_validity(data_id)
        if valid_id and "Error" not in valid_id :
            data_collection = db.db["DataSample"]
            query = {
                "date" :  valid_id['date'],
                "time" : valid_id['time']
            }
            # valid_data = data_collection.find(query)
            skip = (page - 1) * items_per_page  # Hitung berapa data yang akan dilewati
            valid_data = data_collection.find(query).skip(skip).limit(items_per_page)


            # Konversi data menjadi DataFrame
            df = pd.DataFrame(list(valid_data))
            data_json = df.to_json(orient="records")
            # Kirim data JSON ke klien
            self.write({"records": data_json})
            # self.write({"records": "TEST TEST"})
        
        else:
            self.set_status(404)
            self.write({"Error": "Data not found"})


    def check_id_validity(self, data_id):
        try:
            if str(uuid.UUID(data_id)) == data_id:
                verify_collection = db.db["DataVerify"]
                verify = verify_collection.find_one({"_id": data_id})

                if verify:
                    serialized_dict = {key: value for key, value in verify.items() if key != '_id'}
                    return serialized_dict
            # else:
            return None
        except Exception as e:
            return {"Error": "Invalid audio ID format"}
        
class DataHandler(tornado.web.RequestHandler):
    async def put(self, data_id):
        valid_id = self.check_id_validity(data_id)        
        if valid_id and "Error" not in valid_id :
            data_collection = db.db["DataSample"]
            requestData = json.loads(self.request.body)

            _id = requestData["id"]
            if data_collection.find_one({"_id": _id}):
                json_data = {
                    "word" :  requestData["word"],
                    "Deskripsi" : requestData["Deskripsi"]

                }
                # data_collection.insert_one(json_data)
                data_collection.update_one({"_id": _id}, {"$set": json_data}, upsert=False)
                self.write({"messages": "Data updated"})
            else:
                self.set_status(404)
                self.write({"Error": "Data not found"})
            
        else:
            self.set_status(404)
            self.write({"Error": "Invalid ID format"})

    async def delete(self, data_id):
        valid_id = self.check_id_validity(data_id)        
        if valid_id and "Error" not in valid_id :
            data_collection = db.db["DataSample"]
            requestData = json.loads(self.request.body)

            _id = requestData["id"]
            if data_collection.find_one({"_id": _id}):
                # Menghapus data
                data_collection.delete_one({"_id": _id})
                self.write({"messages": "Data deleted"})

            else:
                self.set_status(404)
                self.write({"Error": "Data not found"})
            
        else:
            self.set_status(404)
            self.write({"Error": "Invalid ID format"})

    def check_id_validity(self, data_id):
        try:
            if str(uuid.UUID(data_id)) == data_id:
                verify_collection = db.db["DataVerify"]
                verify = verify_collection.find_one({"_id": data_id})

                if verify:
                    serialized_dict = {key: value for key, value in verify.items() if key != '_id'}
                    return serialized_dict
            # else:
            return None
        except Exception as e:
            return {"Error": "Invalid audio ID format"}