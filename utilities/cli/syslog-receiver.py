# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import os
import sys
import ssl
import queue
import atexit
import logging
import argparse
import threading
import socketserver
import logging.config
import multiprocessing

from getpass import getpass
from pathlib import Path
from time import (
    sleep,
    time,
)
import requests

HERE = Path(__file__).parent.parent.absolute()
DATA_DIRECTORY = HERE / "_data"
LOG_DIRECTORY = HERE / "log"

def get_logging_config(level, filename):
    return {
            "version": 1,
            "disable_existing_loggers": True,
            "formatters": {
                "verbose": {
                    "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
                    "format": '%(levelname)s %(name)s %(asctime)s %(module)s %(lineno)s %(process)d %(thread)d %(message)s',
                },
                "simple": {
                    "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
                    "format": "%(levelname)s %(message)s",
                },
            },
            "handlers": {
                "file": {
                    "level": level,
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": str(filename.absolute()),
                    "mode": "a",
                    "maxBytes": 5242880,
                    "backupCount": 10,
                    "formatter": "verbose",
                    "delay": True,
                },
                "console": {
                    "class": "logging.StreamHandler",
                    "level": level,
                    "formatter": "simple",
                },
            },
            "loggers": {
                f"{__name__}": {
                    "handlers": ["file", "console"],
                    "level": level,
                },
            }
        }

def configure_logging(log_level, log_file):
    logging.config.dictConfig(get_logging_config(log_level, log_file))


def parse_argv(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--server",
        default=os.getenv("SYSLOG_RECEIVER_SERVER", "http://localhost:8000"),
        help="The scheme, host and port of the server (ie. http://localhost:8000)"
    )
    parser.add_argument(
        "--server-endpoint",
        default=os.getenv("SYSLOG_RECEIVER_SERVER_ENDPOINT", "/api/events/"),
    )
    parser.add_argument(
        "--no-verify",
        action="store_true",
        default=os.getenv("SYSLOG_RECEIVER_NO_VERIFY", "false").lower() in ("1", "true", "yes"),
        help="If specified, TLS hostname verification will be disabled"
    )
    parser.add_argument(
        "-i",
        "--index",
        default=os.getenv("SYSLOG_RECEIVER_INDEX", "default"),
        help="The index in which to store the event",
    )
    parser.add_argument(
        "-H",
        "--host",
        default=os.getenv("SYSLOG_RECEIVER_HOST", None),
        help="The host to assign to the event, By default will assign "
             "the IP address of the client as the host",
    )
    parser.add_argument(
        "-s",
        "--source",
        default=os.getenv("SYSLOG_RECEIVER_SOURCE", "text/syslog"),
        help="The source to associate with the event",
    )
    parser.add_argument(
        "-t",
        "--sourcetype",
        default=os.getenv("SYSLOG_RECEIVER_SOURCETYPE", "text/syslog"),
        help="The sourcetype to associate with the event (also controls field "
             "extraction)",
    )
    parser.add_argument(
        "-u",
        "--username",
        default=os.getenv("SYSLOG_RECEIVER_DELVE_USERNAME", None),
        help="The username to use for authentication to Delve (if omitted, you will be "
             "prompted)",
    )
    parser.add_argument(
        "-p",
        "--password",
        default=os.getenv("SYSLOG_RECEIVER_DELVE_PASSWORD", None),
        help="The password to use for authentication to Delve (if omitted, you will "
             "be prompted)",
    )
    parser.add_argument(
        "--line-ending",
        choices=(
            "linux",
            "macos",
            "windows",
        ),
        default=os.getenv("SYSLOG_RECEIVER_LINE_ENDING", "linux"),
        help="Type of line endings to expect",
    )
    parser.add_argument(
        "--udp",
        action="store_true",
        default=os.getenv("SYSLOG_RECEIVER_UDP", "false").lower() in ("1", "true", "yes"),
        help="If specified, will listen for UDP messages",
    )
    parser.add_argument(
        "--tcp",
        action="store_true",
        default=os.getenv("SYSLOG_RECEIVER_TCP", "false").lower() in ("1", "true", "yes"),
        help="If specified, will listen for TCP messages",
    )
    parser.add_argument(
        "--tcp-port",
        type=int,
        default=int(os.getenv("SYSLOG_RECEIVER_TCP_PORT", 1514)),
        help="The TCP port to listen on",
    )
    parser.add_argument(
        "--tcp-cert",
        default=os.getenv("SYSLOG_RECEIVER_TCP_CERT", None),
        help="If this and --tcp-key are specified, the TCP listener will use TLS",
    )
    parser.add_argument(
        "--tcp-key",
        default=os.getenv("SYSLOG_RECEIVER_TCP_KEY", None),
        help="If this and --tcp-cert are specified, the TCP listener will use TLS",
    )
    parser.add_argument(
        "--udp-port",
        type=int,
        default=int(os.getenv("SYSLOG_RECEIVER_UDP_PORT", 2514)),
        help="The UDP port to listen on",
    )
    parser.add_argument(
        "--hostname",
        default=os.getenv("SYSLOG_RECEIVER_HOSTNAME", "127.0.0.1"),
        help="The hostname (or IP) to listen on"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=int(os.getenv("SYSLOG_RECEIVER_VERBOSE", 0)),
        help="If specified, increase logging verbosity (can be specified multiple times)",
    )
    parser.add_argument(
        "-l",
        "--log-file",
        type=Path,
        default=Path(os.getenv("SYSLOG_RECEIVER_LOG_FILE", LOG_DIRECTORY / f"syslog-receiver-{os.getpid()}.log")),
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=int(os.getenv("SYSLOG_RECEIVER_BATCH_SIZE", 10_000)),
        help="The number of events to send to the delve server per request",
    )
    parser.add_argument(
        "--max-queue-size",
        type=int,
        default=int(os.getenv("SYSLOG_RECEIVER_MAX_QUEUE_SIZE", 10_000)),
        help="The max number of events waiting to be uploaded to delve",
    )
    return parser.parse_args(argv)


