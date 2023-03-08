import argparse
import logging
import os
import signal
import socketserver
import threading
import traceback

from lib.config_parser import ConfigParser
from lib.file_reader import FileReader
from lib.request_handler import request_handler
from lib.ssm_reader import SSMReader


def exception_handler(args):
    traceback.print_exception(None, args.exc_value, args.exc_traceback)
    os.kill(os.getpid(), signal.SIGINT)


def main():
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    print(f'[ALL] Log level: {log_level}')
    logging.basicConfig(format='[%(levelname)s] %(message)s', level=log_level)

    threading.excepthook = exception_handler

    parser = argparse.ArgumentParser(description='Accept and redirect http requests')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Bind to host')
    parser.add_argument('--port', type=int, default=8080, help='Listen port')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--ssm-config', type=str, help='SSM path')
    group.add_argument('--file-config', type=str, help='path to file')

    cli = parser.parse_args()

    if cli.ssm_config:
        config = SSMReader().read(cli.ssm_config)
    elif cli.file_config:
        config = FileReader().read(cli.file_config)
    else:
        raise Exception('Undefined config')

    config_parser = ConfigParser(config)

    logging.info(f'Start server at {cli.host}:{cli.port}')
    httpd = socketserver.TCPServer((cli.host, cli.port), request_handler(config_parser=config_parser))
    httpd.allow_reuse_address = True
    httpd.serve_forever()


if __name__ == '__main__':
    main()
