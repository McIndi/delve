# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import re
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
from pathlib import Path
from getpass import getpass
from typing import Dict, Optional

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
                __name__: {
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
    parser.add_argument(
        "--allow-basic",
        action="store_true",
        default=os.getenv("SYSLOG_RECEIVER_ALLOW_BASIC", "false").lower() in ("1", "true", "yes"),
        help="If specified, will allow BASIC_SYSLOG messages (a more permissive format) to be parsed",
    )
    return parser.parse_args(argv)

# Precompiled regexes for RFC 3164 and RFC 5424
RFC3164_REGEX = re.compile(
    r'^<(?P<pri>\d+)>'                        # <PRI>
    r'(?P<timestamp>'
    r'[A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+' # e.g., "Sep  5 06:50:27"
    r'(?P<host>\S+)\s+(?P<tag>\S+):\s*(?P<msg>.*)$' # HOST TAG: MSG
)
RFC5424_REGEX = re.compile(
    r'^<(?P<pri>\d+)>'                       # <PRI>
    r'(?P<version>\d)\s+'                   # VERSION
    r'(?P<timestamp>'
    r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?)\s+' # e.g., "2003-10-11T22:14:15.003Z"
    r'(?P<host>\S+)\s+(?P<appname>\S+)\s+'  # HOST APP-NAME
    r'(?P<procid>\S+)\s+(?P<msgid>\S+)\s+' # PROCID MSGID
    r'(?P<sd>-|\[.*?\])\s*(?P<msg>.*)$' # STRUCTURED-DATA MSG (optional)
)
BASIC_SYSLOG = re.compile(
    r'^<(?P<pri>\d+)>'                         # <PRI>
    r'(?:(?P<version>\d+)\s+)?'                # optional VERSION
    r'(?P<timestamp>('
        r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:[.,]\d+)?(?:Z|[+-]\d{2}:?\d{2})?'  # ISO/RFC3339 (with optional frac + TZ)
        r'|[A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}'                                # RFC3164 style (e.g., "Sep  5 06:50:27")
        r'|\d{10}(?:\.\d+)?'                                                          # Unix epoch seconds (optional .fractions)
        r'|\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}:\d{2}'                                     # 2025/09/05 06:50:27
        r'|\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}'                                     # 2025-09-05 06:50:27
    r'))\s+(?P<message>.*)$'
)
# Per-host RFC cache
host_rfc_map: Dict[str, str] = {}

def detect_rfc(message: str, allow_basic: bool = False) -> Optional[str]:
    """Detects RFC type for a syslog message."""
    if RFC5424_REGEX.match(message):
        return "RFC5424"
    elif RFC3164_REGEX.match(message):
        return "RFC3164"
    elif allow_basic and BASIC_SYSLOG.match(message):
        return "BASIC_SYSLOG"
    return None