def main(argv=None):
    listening = False
    if argv is None:
        argv = sys.argv[1:]
    args = parse_argv(argv=argv)

    log_level = 50 - (args.verbose*10)
    log_file = args.log_file
    configure_logging(log_level, log_file)
    log = logging.getLogger(__name__)

    server = args.server
    log.debug(f"Found {server=}")

    server_endpoint = args.server_endpoint
    log.debug(f"Found {server_endpoint=}")

    no_verify = args.no_verify
    log.debug(f"Found {no_verify=}")

    index = args.index
    log.debug(f"Found {index=}")

    host = args.host
    log.debug(f"Found {host=}")

    source = args.source
    log.debug(f"Found {source=}")

    sourcetype = args.sourcetype
    log.debug(f"Found {sourcetype=}")

    udp = args.udp
    log.debug(f"Found {udp=}")

    tcp = args.tcp
    log.debug(f"Found {tcp=}")

    tcp_port = args.tcp_port
    log.debug(f"Found {tcp_port=}")

    tcp_cert = args.tcp_cert
    log.debug(f"Found {tcp_cert=}")

    tcp_key = args.tcp_key
    log.debug(f"Found {tcp_key=}")

    udp_port = args.udp_port
    log.debug(f"Found {udp_port=}")

    hostname = args.hostname
    log.debug(f"Found {hostname=}")

    sourcetype = args.sourcetype
    log.debug(f"Found {sourcetype=}")

    batch_size = args.batch_size
    log.debug(f"Found {batch_size=}")

    max_queue_size = args.max_queue_size
    log.debug(f"Found {max_queue_size=}")

    line_ending = args.line_ending
    log.debug(f"Found {line_ending=}")
    if line_ending == "windows":
        line_ending = "\r\n"
    elif line_ending == "linux":
        line_ending = "\n"
    elif line_ending == "macos":
        line_ending = "\r"

    username = args.username
    log.debug(f"Found {username=}")
    password = args.password

    if not username:
        if not sys.stdin.isatty():
            raise ValueError(
                f"For non-interactive use, you must supply "
                f"username and password on the command line",
            )
        username = input("Please specify username: ")
    if not password:
        if not sys.stdin.isatty():
            raise ValueError(
                f"For non-interactive use, you must supply "
                f"username and password on the command line",
            )
        password = getpass.getpass("Please specify password: ")

    # BUILD COMPUTED VALUES
    starttime = time()
    log.info(f"start: {starttime}")

    url = f"{server}{server_endpoint}"
    log.debug(f"Found url: {url}")
    basic_auth = requests.auth.HTTPBasicAuth(username, password)

    session = requests.Session()
    if no_verify:
        log.warning(f"Hostname verification has been disabled")
        session.verify = False
    session.auth = basic_auth
    log.debug(f"HTTP session initiated")

    event_queue = multiprocessing.Queue(maxsize=max_queue_size)
    log.debug(f"Provisioning listeners")
    class SyslogUDPHandler(socketserver.BaseRequestHandler):
        def handle(self):
            log.debug("Inside handle")
            nonlocal index
            nonlocal source
            nonlocal sourcetype
            nonlocal event_queue

            # data = bytes.decode(self.request[0].strip())
            data = self.request[0].strip().decode()
            log.debug(f"Found {data=}")
            # socket = self.request[1]
            if host:
                item = {
                    "index": index,
                    "host": host,
                    "source": source,
                    "sourcetype": sourcetype,
                    "text": data,
                }
            else:
                item = {
                    "index": index,
                    "host": self.client_address[0],
                    "source": source,
                    "sourcetype": sourcetype,
                    "text": data,
                }
            event_queue.put(item)

    # class SyslogTCPServer(socketserver.TCPServer):
    class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
        request_queue_size = 25

        def __init__(self, event_queue, *args, certfile=None, keyfile=None, **kwargs):
            self.queue = event_queue
            self.ssl_context = None
            if certfile and keyfile:
                self.certfile = certfile
                self.keyfile = keyfile
                self._configure_tls()
            super().__init__(*args, **kwargs)

        def _configure_tls(self):
            try:
                self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                self.ssl_context.load_cert_chain(self.certfile, self.keyfile)
                log.debug("TLS configured successfully")
            except Exception as e:
                log.error(f"Failed to configure TLS: {e}")
                self.ssl_context = None

        def get_request(self):
            log.debug("Received request")
            (socket, addr) = super().get_request()
            if self.ssl_context:
                try:
                    socket = self.ssl_context.wrap_socket(socket, server_side=True)
                    log.debug("TLS handshake completed")
                except ssl.SSLError as e:
                    log.error(f"TLS handshake failed: {e}")
                    socket.close()
                    raise
            return socket, addr

        def finish_request(self, request, client_address):
            self.RequestHandlerClass(self.queue, request, client_address, self)

        def server_close(self):
            self.socket.close()
            self.shutdown()
            return super().server_close()

    class SyslogTCPHandler(socketserver.StreamRequestHandler):

        def __init__(self, event_queue, *args, **kwargs):
            self.queue = event_queue
            socketserver.StreamRequestHandler.__init__(self, *args, **kwargs)

        def handle(self):
            log.debug("In handle")
            for line in self.rfile:
                line = line.decode().strip()
                log.debug(f"Found {line=}")
                if host:
                    item = {
                        "index": index,
                        "host": host,
                        "source": source,
                        "sourcetype": sourcetype,
                        "text": line,
                    }
                else:
                    item = {
                        "index": index,
                        "host": self.client_address[0],
                        "source": source,
                        "sourcetype": sourcetype,
                        "text": line,
                    }
                self.queue.put(item)

        def finish(self):
            self.request.close()

    log.debug("Starting sender_process")
    sender_process = multiprocessing.Process(
        target=send_to_delve,
        args=(
            event_queue,
            url,
            session,
            batch_size,
            log_level,
        ),
        daemon=True,
    )
    sender_process.start()
    def _terminate_sender():
        sender_process.terminate()
        sleep(5)
        sender_process.close()
    log.debug("Registering cleanup function for future exit")
    atexit.register(_terminate_sender)

    try:
        if udp:
            # UDP server
            log.debug("Starting UDP listener")
            udpServer = socketserver.UDPServer((hostname, udp_port), SyslogUDPHandler)
            udpThread = threading.Thread(target=udpServer.serve_forever)
            udpThread.daemon = True
            udpThread.start()
            # udpServer.serve_forever(poll_interval=0.5)
        
        if tcp:
            # TCP server
            log.debug("Starting TCP listener")
            tcp_server = ThreadedTCPServer(
                event_queue,
                (hostname, tcp_port),
                SyslogTCPHandler,
                certfile=tcp_cert,
                keyfile=tcp_key,
            )
            tcpThread = threading.Thread(target=tcp_server.serve_forever)
            tcpThread.daemon = True
            tcpThread.start()
            # tcpServer.serve_forever(poll_interval=0.5)
        
        while True:
            log.debug("At the top of the main loop")
            if tcp and not tcpThread.is_alive():
                log.debug("Restarting TCP listener")
                tcpThread = threading.Thread(target=tcp_server.serve_forever)
                tcpThread.daemon = True
                tcpThread.start()
            if udp and not udpThread.is_alive():
                log.debug("Restarting UDP listener")
                udpThread = threading.Thread(target=udpServer.serve_forever)
                udpThread.daemon = True
                udpThread.start()
            sleep(1)
    except (IOError, SystemExit):
        raise
    except KeyboardInterrupt:
        log.warning("Crtl+C Pressed. Shutting down.")
        # listening = False
        if udp:
            udpServer.shutdown()
            udpServer.server_close()
        if tcp:
            tcp_server.shutdown()
            tcp_server.server_close()
    return 0

