import tornado.web
import tornado.ioloop
from tornado.web import HTTPError
from Handlers.uploadHandler import UploadHandler
from Handlers.downloadHandler import DownloadHandler
from Handlers.htmlHandler import HTMLHandler
from Handlers.socketHanlder import ProgressWebSocket
from Handlers.dataHandler import GetDataHandler, DataHandler
import signal

server = None
progress_ws = None

def make_app():
    return tornado.web.Application([
        (r"/", HTMLHandler),
        (r"/upload", UploadHandler),
        (r"/download/(.*)", DownloadHandler),
        (r"/websocket", ProgressWebSocket),
        (r"/get_data/(.*)", GetDataHandler),
        (r"/data/(.*)", DataHandler)
    ],
    debug=True,
    autoreload=True
    )
def start_server(port=8888):
    if port != 8888:
        raise HTTPError(400, "Server can only run on port 8888")
    
    global server
    app = make_app()

    server = tornado.httpserver.HTTPServer(app, max_buffer_size=10485760000, max_body_size=10485760000)
    server.listen(port)
    print(f'Server is listening on localhost on port {port}')

    # Tangani KeyboardInterrupt
    def signal_handler(signum, frame):
        print("Received KeyboardInterrupt. Stopping server...")
        stop_server()
    
    # Mengaitkan penanganan KeyboardInterrupt dengan fungsi signal_handler
    signal.signal(signal.SIGINT, signal_handler)

    tornado.ioloop.IOLoop.current().start()

def stop_server():
    global server
    if server is not None:
        server.stop()  # Hentikan server jika ada yang berjalan
    tornado.ioloop.IOLoop.current().stop()


if __name__ == '__main__':
    start_server()