def parse_syslog_message(message: str, host: str, logger: Optional[logging.Logger]=None, allow_basic: bool=False) -> Optional[dict]:
    """
    Parses a syslog message, detects RFC, and caches per host. Returns parsed fields or None.
    Logs errors for unrecognized messages.
    """
    rfc_type = host_rfc_map.get(host)
    if not rfc_type:
        rfc_type = detect_rfc(message, allow_basic=True)
        if rfc_type:
            host_rfc_map[host] = rfc_type
    if rfc_type == "RFC5424":
        match = RFC5424_REGEX.match(message)
    elif rfc_type == "RFC3164":
        match = RFC3164_REGEX.match(message)
    elif allow_basic and rfc_type == "BASIC_SYSLOG":
        match = BASIC_SYSLOG.match(message)
    else:
        match = None
    if match:
        return match.groupdict()
    if logger:
        logger.warning("Unrecognized syslog format from host %s: %s", host, message[:200])
    return None

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
    log.debug("Found server: %s", server)

    server_endpoint = args.server_endpoint
    log.debug("Found server_endpoint: %s", server_endpoint)

    no_verify = args.no_verify
    log.debug("Found no_verify: %s", no_verify)

    index = args.index
    log.debug("Found index: %s", index)

    host = args.host
    log.debug("Found host: %s", host)

    source = args.source
    log.debug("Found source: %s", source)

    sourcetype = args.sourcetype
    log.debug("Found sourcetype: %s", sourcetype)

    udp = args.udp
    log.debug("Found udp: %s", udp)

    tcp = args.tcp
    log.debug("Found tcp: %s", tcp)

    tcp_port = args.tcp_port
    log.debug("Found tcp_port: %s", tcp_port)

    tcp_cert = args.tcp_cert
    log.debug("Found tcp_cert: %s", tcp_cert)

    tcp_key = args.tcp_key
    log.debug("Found tcp_key: %s", tcp_key)

    udp_port = args.udp_port
    log.debug("Found udp_port: %s", udp_port)

    hostname = args.hostname
    log.debug("Found hostname: %s", hostname)

    sourcetype = args.sourcetype
    log.debug("Found sourcetype: %s", sourcetype)

    batch_size = args.batch_size
    log.debug("Found batch_size: %s", batch_size)

    max_queue_size = args.max_queue_size
    log.debug("Found max_queue_size: %s", max_queue_size)

    allow_basic = args.allow_basic
    log.debug("Found allow_basic: %s", allow_basic)

    line_ending = args.line_ending
    log.debug("Found line_ending: %s", line_ending)
    if line_ending == "windows":
        line_ending = "\r\n"
    elif line_ending == "linux":
        line_ending = "\n"
    elif line_ending == "macos":
        line_ending = "\r"

    username = args.username
    log.debug("Found username: %s", username)
    password = args.password

    if not username:
        if not sys.stdin.isatty():
            raise ValueError(
                "For non-interactive use, you must supply "
                "username and password on the command line "
                "or through environment variables: "
                "SYSLOG_RECEIVER_DELVE_USERNAME and SYSLOG_RECEIVER_DELVE_PASSWORD",
            )
        username = input("Please specify username: ")
    if not password:
        if not sys.stdin.isatty():
            raise ValueError(
                "For non-interactive use, you must supply "
                "username and password on the command line "
                "or through environment variables: "
                "SYSLOG_RECEIVER_DELVE_USERNAME and SYSLOG_RECEIVER_DELVE_PASSWORD",
            )
        password = getpass("Please specify password: ")

    # BUILD COMPUTED VALUES
    starttime = time()
    log.info("start: %s", starttime)

    url = f"{server}{server_endpoint}"
    log.debug("Found url: %s", url)
    basic_auth = requests.auth.HTTPBasicAuth(username, password)

    session = requests.Session()
    if no_verify:
        log.warning("Hostname verification has been disabled")
        session.verify = False
    session.auth = basic_auth
    log.debug("HTTP session initiated")

    event_queue = multiprocessing.Queue(maxsize=max_queue_size)
    sender_queue = multiprocessing.Queue(maxsize=max_queue_size)
    log.debug("Provisioning listeners and queues")
    class SyslogUDPHandler(socketserver.BaseRequestHandler):
        def handle(self):
            nonlocal index
            nonlocal source
            nonlocal sourcetype
            nonlocal event_queue

            # data = bytes.decode(self.request[0].strip())
            data = self.request[0].strip().decode()
            log.debug("Found data: %s", data)
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
            log.info("Added event to event_queue: %s", event_queue.qsize())

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
                log.error("Failed to configure TLS: %s", e)
                self.ssl_context = None

        def get_request(self):
            log.info("Received new message")
            (socket, addr) = super().get_request()
            if self.ssl_context:
                try:
                    socket = self.ssl_context.wrap_socket(socket, server_side=True)
                    log.debug("TLS handshake completed")
                except ssl.SSLError as e:
                    log.error("TLS handshake failed: %s", e)
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
            log.info("In handle")
            log.info("Event queue size: %s", self.queue.qsize())
            for line in self.rfile:
                line = line.decode().strip()
                log.debug("Found line: %s", line)
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
                log.info("Added event to event_queue: %s", self.queue.qsize())

        def finish(self):
            self.request.close()

    validator_proc = multiprocessing.Process(
        target=validator_process,
        args=(event_queue, sender_queue, log_level, allow_basic),
        daemon=True,
    )
    validator_proc.start()

    log.debug("Starting sender_process")
    sender_process = multiprocessing.Process(
        target=send_to_delve,
        args=(
            sender_queue,
            url,
            session,
            batch_size,
            log_level,
        ),
        daemon=True,
    )
    sender_process.start()

    def _terminate_processes():
        validator_proc.terminate()
        sender_process.terminate()
        sleep(5)
        validator_proc.close()
        sender_process.close()
    log.debug("Registering cleanup function for future exit")
    atexit.register(_terminate_processes)

    tcpThread = None
    tcp_server = None
    udpThread = None
    udpServer = None
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
            if tcp and isinstance(tcpThread, threading.Thread) and isinstance(tcp_server, ThreadedTCPServer) and not tcpThread.is_alive():
                log.debug("Restarting TCP listener")
                tcpThread = threading.Thread(target=tcp_server.serve_forever)
                tcpThread.daemon = True
                tcpThread.start()
            if udp and isinstance(udpThread, threading.Thread) and isinstance(udpServer, socketserver.UDPServer) and not udpThread.is_alive():
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
        if udp and udpServer:
            udpServer.shutdown()
            udpServer.server_close()
        if tcp and tcp_server:
            tcp_server.shutdown()
            tcp_server.server_close()
    return 0

