import logging
import re
import urllib
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse

import requests
import simplejson

from lib.config_parser import ConfigParser


def request_handler(config_parser: ConfigParser) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if urlparse(self.path).path == '/health':
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'OK')
            else:
                self.send_response(404)

        def do_POST(self):
            content_len = int(self.headers['Content-Length'])
            body = self.rfile.read(content_len).decode('utf-8')
            query = urllib.parse.parse_qs(body)
            logging.debug(f"Request query: {query['payload']}")
            if type(query['payload']) is list:
                raw_payload = query['payload'][0]
            else:
                raw_payload = query['payload']
            json = simplejson.loads(raw_payload)

            route = None
            for route in config_parser.parsed['routes']:
                if re.fullmatch(route['body_re'], json['text']):
                    break

            if route is None:
                self.send_response(418)
                return

            if 'channel' in route:
                json['channel'] = route['channel']

            headers = {}
            for h in self.headers:
                if h.lower() == 'host':
                    headers['Host'] = urlparse(route['url']).hostname
                else:
                    headers[h] = self.headers[h]

            request = requests.post(route['url'], headers=headers, data={'payload': simplejson.dumps(json)})
            self.send_response(request.status_code)
            for k, v in request.headers.items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(request.content)

    return Handler
