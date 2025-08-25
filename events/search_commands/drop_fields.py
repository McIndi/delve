# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import argparse
import logging
from typing import Any, Dict, List, Union

from django.db.models.query import QuerySet
from django.http import HttpRequest

from .decorators import search_command
from events.util import resolve
from events.models import (
    BaseEvent,
)
from events.validators import (
    QuerySetOrListOfDictsOrEvents
)

parser = argparse.ArgumentParser(
    prog="drop_fields",
    description="Remove the specified fields from the result set.",
)
parser.add_argument(
    "fields",
    nargs="+",
    help="Field to drop if present from all events."
)

@search_command(
    parser,
    input_validators=[
        QuerySetOrListOfDictsOrEvents,
    ]
)
def drop_fields(request: HttpRequest, events: Union[QuerySet, List[Dict[str, Any]]], argv: List[str], environment: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Remove the specified fields from the result set.

    Args:
        request (HttpRequest): The HTTP request object.
        events (Union[QuerySet, List[Dict[str, Any]]]): The result set to operate on.
        argv (List[str]): List of command-line arguments.
        environment (Dict[str, Any]): Dictionary used as a jinja2 environment (context) for rendering the arguments of a command.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries with specified fields removed.
    """
    args = drop_fields.parser.parse_args(argv[1:])
    log = logging.getLogger(__name__)
    fields = args.fields
    log.debug(f"Found fields: {fields}")
    events = resolve(events)

    for event in events:
        for field in fields:
            log.debug(f"Checking event for field: {field}")
            try:
                event.pop(field)
            except:
                pass
        yield event
