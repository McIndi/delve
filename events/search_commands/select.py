# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import argparse
import logging
import inspect
from types import GeneratorType
from typing import Any, Dict, List, Union

from django.db.models.query import QuerySet
from django.http import HttpRequest

from .decorators import search_command

parser = argparse.ArgumentParser(
    prog="select",
    description="Remove all but the specified fields from all events."
)
parser.add_argument(
    nargs="+",
    dest="fields",
    help="The fields to select from the result set",
)

@search_command(parser)
def select(request: HttpRequest, events: Union[QuerySet, List[Dict[str, Any]]], argv: List[str], environment: Dict[str, Any]) -> Union[QuerySet, List[Dict[str, Any]]]:
    """
    Remove all but the specified fields from all events.

    Args:
        request (HttpRequest): The HTTP request object.
        events (Union[QuerySet, List[Dict[str, Any]]]): The result set to operate on.
        argv (List[str]): List of command-line arguments.
        environment (Dict[str, Any]): Dictionary used as a jinja2 environment (context) for rendering the arguments of a command.

    Returns:
        Union[QuerySet, List[Dict[str, Any]]]: A QuerySet or list of events with only the specified fields.
    """
    log = logging.getLogger(__name__)
    args = select.parser.parse_args(argv[1:])
    log.info(f"In select, Found args: {args}")
    if isinstance(events, GeneratorType) or inspect.isgeneratorfunction(events) or isinstance(events, list):
        log.debug("Found events to be list or generator function.")
        for event in events:
            row = {}
            for field in args.fields:
                item = event
                for segment in field.split("__"):
                    log.debug(f"Trying segment: {segment}")
                    try:
                        item = item[segment]
                        log.debug(f"Found segment {segment}: {item}")
                    except KeyError:
                        log.warning(f"Received KeyError, field {segment} not in {item}")
                        item = None
                    except TypeError:
                        item = getattr(item, segment)
                row[field] = item
                log.debug(f"row[field]: {row[field]}")
            log.debug(f"Yielding row: {row}")
            yield row
    elif isinstance(events, QuerySet):
        log.debug(f"Found events to be instance of QuerySet.")
        for row in list(events.values(*args.fields)):
            log.debug(f"Yielding row: {row}")
            yield row
    else:
        log.warning(f"Found type(events): {type(events)}")
