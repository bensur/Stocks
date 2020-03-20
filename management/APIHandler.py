import json
import lib.helpers as helpers
import traceback
from http.server import BaseHTTPRequestHandler
from management.StocksManager import StocksManager


logger = helpers.get_logger()


# This class will handle any incoming request
class APIHandler(BaseHTTPRequestHandler):
    sm = StocksManager()

    # Handler for the GET requests
    def do_GET(self):
        try:
            response = self.sm.handle(path=self.path, headers=self.headers, command=self.command)
        except Exception as e:
            response = {"response_code": 500, "response": json.dumps({"response_message": "An error occurred"})}
            logger.critical("An error occurred. Exception: %s" % e)
            traceback.print_tb(e.__traceback__)
        self.send_response(response['response_code'])
        if 'headers' in response:
            for header_k, header_v in response['headers']:
                self.send_header(header_k, header_v)
        else:
            self.send_header('Content-type', 'application/json')
        self.end_headers()
        # Send the response
        if 'response' in response:
            self.wfile.write(response['response'].encode('utf-8'))
        return

    # Handler for the POST requests
    def do_POST(self):
        content_len = int(self.headers.get('Content-Length', 0))
        if content_len:
            post_body = self.rfile.read(content_len)
        else:
            post_body = None
        try:
            response = self.sm.handle(path=self.path, headers=self.headers, command=self.command, post_data=post_body)
        except Exception as e:
            response = {"response_code": 500, "response": json.dumps({"response_message": "An error occurred"})}
            logger.critical("An error occurred. Exception: %s" % e)
            traceback.print_tb(e.__traceback__)
        self.send_response(response['response_code'])
        if 'headers' in response:
            for header_k, header_v in response['headers']:
                self.send_header(header_k, header_v)
        else:
            self.send_header('Content-type', 'application/json')
        self.end_headers()
        # Send the response
        if 'response' in response:
            self.wfile.write(response['response'].encode('utf-8'))
        return
        # try:
        #     response = self.sm.handle(path=self.path, headers=self.headers, command=self.command, post_data=post_body)
        # except Exception as e:
        #     print(e)
        #     response = {"response": "An error has occurred",
        #                 "response_code": 500}
        # finally:
        #     self.send_response(response['response_code'])
        #     if 'headers' in response:
        #         for header_k, header_v in response['headers']:
        #             self.send_header(header_k, header_v)
        #     else:
        #         self.send_header('Content-type', 'application/json')
        #     self.end_headers()
        #     # Send the response
        #     if 'response' in response:
        #         self.wfile.write(response['response'].encode('utf-8'))
        #     return
