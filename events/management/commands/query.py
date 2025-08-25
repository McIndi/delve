# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

from getpass import getpass
from pprint import pprint
import argparse
import logging
import json

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django.forms.models import model_to_dict

import requests
import requests.auth
import rich

from events.models import (
    Event,
)

class Command(BaseCommand):
    help = "".join(
        (
            "Query the delve API",
        )
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "-u", "--username",
            help="The username for authentication to delve",
        )
        parser.add_argument(
            "-p", "--password",
            help="The password for authentication to delve",
        )
        parser.add_argument(
            "-s", "--server",
            default="http://localhost:8000",
            help="The delve server, including scheme and port (default http://localhost:8000)",
        )
        parser.add_argument(
            "-i", "--input-file",
            type=argparse.FileType("r"),
            default="-",
            help="The input file to read (default stdin)",
        )
        parser.add_argument(
            "-o", "--output-file",
            type=argparse.FileType("w"),
            default="-",
            help="The output file to write to (default stdout)",
        )
        parser.add_argument(
            "-n", "--name",
            default="",
            help="The name of the query."
        )
        parser.add_argument(
            "-f", "--format",
            choices=(
                "table",
                "json",
                # "xml",
            ),
            default="table",
            help="The output format (default pprint)",
        )

    def handle(self, *args, **options):
        log = logging.getLogger(__name__)
        input_file = options["input_file"]
        log.info(f"Found input_file: {input_file}")

        name = options["name"]
        log.info(f"Found name: '{name}'")

        output_file = options["output_file"]
        log.info(f"Found output_file: {output_file}")

        server = options["server"]
        log.info(f"Found server: {server}")
        if server is None:
            server = input("Please enter address of delve API (ex. https://localhost:8000)")

        username = options["username"]
        log.info(f"Found username: {username}")
        if username is None:
            username = input(f"Please enter username for {server}: ")

        password = options["password"]
        if password is None:
            password = getpass(f"Enter password for {username}: ")

        format = options["format"]
        log.info(f"Found format: {format}")

        if input_file.isatty():
            print("Please provide query. Use EOF (windows ctrl+Z Enter, Linux ctrl+D)")
        text = input_file.read()
        log.info(f"Found text: {text}")

        url = f"{server}/api/query/"
        auth = requests.auth.HTTPBasicAuth(
            username=username,
            password=password,
        )
        response = requests.post(
            url,
            auth=auth,
            data={
                "text": text,
                "name": name,
            }
        )
        log.info(f"Received response: {response}")
        response_json = response.json()
        log.info(f"Found response json: {response_json}")
        if format == "table":
            column_names = set()
            if isinstance(response_json, list):
                pass
            elif isinstance(response_json, dict):
                response_json = [response_json]
            else:
                response_json = [
                    {
                        "response": response_json,
                    }
                ]
            for event in response_json:
                column_names = column_names.union(event.keys())
            from rich.table import Column, Table
            from rich.console import Console
            table = Table(
                *list(column_names),
            )
            for event in response_json:
                table.add_row(*[json.dumps(value) for value in event.values()])
            console = Console()
            console.print(table)
            # print(json.dumps(response_json, indent=4))
        elif format == "json":
            print(json.dumps(response_json, indent=4))
