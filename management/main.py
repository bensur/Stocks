from http.server import HTTPServer
from management.APIHandler import APIHandler
import lib.helpers as helpers
import os

PORT_NUMBER = 8080
API_KEY = "TEFK1KZP8TU5E11J"

if __name__ == '__main__':
    logger = helpers.get_logger()
    if 'ALPHAVANTAGE_API_KEY' not in os.environ:
        os.environ['ALPHAVANTAGE_API_KEY'] = API_KEY
    else:
        logger.debug("ALPHAVANTAGE_API_KEY='%s'" % os.environ['ALPHAVANTAGE_API_KEY'])
    print(('ALPHAVANTAGE_API_KEY' in os.environ))
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

    except Exception as e:
        logger.error("Encountered unhandled exception: %s" % e)
        server.socket.close()
