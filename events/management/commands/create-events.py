# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

"""A CLI program to create an event in delve through the
delve REST API.
"""
import re
import sys
import json
# import argparse
import getpass
import logging
from pathlib import Path
from time import (
    time,
)
from concurrent.futures import (
    ThreadPoolExecutor,
    # ProcessPoolExecutor,
)
from multiprocessing import (
    cpu_count
)

from django.core.management.base import BaseCommand, CommandError

import requests

def profile(func, *args, **kwargs):
    def inner():
        start = time()
        result = func(*args, **kwargs)
        elapsed = time() - start
        return (elapsed, result)
    return inner

def log_result(f):
    log = logging.getLogger(__name__)
    elapsed, result = f.result()
    try:
        result_json = result.json()
    except:
        result_json = None
        log.info(f"Found response: {result.text}")
    log.debug(f"Found {result_json=}")
    if len(result_json) == 1:
        log.info(
            f"Processed: {result.request.body}, {result_json}, "
            f"elapsed time {elapsed}."
        )
    else:
        log.info(f"Finished processing: {len(result_json)} records, elapsed time {elapsed}.")

def submit_job(func, queue, executor):
    log = logging.getLogger(__name__)
    log.info(
        f"Queue has reached sufficient size or file is exhausted"
        f", {len(queue)}, sending messages to server",
    )
    future = executor.submit(func)
    future.add_done_callback(
        lambda x: log_result(x)
    )
    queue.clear()
    i = 0

class Command(BaseCommand):
    help = "Create events through the Delve REST API"
    suppressed_base_arguments = [
        "--verbosity",
    ]

    def add_arguments(self, parser):
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
        parser.add_argument(
            "-s",
            "--source",
            default="user",
            help="The source to associate with the event",
        )
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
            "-V",
            "--verbose",
            action="count",
            default=0,
        )
        parser.add_argument(
            "-l",
            "--log-file",
            type=Path,
            # default=settings.BASE_DIR / "log" / "create-events.log",
        )
        parser.add_argument(
            "-d",
            "--delay",
            type=int,
            default=1,
            help="The number of seconds to sleep between API POST requests",
        )
        parser.add_argument(
            "-q",
            "--queue-size",
            type=int,
            default=5,
            help="The number of events for the queue of bulk uploads",
        )
        parser.add_argument(
            "-w",
            "--workers",
            type=int,
            default=cpu_count(),
            help="The number of workers to perform uploads",
        )
        parser.add_argument(
            "infile",
            nargs='?',
            type=Path,
            default=sys.stdin,
            help="The file to read from",
        )
        parser.add_argument(
            "--event-regex",
            help="A regular expression to parse the file into events. Should match each event in its entirety"
        )
        # parser.add_argument('infile', )

    def handle(self, *args, **options):
        log_level = 50-options["verbose"]*10
        logging.basicConfig(
            level=log_level,
        )
        log = logging.getLogger(__name__)
        log_file = options["log_file"]
        if log_file:
            log.info(f"adding logger to {log_file}")
            file_handler = logging.FileHandler(
                filename=log_file,
                mode="w",
            )
            log.addHandler(file_handler)
        server = options["server"]
        log.debug(f"Found server: {server}")
        index = options["index"]
        log.debug(f"Found index: {index}")
        host = options["host"]
        log.debug(f"Found host: {host}")
        source = options["source"]
        log.debug(f"Found source: {source}")
        sourcetype = options["sourcetype"]
        log.debug(f"Found sourcetype: {sourcetype}")
        infile = options["infile"]
        log.debug(f"Found infile: {infile}")
        delay = options["delay"]
        log.debug(f"Found delay: {delay}")
        queue_size = options["queue_size"]
        log.debug(f"Found queue_size: {queue_size}")
        workers = options["workers"]
        log.debug(f"Found workers: {workers}")
        username = options["username"]
        log.debug(f"Found username: {username}")
        password = options["password"]

        event_regex = options["event_regex"]
        log.debug(f"Found {event_regex=}")
        no_verify = options["no_verify"]
        log.debug(f"Found {no_verify=}")

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

        starttime = time()
        log.info(f"start: {starttime}")

        url = f"{server}/api/events/"
        log.debug(f"Found url: {url}")
        basic_auth = requests.auth.HTTPBasicAuth(username, password)

        queue = []
        session = requests.Session()
        if no_verify:
            log.warning(f"Hostname verification has been disabled")
            session.verify = False
        session.auth = basic_auth
        with ThreadPoolExecutor(max_workers=workers) as executor:
            with infile.open("r") as fin:
                if event_regex:
                    iterable = re.findall(event_regex, fin.read())
                else:
                    iterable = fin
                for line in iterable:
                    log.debug(f"Found line: {line}, appending to outgoing queue.")
                    if not line.strip():
                        # line is only whitespace
                        log.debug(f"Line is only whitespace, skipping.")
                        continue
                    item = {
                        "index": index,
                        "host": host,
                        "source": source,
                        "sourcetype": sourcetype,
                        "text": line,
                    }
                    log.debug(f"Appending item to queue: {type(item)}({json.dumps(item)})")
                    queue.append(item)

                    if len(queue) >= queue_size:
                        log.info("queue is full, submit this batch of events")
                        submit_job(
                            profile(
                                session.post,
                                url,
                                json=queue.copy(),
                            ),
                            queue,
                            executor,
                        )
                        # queue.clear()
                else:
                    # ^ This else belongs to the for loop, for more information 
                    # see here: https://docs.python.org/3/tutorial/controlflow.html#break-and-continue-statements-and-else-clauses-on-loops
                    #
                    # Loop has finished, but queue is not full.
                    # submit a job for the events left in the queue
                    if queue:
                        log.info(f"file is exhausted, submiting final batch of events. size: {len(queue)}")
                        submit_job(
                            profile(
                                session.post,
                                url,
                                json=queue.copy(),
                            ),
                            queue,
                            executor
                        )
                        # queue.clear()
        
        endtime = time()
        log.info(f"Elapsed time for total execution: {endtime - starttime}")
