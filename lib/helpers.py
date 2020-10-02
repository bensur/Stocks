import logging
import pycurl
from io import StringIO


def curl(url, curl_headers=None, post_data="", username=None, password=None, cookie_file=None, cookie_jar=None):
    """
    Preform curl with given options to given URL and return response
    :param url: URL to send request to
    :type url: str
    :param curl_headers: List of headers to add to request
    :type curl_headers: list
    :param post_data: POST data string to add to request
    :type post_data: str
    :param username: Username to use with basic authentication
    :type username: str
    :param password: Password to use with basic authentication
    :type password: str
    :param cookie_file: File name to use as cookie file
    :type cookie_file: str
    :param cookie_jar: File name to use as cookie jar
    :type cookie_jar: str
    :return: Hash (dict) with 'response_body' and 'response_code' (http code)
    :rtype: dict
    """
    if curl_headers is None:
        curl_headers = []
    curl_buffer = StringIO()
    curl_obj = pycurl.Curl()
    curl_obj.setopt(pycurl.URL, url.encode('iso-8859-1'))
    # Follow redirection
    curl_obj.setopt(pycurl.FOLLOWLOCATION, True)
    # Disable peer verification
    curl_obj.setopt(pycurl.SSL_VERIFYPEER, 0)
    curl_obj.setopt(pycurl.SSL_VERIFYHOST, 0)
    # Set token header if not empty
    if curl_headers:
        curl_obj.setopt(pycurl.HTTPHEADER, curl_headers)
    # Add post data if available
    if post_data:
        curl_obj.setopt(pycurl.POST, 1)
        curl_obj.setopt(pycurl.POSTFIELDS, post_data)
    # Add basic auth if username & password provided
    if username is not None and username and password is not None and password:
        curl_obj.setopt(pycurl.HTTPAUTH, pycurl.HTTPAUTH_BASIC)
        curl_obj.setopt(pycurl.USERPWD, '%s:%s' % (username, password))
    if cookie_file is not None and cookie_file:
        curl_obj.setopt(pycurl.COOKIEFILE, cookie_file)
    if cookie_jar is not None and cookie_jar:
        curl_obj.setopt(pycurl.COOKIEJAR, cookie_jar)
    # Write data to buffer
    curl_obj.setopt(pycurl.WRITEFUNCTION, curl_buffer.write)
    # Make the request and close connection
    curl_obj.perform()
    response_code = curl_obj.getinfo(pycurl.RESPONSE_CODE)
    curl_obj.close()
    # Return response
    return {'response_body': curl_buffer.getvalue(), 'response_code': response_code}


def get_logger(loglevel=logging.DEBUG):
    """
    Return logger object initialized according to config file
    :return: logger object
    :rtype logging.Logger
    """
    # Set logger
    logger = logging.getLogger(__name__)
    logger.setLevel(loglevel)
    # Create file handler
    # fh = logging.FileHandler(config['log_file'])
    # fh.setLevel(get_log_level(config['log_level']))
    # Create console handler
    ch = logging.StreamHandler()
    # Create formatter and add it to the handlers
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s -- %(message)s', "%Y-%m-%dT%H:%M:%S")
    ch.setFormatter(formatter)
    # fh.setFormatter(formatter)
    # Add the handlers to logger
    if not logger.hasHandlers():
        logger.addHandler(ch)
    # logger.addHandler(fh)
    return logger

