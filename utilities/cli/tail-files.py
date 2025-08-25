# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

"""A CLI program to tail a file and create events in delve
through the delve REST API.
"""
import sys
import glob
import json
import queue
import atexit
import hashlib
import getpass
import logging
import logging.config
import argparse
from pathlib import Path
import multiprocessing
from time import (
    time,
    sleep,
)

import requests

HERE = Path(__file__).parent.parent.absolute()
DATA_DIRECTORY = HERE / "_data"
LOG_DIRECTORY = HERE / "log"

def parse_argv(argv):
    parser = argparse.ArgumentParser(
        description="Create events through the Delve REST API",
    )
    parser.add_argument(
        "--server",
        default="http://localhost:8000",
        help="The scheme, host and port of the server (ie. http://localhost:8000)"
    )
    parser.add_argument(
        "--no-verify",
        action="store_true",
        help="If specified, TLS hostname verification will be disabled"
    )
    parser.add_argument(
        "-i",
        "--index",
        default="default",
        help="The index in which to store the event",
    )
    parser.add_argument(
        "-H",
        "--host",
        default="localhost",
        help="The host to associate with the event",
    )
    # parser.add_argument(
    #     "-s",
    #     "--source",
    #     default="user",
    #     help="The source to associate with the event",
    # )
    parser.add_argument(
        "-t",
        "--sourcetype",
        default="plaintext",
        help="The sourcetype to associate with the event (also controls field "
            "extraction)",
    )
    parser.add_argument(
        "-u",
        "--username",
        help="The username to use for authentication (if omitted, you will be "
            "prompted)",
    )
    parser.add_argument(
        "-p",
        "--password",
        help="The password to use for authentication (if omitted, you will "
            "be prompted)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
    )
    parser.add_argument(
        "-l",
        "--log-file",
        type=Path,
        default=LOG_DIRECTORY / "tail-files.log",
    )
    parser.add_argument(
        "-d",
        "--delay",
        type=int,
        default=1,
        help="The number of seconds to sleep between API POST requests",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1_000,
        help="The number of events to send to the delve server per request",
    )
    parser.add_argument(
        "--max-queue-size",
        type=int,
        default=10_000,
        help="The max number of events waiting to be uploaded to delve",
    )
    # parser.add_argument(
    #     "-w",
    #     "--workers",
    #     type=int,
    #     default=cpu_count(),
    #     help="The number of workers to perform uploads",
    # )
    # parser.add_argument(
    #     "--event-regex",
    #     help="A regular expression to parse the file into events. Should match each event in its entirety"
    # )
    parser.add_argument(
        "patterns",
        nargs=argparse.REMAINDER,
        help="Glob patterns matching files to monitor "
             "(You might need to quote this to prevent shell expansion)",
    )
    args = parser.parse_args(argv)
    return args

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    args = parse_argv(argv)

    # CONFIGURE LOGGING
    log_level = 50 - (args.verbose * 10)
    log_file = args.log_file
    logging.config.dictConfig(
        {
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
                    "level": log_level,
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": str(log_file.absolute()),
                    "mode": "a",
                    "maxBytes": 5242880,
                    "backupCount": 10,
                    "formatter": "verbose",
                    # "delay": True,
                },
                "console": {
                    "class": "logging.StreamHandler",
                    "level": log_level,
                    "formatter": "simple",
                },
            },
            "loggers": {
                f"{__name__}": {
                    "handlers": ["file", "console"],
                    "level": log_level,
                },
            }
        }
    )

    log = logging.getLogger(__name__)

    # VALIDATE AND LOG ARGUMENTS
    server = args.server
    log.debug(f"Found {server=}")

    index = args.index
    log.debug(f"Found {index=}")

    host = args.host
    log.debug(f"Found {host=}")

    sourcetype = args.sourcetype
    log.debug(f"Found {sourcetype=}")

    delay = args.delay
    log.debug(f"Found {delay=}")

    max_queue_size = args.max_queue_size
    log.debug(f"Found {max_queue_size=}")

    batch_size = args.batch_size
    log.debug(f"Found {batch_size=}")

    patterns = args.patterns
    log.debug(f"Found {patterns=}")

    if isinstance(patterns, str):
        patterns = [patterns]

    no_verify = args.no_verify
    log.debug(f"Found {no_verify=}")

    username = args.username
    log.debug(f"Found username: {username}")
    password = args.password   # DO NOT LOG PASSWORD
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

    url = f"{server}/api/events/"
    log.debug(f"Found url: {url}")
    basic_auth = requests.auth.HTTPBasicAuth(username, password)

    session = requests.Session()
    if no_verify:
        log.warning(f"Hostname verification has been disabled")
        session.verify = False
    session.auth = basic_auth
    log.debug(f"HTTP session initiated")

    # INITIALIZE FILE POSITION DATA
    data_file = DATA_DIRECTORY.joinpath("tail-files.json")
    log.debug(f"Found {data_file=}")
    if data_file.exists():
        log.debug(f"{data_file=} exists")
        file_positions = json.loads(data_file.read_text())
    else:
        log.debug(f"{data_file=} does not exist")
        file_positions = {}
        data_file.write_text(json.dumps(file_positions))

    filenames = []
    for pattern in patterns:
        for filename in glob.iglob(pattern):
            filename = Path(filename)
            filenames.append(filename.absolute())
            if str(filename) not in file_positions:
                while filename.stat().st_size < 256:
                    sleep(0.1)
                file_positions[str(filename.absolute())] = {
                    "current_position": 0,
                    "hash": hashlib.sha256(filename.open('rb').read(256)).hexdigest(),
                }
                data_file.write_text(json.dumps(file_positions))

    event_queue = multiprocessing.Queue(maxsize=max_queue_size)
    logging_queue = multiprocessing.Queue(maxsize=max_queue_size)
    sender_process = multiprocessing.Process(
        target=send_to_delve,
        args=(
            event_queue,
            logging_queue,
            url,
            session,
            batch_size,
        ),
        daemon=True,
    )
    sender_process.start()
    def _terminate_sender():
        sender_process.terminate()
        sleep(5)
        sender_process.close()
    atexit.register(_terminate_sender)

    sleep(1)
    while not logging_queue.empty():
        level, message = logging_queue.get()
        log.debug(f"Found {level=}, {message=}")
        log.log(level=level, msg=message)

    # MAIN PROGRAM LOOP
    while True:
        for filename in filenames:
            while not logging_queue.empty():
                level, message = logging_queue.get()
                log.debug(f"Found {level=}, {message=}")
                log.log(level=level, msg=message)

            log.debug(f"Reading {filename=}")
            current_position = file_positions[str(filename)]["current_position"]
            log.debug(f"Found {current_position=}")
            try:
                size = filename.stat().st_size
            except:
                log.exception(f"{filename=} not found, could be rolling. Will circle back to it.")
                sleep(0.1)
                continue
            if current_position == size:
                # No new data
                log.debug(f"No new data for {filename=}")
                continue
            elif current_position > size:
                log.info(f"Found {current_position=}")
                while filename.stat().st_size < 256:
                    log.info(f"Waiting for {filename=} to reach at least 256 bytes")
                    sleep(0.1)
                file_positions[str(filename)] = {
                    "current_position": 0,
                    "hash": hashlib.sha256(filename.open('rb').read(256)).hexdigest(),
                }
                log.debug(f"Writing file positions {data_file=}")
                data_file.write_text(json.dumps(file_positions))
            with filename.open("r") as fin:
                log.debug(f"Opened {filename=} for reading, seeking to {current_position=}")
                fin.seek(current_position)
                while True:
                    line = fin.readline()
                    if not line:
                        break
                    while not ("\n" in line) and not ("\r" in line):
                        # Don't have a whole line yet
                        sleep(0.1)
                        line += fin.readline()
                    log.info(f"Found {line=}")
                    item = {
                        "index": index,
                        "host": host,
                        "source": str(filename),
                        "sourcetype": sourcetype,
                        "text": line,
                    }
                    event_queue.put(item)
                    current_position = fin.tell()
                    log.debug(f"Now {current_position=}")
            
            file_positions[str(filename)]["current_position"] = current_position
            log.info(f"Writing to {data_file=}")
            data_file.write_text(json.dumps(file_positions))
            log.debug(f"Checking {logging_queue=} for log messages")
            while not logging_queue.empty():
                level, message = logging_queue.get()
                log.debug(f"Found {level=}, {message=}")
                log.log(level=level, msg=message)

