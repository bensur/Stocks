from BaseHTTPServer import HTTPServer
from APIHandler import APIHandler

PORT_NUMBER = 8080

if __name__ == '__main__':
    try:
        # Create a web server and define the handler to manage the
        # incoming request
        server = HTTPServer(('', PORT_NUMBER), APIHandler)
        print 'Started httpserver on port ', PORT_NUMBER

        # Wait forever for incoming htto requests
        server.serve_forever()

    except KeyboardInterrupt:
        print '^C received, shutting down the web server'
        server.socket.close()
