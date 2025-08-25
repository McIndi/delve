# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import argparse
from datetime import datetime
import logging
from typing import Any, Dict, List, Union

from dateutil.parser import parse
from django.db.models.query import QuerySet
from django.http import HttpRequest

from events.util import resolve
from .decorators import search_command

parser = argparse.ArgumentParser(
    prog="mark_timestamp",
    description="Parse the given fields from strings to datetime objects. Useful for use with filter search_command",
)
parser.add_argument(
    "fields",
    nargs="+",
    help="Provide the fields you would like to parse as datetime",
)

@search_command(parser)
def mark_timestamp(request: HttpRequest, events: Union[QuerySet, List[Dict[str, Any]]], argv: List[str], environment: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parse the given fields from strings to datetime objects. Useful for use with filter search_command.

    Args:
        request (HttpRequest): The HTTP request object.
        events (Union[QuerySet, List[Dict[str, Any]]]): The result set to operate on.
        argv (List[str]): List of command-line arguments.
        environment (Dict[str, Any]): Dictionary used as a jinja2 environment (context) for rendering the arguments of a command.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries with the specified fields parsed as datetime objects.
    """
    log = logging.getLogger(__name__)
    events = resolve(events)
    log.info(f"Received argv: {argv}")
    if "mark_timestamp" in argv:
        argv.pop(argv.index("mark_timestamp"))
    args = mark_timestamp.parser.parse_args(argv)
    log.info(f"Parsed args: {args}")
    for event in events:
        for field in args.fields:
            if field in event:
                if not isinstance(event[field], datetime):
                    event[field] = parse(event[field])
        yield event
