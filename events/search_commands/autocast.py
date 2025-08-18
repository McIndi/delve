# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import logging
import argparse
from typing import Any, Dict, List, Union

from django.db.models.query import QuerySet
from django.http import HttpRequest

from .util import cast
from .decorators import search_command
from events.validators import QuerySetOrListOfDicts
from events.util import resolve

parser = argparse.ArgumentParser(
    prog="autocast",
    description="Attempt to cast fields to types based on their values."
)
parser.add_argument(
    "fields",
    nargs="*",
    help="Provide one or more fields to autocast",
)

@search_command(
    parser,
    input_validators=[
        QuerySetOrListOfDicts,
    ],
)
def autocast(request: HttpRequest, events: Union[QuerySet, List[Dict[str, Any]]], argv: List[str], environment: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Attempt to cast fields to types based on their values.

    Args:
        request (HttpRequest): The HTTP request object.
        events (Union[QuerySet, List[Dict[str, Any]]]): The result set to operate on.
        argv (List[str]): List of command-line arguments.
        environment (Dict[str, Any]): Dictionary used as a jinja2 environment (context) for rendering the arguments of a command.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries with fields cast to appropriate types.
    """
    log = logging.getLogger(__name__)
    log.info("In search_command autocast")
    events = resolve(events)
    log.debug(f"Received argv: {argv}")
    if "autocast" in argv:
        argv.pop(argv.index("autocast"))
    args = autocast.parser.parse_args(argv)

    ret = []
    for event in events:
        log.debug(f"Found event: {event}")
        for field in args.fields:
            # lhs = left-hand side, rhs right-hand side
            log.debug(f"Found field: {type(field)}({field})")
            event[field] = cast(event[field])
            log.debug(f"New type of field: {type(field)}({field})")
        yield event
