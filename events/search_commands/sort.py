# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import argparse
import logging
from typing import Any, Dict, List, Union

from django.db.models.query import QuerySet
from django.http import HttpRequest
from operator import itemgetter

from events.util import resolve
from .decorators import search_command

parser = argparse.ArgumentParser(
    prog="sort",
    description="Sort the result set by the given fields",
)
parser.add_argument(
    "-d", "--descending",
    action="store_true",
    help="If specified, sorting will be done in descending order",
)
parser.add_argument(
    nargs="*",
    dest="fields",
    help="The fields to sort by",
)

@search_command(parser)
def sort(request: HttpRequest, events: Union[QuerySet, List[Dict[str, Any]]], argv: List[str], environment: Dict[str, Any]) -> Union[QuerySet, List[Dict[str, Any]]]:
    """
    Sort the result set by the specified fields.

    Args:
        request (HttpRequest): The HTTP request object.
        events (Union[QuerySet, List[Dict[str, Any]]]): The result set to operate on.
        argv (List[str]): List of command-line arguments.
        environment (Dict[str, Any]): Dictionary used as a jinja2 environment (context) for rendering the arguments of a command.

    Returns:
        Union[QuerySet, List[Dict[str, Any]]]: A sorted QuerySet or list of events.
    """
    log = logging.getLogger(__name__)
    log.debug(f"Found events: {events}")
    args = sort.parser.parse_args(argv[1:])
    log.debug(f"Found args: {args}")

    events = resolve(events)

    if not args.fields:
        log.info("No fields specified, using default sort")
        return sorted(
            events,
            reverse=args.descending,
        )
    else:
        log.debug(f"Sorting by fields: {args.fields}")
        events.sort(
            reverse=args.descending,
            key=itemgetter(*args.fields),
        )

    return events
