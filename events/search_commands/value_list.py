# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import argparse
import logging
from typing import Any, Dict, List, Union

from django.db.models.query import QuerySet
from django.http import HttpRequest

from events.util import resolve
from events.models import Query, Event
from .decorators import search_command

parser = argparse.ArgumentParser(
    prog="value_list",
    description="Reduce the result set to include the values from a given field",
)
parser.add_argument(
    "field",
    help="The field to extract the values from",
)

@search_command(parser)
def value_list(request: HttpRequest, events: Union[QuerySet, List[Dict[str, Any]]], argv: List[str], environment: Dict[str, Any]) -> List[Any]:
    """
    Reduce the result set to include the values from a given field.

    Args:
        request (HttpRequest): The HTTP request object.
        events (Union[QuerySet, List[Dict[str, Any]]]): The result set to operate on.
        argv (List[str]): List of command-line arguments.
        environment (Dict[str, Any]): Dictionary used as a jinja2 environment (context) for rendering the arguments of a command.

    Returns:
        List[Any]: A list of values for the specified field.
    """
    log = logging.getLogger(__name__)
    args = value_list.parser.parse_args(argv[1:])
    log.info(f"Found args: {args}")
    events = resolve(events)

    values = []
    for event in events:
        ret = event.get(args.field, "")
        log.info(f"Found ret: {ret}")
        values.append(ret)
    return values