def send_to_delve(event_queue, logging_queue, url, session, batch_size):
    timeout = 1 # seconds
    current_batch = []
    logging_queue.put((logging.DEBUG, "Sender process entering main loop."))
    while True:
        while len(current_batch) < batch_size:
            logging_queue.put((logging.DEBUG, f"{len(current_batch)=} less than {batch_size=}"))
            try:
                item = event_queue.get(timeout=timeout)
                logging_queue.put((logging.DEBUG, f"Found {item=}"))
                current_batch.append(item)

            except queue.Empty:
                logging_queue.put((logging.DEBUG, f"Event queue is empty"))
                if len(current_batch) > 0:
                    logging_queue.put((logging.INFO, "Sending request to delve"))
                    try:
                        response = session.post(
                            url,
                            json=current_batch,
                        )
                        logging_queue.put((logging.DEBUG, f"Found {response.text}"))
                    except Exception as e:
                        logging_queue.put((logging.ERROR, f"Found exception: {e=}"))
                        raise
                    logging_queue.put((logging.INFO, f"Received {response=} from delve"))
                    current_batch.clear()
                sleep(0.25)
        if len(current_batch) > 0:
            logging_queue.put((logging.INFO, "Sending request to delve"))
            response = session.post(
                url,
                json=current_batch,
            )
            logging_queue.put((logging.INFO, f"Received {response=} from delve"))
            current_batch.clear()
        
if __name__ == "__main__":
    log = logging.getLogger(__name__)
    try:
        sys.exit(main())
    except:
        log.exception(f"An unhandled exception has occurred")
