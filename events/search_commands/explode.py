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
    prog="explode",
    description="Extract the nested JSON fields from an object and "
                "add them to the event. Also removes the original field.",
)
parser.add_argument(
    "--prefix",
    default="",
    help="String to be prefixed to the name of the fields "
            "that the explode operation creates"
)
parser.add_argument(
    "field",
    help="If field points to a JSON object, it's fields will be added "
    "to the event and the original field will be removed. "
    "Events without the specified fields will be omitted from the results"
)

@search_command(parser)
def explode(request: HttpRequest, events: Union[QuerySet, List[Dict[str, Any]]], argv: List[str], environment: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract the nested JSON fields from an object and add them to the event. Also removes the original field.

    Args:
        request (HttpRequest): The HTTP request object.
        events (Union[QuerySet, List[Dict[str, Any]]]): The result set to operate on.
        argv (List[str]): List of command-line arguments.
        environment (Dict[str, Any]): Dictionary used as a jinja2 environment (context) for rendering the arguments of a command.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries with the nested JSON fields extracted and added to the event.
    """
    args = explode.parser.parse_args(argv[1:])
    log = logging.getLogger(__name__)
    field = args.field
    events = resolve(events)
    for event in events:
        log.debug(f"Found event: {event}")
        
        if field in event:
            log.debug(f"field {field} is present in event: {event}")
            value = event.pop(field, None)
            log.debug(f"Event after pop: {event}")
            if isinstance(value, dict):
                event.update(
                    {f"{args.prefix}{k}": v for k, v in value.items()}
                )
                log.debug(f"Event after update: {event}")
                yield event
            elif value is None:
                log.debug(f"Found {value=}, removing field.")
                yield event
            else:
                log.debug(f"value {value} was not a dictionary")
                event.update({field: value})
                yield event
        else:
            yield event
