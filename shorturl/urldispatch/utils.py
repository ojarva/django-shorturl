import urllib2
from urlparse import urlparse
import socket
import datetime

def get_destination_url(destination_url):
    for item in ["ttp://", "tp://", "p://", "://", "//", "/"]:
        if destination_url.startswith(item):
             destination_url = destination_url.replace(item, "", 1)
    parsed = urlparse(destination_url)
    if len(parsed.scheme) == 0:
        destination_url = "http://%s" % destination_url
    return destination_url

def test_url(destination_url):

    data = {}

    def fail(message):
        data["status_current"] = False
        data["status_last_error"] = message
        data["status_working_since"] = None
        data["status_last_fail"] = datetime.datetime.now()

    def success():
        data["status_current"] = True

    class HeadRequest(urllib2.Request):
        def get_method(self):
            return "HEAD"

    parsed_destination = urlparse(destination_url)

    def test_http():
        try:
            a = urllib2.urlopen(HeadRequest(destination_url), None, 3)
            headers = dict(a.info())
            success()
        except (urllib2.HTTPError, urllib2.URLError), err:
            fail(str(err))
        except ValueError:
            fail(str("Invalid URL"))

    def test_socket():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        try:
            port = parsed_destination.port
            if port is None:
                port = 80
                try:
                    port = socket.getservbyname(parsed_destination.scheme)
                except socket.error:
                    pass
            s.connect((parsed_destination.hostname, port))
            s.close()
            success()
        except socket.gaierror:
            fail("Can't resolve DNS name")
        except socket.timeout:
            fail("Connection timed out")
        except (socket.herror, socket.error), err:
            fail(str(err))

    if parsed_destination.scheme.startswith("http"):
        test_http()
    else:
        test_socket()

    return data