def validator_process(event_queue, sender_queue, log_level, allow_basic):
    """
    Validates and parses events from event_queue, pushes valid ones to sender_queue.
    Drops invalid events and logs a warning.
    """
    import queue
    log = logging.getLogger(__name__)
    logging.config.dictConfig(get_logging_config(log_level, LOG_DIRECTORY / f'validator-{os.getpid()}.log'))
    while True:
        drained = 0
        try:
            # Block briefly to avoid tight spin when idle.
            event = event_queue.get(timeout=0.1)
            while True:
                # process first event then drain the rest without sleeping
                host = event.get("host")
                text = event.get("text")
                extracted = parse_syslog_message(text, host, logger=log, allow_basic=allow_basic)
                if extracted:
                    event["extracted_fields"] = extracted
                    sender_queue.put(event)
                    log.debug("→ sender_queue size ~ %s", sender_queue.qsize())
                drained += 1
                # Grab next if available; break when empty
                event = event_queue.get_nowait()
        except queue.Empty:
            if drained == 0:
                # only back off when we truly had nothing to do
                sleep(0.01)
            # else immediately loop to keep up
        except Exception as e:
            log.exception("Validator error: %s", e)

def send_to_delve(event_queue, url, session, batch_size, log_level):
    log = logging.getLogger(__name__)
    logging.config.dictConfig(get_logging_config(log_level, LOG_DIRECTORY / f'sender-{os.getpid()}.log'))
    timeout = 1 # seconds
    current_batch = []
    while True:
        log.debug("In sending loop")
        while len(current_batch) < batch_size:
            try:
                log.debug("Trying to get an item")
                item = event_queue.get_nowait()
                current_batch.append(item)
                log.info("Appended item to current_batch: %s, %s", len(current_batch), event_queue.qsize())
            except queue.Empty:
                log.info("Queue was empty")
                if current_batch:
                    try:
                        log.debug("Sending request to delve")
                        response = session.post(
                            url,
                            json=current_batch,
                        )
                        log.debug("Received response: %s", response.status_code)
                    except Exception as e:
                        log.debug("Exception raised: %s", e)
                        raise
                    log.debug("clearing current_batch")
                    current_batch.clear()
                    break
                else:
                    sleep(0.025)
        log.info("Batch size reached, sending to delve")
        if current_batch:
            response = session.post(
                url,
                json=current_batch,
            )
            current_batch.clear()

if __name__ == "__main__":
    listening = True
    sys.exit(main())