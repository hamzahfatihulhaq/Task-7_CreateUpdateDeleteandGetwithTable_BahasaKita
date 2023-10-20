import unittest
from tornado.testing import AsyncHTTPTestCase, gen_test
from tornado.gen import coroutine
import tornado.httputil
from tornado.httpclient import HTTPRequest
import http.client 
import tornado.websocket 
from tornado.websocket import websocket_connect
import tornado.ioloop 
import json
from unittest.mock import Mock
import pymongo

import sys
import os
# Dapatkan path lengkap dari direktori 'Handlers' dan tambahkan ke sys.path
handlers_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Project'))
sys.path.insert(0, handlers_dir)

from Project.app import make_app, start_server, stop_server
from Project.Handlers.socketHanlder import ProgressWebSocket


class TestHandler(AsyncHTTPTestCase):        
    def get_app(self):
        return make_app()
    
    def setUp(self):
        super().setUp()
        self.ws_connection = None
        self.received_message_str = None
        self.progress_message = None

    def tearDown(self):
        if self.ws_connection:
            self.ws_connection.close()
        super().tearDown()

    def test_homepage(self):
        print(
            "========================test_homepage============================="
        )
        response = self.fetch("/")
        self.assertEqual(response.code, 200)
        print(
            "====================================================================="
        )
    
    # gen_test()
    # def test_run_server(self):
    #     print(
    #         "========================test_run_server============================="
    #     )
    #     start_server(8888) 
    #     # stop_server()
    #     self.assertTrue(True)
    #     print(
    #         "====================================================================="
    #     )

    # @gen_test()
    # def test_stop_server(self):
    #     print(
    #         "========================test_stop_server============================="
    #     )
    #     try:
    #         yield start_server(port=8889) 
    #     except tornado.httpclient.HTTPError as e:
    #         self.assertEqual(e.response.code, 400)
    #     except tornado.web.HTTPError as e:
    #         self.assertEqual(e.status_code, 400)
    #     print(
    #         "====================================================================="
    #     )

    # datahandler
    @gen_test(timeout=10)
    async def test_get_dataHandler(self):
        client = pymongo.MongoClient("mongodb://localhost:27017")
        db = client["my_database"]
        collection = db["DataVerify"]

        # Simulasikan sebuah filename yang valid
        valid_filename = collection.find_one(sort=[("_id", pymongo.DESCENDING)])
        valid_filename = valid_filename["_id"]

        page =1
        item_per_page = 10
        response_future = self.http_client.fetch(
            self.get_url(f"/get_data/{valid_filename}?page={page}&items_per_page={item_per_page}"),
            method="GET"
        )
        response = await response_future

        self.assertEqual(response.code, 200)
        data = json.loads(response.body)
        self.assertIn("records", data)
    
    @gen_test
    def test_getdata_handler_id_not_found(self):
        # Menguji kasus ketika file tidak ditemukan
        print(
            "========================test_GET Data_handler_file_not_found============================="
        )
        try:
            page =1
            item_per_page = 10
            yield self.http_client.fetch(
                self.get_url(f"/get_data/5adda310-aa23-489b-9a83-4c6d98cccd06?page={page}&items_per_page={item_per_page}"),
                raise_error=True
            )
        except tornado.httpclient.HTTPError as e:
            # Periksa apakah status kode yang diharapkan adalah 400
            self.assertEqual(e.response.code, 404)

        print(
            "====================================================================="
        )
    
    @gen_test
    def test_getdata_handler_invalid_id_format(self):
        print(
            "========================test_download_handler_invalid_id_format============================="
        )
        # Menguji kasus ketika ID tidak valid
        try:
            page =1
            item_per_page = 10
            yield self.http_client.fetch(
                self.get_url(f"/get_data/1111111?page={page}&items_per_page={item_per_page}"),
                raise_error=True
            )
        except tornado.httpclient.HTTPError as e:
            # Periksa apakah status kode yang diharapkan adalah 400
            self.assertEqual(e.response.code, 404)

        print(
            "====================================================================="
        )
    
    # # update
    @gen_test(timeout=30)
    async def test_edit_dataHandler(self):
        print(
            "========================test_UPDATE_data_handler============================="
        )
        client = pymongo.MongoClient("mongodb://localhost:27017")
        db = client["my_database"]
        collection = db["DataVerify"]

        # Simulasikan sebuah filename yang valid
        valid_filename = collection.find_one(sort=[("_id", pymongo.DESCENDING)])
        valid_filename = valid_filename["_id"]

        data = {
            "id": "1b2e9140-c588-4026-ab3e-41a4bbd58a3f",
            "Deskripsi": "Updated Deskripsi",
            "word": "Updated Word"
        }
        response_future = self.http_client.fetch(
            self.get_url(f"/data/{valid_filename}"),
            method="PUT", 
            body=json.dumps(data)
        )
        response = await response_future
        
        self.assertEqual(response.code, 200)
        data = json.loads(response.body)
        self.assertIn("messages", data)
    
    @gen_test(timeout=30)
    def test_edit_dataHandler_id_not_found(self):
        print(
            "========================test_UPDATE_data_handle_id_not_foundr============================="
        )
        try:
            client = pymongo.MongoClient("mongodb://localhost:27017")
            db = client["my_database"]
            collection = db["DataVerify"]

            # Simulasikan sebuah filename yang valid
            valid_filename = collection.find_one(sort=[("_id", pymongo.DESCENDING)])
            valid_filename = valid_filename["_id"]

            data = {
                "id": "11111",
                "Deskripsi": "Updated Deskripsi",
                "word": "Updated Word"
            }
            yield self.http_client.fetch(
                self.get_url(f"/data/{valid_filename}"),
                method="PUT", 
                body=json.dumps(data),
                raise_error=True
            )
        except tornado.httpclient.HTTPError as e:
            # Periksa apakah status kode yang diharapkan adalah 400
            self.assertEqual(e.response.code, 404)

        print(
            "====================================================================="
        )
    
    @gen_test
    def test_putdata_handler_invalid_id_format(self):
        # Menguji kasus ketika file tidak ditemukan
        print(
            "========================test_UPDATE_data_handler_invalid_id_format============================="
        )
        try:
            data = {
            "id": "1b2e9140-c588-4026-ab3e-41a4bbd58a32",
            "Deskripsi": "Updated Deskripsi",
            "word": "Updated Word"
            }
            yield self.http_client.fetch(
                self.get_url(f"/data/d444458c-2d75-4360-b9a6-d5419634152d"),
                method="PUT", 
                body=json.dumps(data),
                raise_error=True
            )
        except tornado.httpclient.HTTPError as e:
            # Periksa apakah status kode yang diharapkan adalah 400
            self.assertEqual(e.response.code, 404)

        print(
            "====================================================================="
        )
        
    @gen_test
    def test_datahandler_invalid_id_format(self):
        print(
            "========================test_datahandler_invalid_id_format============================="
        )
        # Menguji kasus ketika ID tidak valid
        try:
            data = {
            "id": "1b2e9140-c588-4026-ab3e-41a4bbd58a32",
            "Deskripsi": "Updated Deskripsi",
            "word": "Updated Word"
            }
            yield self.http_client.fetch(
                self.get_url(f"/data/11111"),
                method="PUT", 
                body=json.dumps(data),
                raise_error=True
            )
        except tornado.httpclient.HTTPError as e:
            # Periksa apakah status kode yang diharapkan adalah 400
            self.assertEqual(e.response.code, 404)

        print(
            "====================================================================="
        )
    
    # #Delete
    @gen_test(timeout=10)
    async def test_delete_dataHandler(self):
        print(
            "========================test_DELETE_data_handler============================="
        )
        client = pymongo.MongoClient("mongodb://localhost:27017")
        db = client["my_database"]
        collection = db["DataVerify"]

        # Simulasikan sebuah filename yang valid
        valid_filename = collection.find_one(sort=[("_id", pymongo.DESCENDING)])
        valid_filename = valid_filename["_id"]

        data = {
            "id": "dcd38df4-26f3-40c2-945f-1c5bda5524d3"
        }
        response_future = self.http_client.fetch(
            self.get_url(f"/data/{valid_filename}?id={data['id']}"),
            method="DELETE"
        )
        response = await response_future
        
        self.assertEqual(response.code, 200)
        data = json.loads(response.body)
        self.assertIn("messages", data)
    
    @gen_test(timeout=30)
    def test_delete_dataHandler_id_not_found(self):
        print(
            "========================test_DELETE_data_handle_id_not_foundr============================="
        )
        try:
            client = pymongo.MongoClient("mongodb://localhost:27017")
            db = client["my_database"]
            collection = db["DataVerify"]

            # Simulasikan sebuah filename yang valid
            valid_filename = collection.find_one(sort=[("_id", pymongo.DESCENDING)])
            valid_filename = valid_filename["_id"]

            data = {
                "id": "11111",
            }
            yield self.http_client.fetch(
                self.get_url(f"/data/{valid_filename}?id={data['id']}"),
                method="DELETE",
                raise_error=True
            )
        except tornado.httpclient.HTTPError as e:
            # Periksa apakah status kode yang diharapkan adalah 400
            self.assertEqual(e.response.code, 404)

        print(
            "====================================================================="
        )

    @gen_test
    def test_deletedata_handler_invalid_id_format(self):
        # Menguji kasus ketika file tidak ditemukan
        print(
            "========================test_DELETE_data_handler_invalid_id_format============================="
        )
        try:
            data = {
                "id": "dcd38df4-26f3-40c2-945f-1c5bda5524d3"
            }
            yield self.http_client.fetch(
                self.get_url(f"/data/d444458c-2d75-4360-b9a6-d5419634152d?id={data['id']}"),
                method="DELETE", 
                raise_error=True
            )
        except tornado.httpclient.HTTPError as e:
            # Periksa apakah status kode yang diharapkan adalah 400
            self.assertEqual(e.response.code, 404)

        print(
            "====================================================================="
        )
       
   
    # # upload
    @gen_test(timeout=20)
    def test_upload_handler(self):
        print(
            "========================test_upload_handler============================="
        )
        # Buat file CSV sementara untuk pengujian
        temp_csv_file = "Test/Samples/3dee037f-df72-4b8a-a391-7534acf3bc3f.csv"
        
        # Baca isi file
        with open(temp_csv_file, 'rb') as csv_file:
            file_content = csv_file.read()

        response = yield self.upload_file(file_content, "3dee037f-df72-4b8a-a391-7534acf3bc3f.csv")

        # Periksa kode respons
        self.assertEqual(response.code, 200)
        print(
            "====================================================================="
        )
    
    @gen_test
    def test_upload_handler_invalid_file_format(self):
        print(
            "========================test_upload_handler_invalid_file_format============================="
        )
        # Menguji kasus ketika format file yang diunggah tidak valid
        with open("Test/Samples/4446d0a7-79be-462b-91c0-b2dcefd01951", "rb") as file:
            file_content = file.read()

        try:
            yield self.upload_file(file_content, "4446d0a7-79be-462b-91c0-b2dcefd01951")
            
        except tornado.httpclient.HTTPError as e:
            # Periksa apakah status kode yang diharapkan adalah 400
            self.assertEqual(e.response.code, 400)
        print(
            "====================================================================="
        )

    @gen_test
    def test_upload_handler_internal_error(self):
        print(
            "========================test_upload_handler_internal_error============================="
        )
        # Menguji kasus ketika terjadi kesalahan internal dalam fungsi upload
        with open("Test/Samples/a5a333e6-64fd-4de3-87e9-c2f735d18da9.csv", "rb") as file:
            file_content = file.read()

        try:
            yield self.upload_file(file_content, "a5a333e6-64fd-4de3-87e9-c2f735d18da9.csv")

        except tornado.httpclient.HTTPError as e:
            # Periksa apakah status kode yang diharapkan adalah 400
            self.assertEqual(e.response.code, 500)
        
        print(
            "====================================================================="
        )

    # # Helper function untuk mengunggah file
    @coroutine
    def upload_file(self, file_content, filename):
        boundary = "------------------------Boundary"

        headers = {
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        }

        # Konstruksi body permintaan
        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
            f'Content-Type: application/octet-stream\r\n\r\n'
        )

        # Konkatenasi body dengan file_content dalam bentuk binary
        body = body.encode('utf-8') + file_content + b'\r\n'
        body += f"--{boundary}--\r\n".encode('utf-8')

        response_future = self.http_client.fetch(
            self.get_url("/upload"),
            method="POST",
            headers=headers,
            body=body,
            raise_error=True
        )

        response = yield response_future
        return response
    
    # download
    @gen_test
    async def test_download_handler(self):
        print(
            "========================test_download_handler============================="
        )
        client = pymongo.MongoClient("mongodb://localhost:27017")
        db = client["my_database"]
        collection = db["DataVerify"]

        # Simulasikan sebuah filename yang valid
        valid_filename = collection.find_one(sort=[("_id", pymongo.DESCENDING)])
        valid_filename = valid_filename["_id"]

        # Kirim permintaan HTTP GET ke DownloadHandler
        response_future = self.http_client.fetch(
            self.get_url(f"/download/{valid_filename}"),
            method="GET"
        )

        response = await response_future

        # Periksa kode respons
        self.assertEqual(response.code, 200)
        # Pastikan tipe konten adalah 'application/octet-stream'
        self.assertEqual(response.headers.get("Content-Type"), "application/octet-stream")
        # Pastikan tipe disposition adalah 'attachment'
        self.assertEqual(response.headers.get("Content-Disposition"), f"attachment; filename={valid_filename}.csv")

        print(
            "====================================================================="
        )

    @gen_test
    def test_download_handler_file_not_found(self):
        # Menguji kasus ketika file tidak ditemukan
        print(
            "========================test_download_handler_file_not_found============================="
        )
        try:
            yield self.http_client.fetch(
                self.get_url("/download/5adda310-aa23-489b-9a83-4c6d98cccd06"),
                raise_error=True
            )
        except tornado.httpclient.HTTPError as e:
            # Periksa apakah status kode yang diharapkan adalah 400
            self.assertEqual(e.response.code, 404)

        print(
            "====================================================================="
        )


    @gen_test
    def test_download_handler_invalid_id_format(self):
        print(
            "========================test_download_handler_invalid_id_format============================="
        )
        # Menguji kasus ketika ID tidak valid
        try:
            yield self.http_client.fetch(
                self.get_url("/download/1111111"),
                raise_error=True
            )
        except tornado.httpclient.HTTPError as e:
            # Periksa apakah status kode yang diharapkan adalah 400
            self.assertEqual(e.response.code, 404)

        print(
            "====================================================================="
        )
    

    @gen_test
    def test_open_websocket(self):
        print(
            "========================test_open_websocket============================="
        )
        ws_url = f"ws://localhost:{self.get_http_port()}/websocket"  # Dapatkan URL WebSocket

        # Buat WebSocket connection menggunakan AsyncHTTPClient
        self.ws_connection = yield tornado.websocket.websocket_connect(
            ws_url)

        # Simulasikan data progres yang dikirim dari server
        server_progres_data = {'message': 'WebSocket connection established'}
        server_progres_data_str = json.dumps(server_progres_data)

        # Kirim data progres dari server ke WebSocket
        self.ws_connection.write_message(server_progres_data_str)

        # Tunggu hingga pesan selesai diterima dari WebSocket
        self.received_message_str = yield self.ws_connection.read_message()
        # Sekarang, Anda dapat menguraikannya sebagai JSON
        self.received_message = json.loads(self.received_message_str)
        print(self.received_message)

        # Periksa apakah pesan yang diterima adalah pesan progres yang dikirimkan oleh server
        self.assertEqual(self.received_message, server_progres_data)

        print(
            "====================================================================="
        )
        
    # @gen_test
    # def test_send_progress(self):
    #     ws_url = f"ws://localhost:{self.get_http_port()}/websocket"
    #     ws_connection = yield websocket_connect(ws_url)
        
    #     # Tunggu hingga koneksi WebSocket terbuka
    #     response = yield ws_connection.read_message()
    #     self.assertEqual(response, json.dumps({"message": "WebSocket connection established"}))

    #     # Kirim pesan progres ke WebSocket
    #     progress_message = {"progress": "50.00%", "message": "Proses Loading"}
    #     ws_connection.write_message(json.dumps(progress_message))

    #     # Tunggu hingga pesan progres diterima
    #     response = yield ws_connection.read_message()
    #     self.assertEqual(response, json.dumps(progress_message))

    #     ws_connection.close()

    # @gen_test
    # def test_send_complete(self):
    #     ws_url = f"ws://localhost:{self.get_http_port()}/websocket"
    #     ws_connection = yield websocket_connect(ws_url)
        
    #     # Tunggu hingga koneksi WebSocket terbuka
    #     response = yield ws_connection.read_message()
    #     self.assertEqual(response, json.dumps({"message": "WebSocket connection established"}))

    #     # Kirim pesan "Proses selesai" ke WebSocket
    #     complete_message = {"message": "Proses selesai"}
    #     ws_connection.write_message(json.dumps(complete_message))

    #     # Tunggu hingga pesan "Proses selesai" diterima
    #     response = yield ws_connection.read_message()
    #     self.assertEqual(response, json.dumps(complete_message))

    #     ws_connection.close()
        
if __name__ == "__main__":
    tornado.testing.main()