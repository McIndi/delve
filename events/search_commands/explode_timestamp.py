# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import argparse
import logging
from typing import Any, Dict, List, Union
from datetime import datetime, date, time

from django.db.models.query import QuerySet
from django.http import HttpRequest

from events.util import resolve

from .decorators import search_command

parser = argparse.ArgumentParser(
    prog="explode_timestamp",
    description="Extract the available fields in a timestamp field and add them as fields to the event with the optional prefix",
)
parser.add_argument(
    "--prefix",
    default="",
    help="String to be prefixed to the name of the fields that the operation creates"
)
parser.add_argument(
    "field",
    help="A field with a timestamp as the value. All available fields from the timestamp (year, month, day, hour, etc) will be added to the event",
)

@search_command(parser)
def explode_timestamp(request: HttpRequest, events: Union[QuerySet, List[Dict[str, Any]]], argv: List[str], environment: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract the available fields in a timestamp field and add them as fields to the event with the optional prefix.

    Args:
        request (HttpRequest): The HTTP request object.
        events (Union[QuerySet, List[Dict[str, Any]]]): The result set to operate on.
        argv (List[str]): List of command-line arguments.
        environment (Dict[str, Any]): Dictionary used as a jinja2 environment (context) for rendering the arguments of a command.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries with the extracted timestamp fields added.
    """
    args = explode_timestamp.parser.parse_args(argv[1:])
    log = logging.getLogger(__name__)
    field = args.field
    log.debug(f"Found {field=}")
    events = resolve(events)
    for event in events:
        log.debug(f"Found {event=}")
        
        if field in event:
            log.debug(f"{field=} present in {event=}")
            value = event.pop(field, None)
            log.debug(f"After pop: {event=}")
            if isinstance(value, datetime):
                event.update(
                    {
                        f"{args.prefix}year": value.year,
                        f"{args.prefix}month": value.month,
                        f"{args.prefix}day": value.day,
                        f"{args.prefix}hour": value.hour,
                        f"{args.prefix}minute": value.minute,
                        f"{args.prefix}second": value.second,
                        f"{args.prefix}microsecond": value.microsecond,
                    }
                )
                log.debug(f"Event after update: {event}")
                yield event
            elif isinstance(value, date):
                event.update(
                    {
                        f"{args.prefix}year": value.year,
                        f"{args.prefix}month": value.month,
                        f"{args.prefix}day": value.day,
                    }
                )
                log.debug(f"Event after update: {event}")
                yield event
            elif isinstance(value, time):
                event.update(
                    {
                        f"{args.prefix}hour": value.hour,
                        f"{args.prefix}minute": value.minute,
                        f"{args.prefix}second": value.second,
                        f"{args.prefix}microsecond": value.microsecond,
                    }
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
