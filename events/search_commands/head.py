# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import logging
import argparse
from typing import Any, Dict, List, Union

from django.db.models.query import QuerySet
from django.http import HttpRequest

from events.util import resolve
from .decorators import search_command

parser = argparse.ArgumentParser(
    prog="head",
    description="Return the first n records of the result set",
)
parser.add_argument(
    "-n", "--number",
    type=int,
    default=10,
    help="Provide the number of events to return.",
)

@search_command(parser)
def head(request: HttpRequest, events: Union[QuerySet, List[Dict[str, Any]]], argv: List[str], environment: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Return the first n records of the result set.

    Args:
        request (HttpRequest): The HTTP request object.
        events (Union[QuerySet, List[Dict[str, Any]]]): The result set to operate on.
        argv (List[str]): List of command-line arguments.
        environment (Dict[str, Any]): Dictionary used as a jinja2 environment (context) for rendering the arguments of a command.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries with the first n records of the result set.
    """
    log = logging.getLogger(__name__)
    events = resolve(events)
    log.debug(f"Received {len(events)} events")
    log.debug(f"Received argv: {argv}")
    if "head" in argv:
        argv.pop(argv.index("head"))
    args = head.parser.parse_args(argv)

    for item in events[:args.number]:
        yield item
