from http.server import HTTPServer
from management.APIHandler import APIHandler
import lib.helpers as helpers

PORT_NUMBER = 8080

if __name__ == '__main__':
    logger = helpers.get_logger()
    try:
        # Create a web server and define the handler to manage the
        # incoming request
        server = HTTPServer(('', PORT_NUMBER), APIHandler)
        logger.info('Started httpserver on port %i' % PORT_NUMBER)

        # Wait forever for incoming http requests
        server.serve_forever()

    except KeyboardInterrupt:
        logger.info('^C received, shutting down the web server')
        server.socket.close()
