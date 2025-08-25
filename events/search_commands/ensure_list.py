# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import argparse
import logging
from typing import Any, Dict, List, Union

from django.db.models.query import QuerySet
from django.http import HttpRequest

from events.util import resolve

from .decorators import search_command

parser = argparse.ArgumentParser(
    prog="ensure_list",
    description="Ensure that field contains a list. If any other type of value is in the specified field, it will be placed as a single item in a list",
)
parser.add_argument(
    "field",
    help="The field to ensure it is a list"
)

@search_command(parser)
def ensure_list(request: HttpRequest, events: Union[QuerySet, List[Dict[str, Any]]], argv: List[str], environment: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Ensure that field contains a list. If any other type of value is in the specified field, it will be placed as a single item in a list.

    Args:
        request (HttpRequest): The HTTP request object.
        events (Union[QuerySet, List[Dict[str, Any]]]): The result set to operate on.
        argv (List[str]): List of command-line arguments.
        environment (Dict[str, Any]): Dictionary used as a jinja2 environment (context) for rendering the arguments of a command.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries with the specified field ensured to be a list.
    """
    args = ensure_list.parser.parse_args(argv[1:])
    log = logging.getLogger(__name__)
    field = args.field
    events = resolve(events)
    for event in events:
        log.debug(f"Found event: {event}")
        if field in event:
            log.debug(f"field {field} is present in event: {event}")
            value = event.get(field)
            if not isinstance(value, list):
                event[field] = [value]
            yield event
        else:
            event[field] = [None]
            yield event
