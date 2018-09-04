import json
import lib.helpers as helpers
from BaseHTTPServer import BaseHTTPRequestHandler
from StocksManager import StocksManager


logger = helpers.get_logger()


# This class will handles any incoming request
class APIHandler(BaseHTTPRequestHandler):
    sm = StocksManager()

    # Handler for the GET requests
    def do_GET(self):
        response = self.sm.handle(path=self.path, headers=self.headers, command=self.command)
        self.send_response(response['response_code'])
        if 'headers' in response:
            for header_k, header_v in response['headers']:
                self.send_header(header_k, header_v)
        else:
            self.send_header('Content-type', 'application/json')
        self.end_headers()
        # Send the response
        if 'response' in response:
            self.wfile.write(response['response'])
        return

    # Handler for the POST requests
    def do_POST(self):
        content_len = int(self.headers.getheader('content-length', 0))
        if content_len:
            post_body = self.rfile.read(content_len)
        else:
            post_body = None
        response = self.sm.handle(path=self.path, headers=self.headers, command=self.command, post_data=post_body)
        self.send_response(response['response_code'])
        if 'headers' in response:
            for header_k, header_v in response['headers']:
                self.send_header(header_k, header_v)
        else:
            self.send_header('Content-type', 'application/json')
        self.end_headers()
        # Send the response
        if 'response' in response:
            self.wfile.write(response['response'])
        return
