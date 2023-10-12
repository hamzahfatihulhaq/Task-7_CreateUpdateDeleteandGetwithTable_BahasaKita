import tornado.web

class HTMLHandler(tornado.web.RequestHandler):

    async def get(self):
        with open("Project/index.html", "r") as file:
            html_content = file.read()
            self.write(html_content)

            