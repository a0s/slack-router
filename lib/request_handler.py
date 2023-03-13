import re
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse

import requests

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

            route = None
            for route in config_parser.parsed['routes']:
                m = re.search(route['body_re'], body)
                if m:
                    break
            if route is None:
                self.send_response(404)
                self.wfile.write(b'Route not found')
                return

            headers = {}
            for h in self.headers:
                if h.lower() == 'host':
                    headers['Host'] = urlparse(route['url']).hostname
                else:
                    headers[h] = self.headers[h]

            response = requests.post(route['url'], headers=headers, data=body, stream=True)
            response_raw = response.raw.read()

            self.send_response(response.status_code)
            for k, v in response.headers.items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(response_raw)

    return Handler