def send_to_delve(event_queue, url, session, batch_size, log_level):
    # configure_logging(level=log_level, filename=LOG_DIRECTORY / f'sender-{os.getpid()}.log')
    log = logging.getLogger(__name__)
    # logging.basicConfig(filename=LOG_DIRECTORY / 'sender.log', level=logging.DEBUG)
    logging.config.dictConfig(get_logging_config(log_level, LOG_DIRECTORY / f'sender-{os.getpid()}.log'))
    # log.debug(f"Found {log_level=}, {LOG_DIRECTORY / f'sender-{os.getpid()}.log'}")
    timeout = 1 # seconds
    current_batch = []
    while True:
        log.debug("In sending loop")
        while len(current_batch) < batch_size:
            try:
                log.debug("Trying to get an item")
                item = event_queue.get(timeout=timeout)
                log.debug(f"Got item, appending to current_batch")
                current_batch.append(item)
                log.debug(f"Got {item=}")
            except queue.Empty:
                log.debug("Queue was empty")
                if len(current_batch) > 0:
                    try:
                        log.debug("Sending request to delve")
                        response = session.post(
                            url,
                            json=current_batch,
                        )
                        log.debug(f"Received {response=}")
                    except Exception as e:
                        log.debug(f"Exception raised: {e=}")
                        raise
                    log.debug("clearing current_batch")
                    current_batch.clear()
                    break
                sleep(0.25)
        log.debug("Batch size reached, sending to delve")
        if len(current_batch) > 0:
            response = session.post(
                url,
                json=current_batch,
            )
            current_batch.clear()

if __name__ == "__main__":
    listening = True
    sys.exit(main())