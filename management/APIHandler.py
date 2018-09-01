import json
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer


# This class will handles any incoming request from
# the browser
class APIHandler(BaseHTTPRequestHandler):
    # Handler for the GET requests
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        # Send the html message
        self.wfile.write(json.dumps({'text': 'testtext'}))
        return
