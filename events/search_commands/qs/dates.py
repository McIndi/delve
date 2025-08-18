# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import logging
import argparse
from typing import Any, Dict, List

from django.db.models.query import QuerySet
from django.http import HttpRequest

from events.search_commands.decorators import search_command

dates_parser = argparse.ArgumentParser(
    prog="dates",
    description="Return a QuerySet of dates based on the provided field and kind",
)

dates_parser.add_argument(
    "field",
    help="The field to extract dates from",
)

dates_parser.add_argument(
    "kind",
    choices=["year", "month", "week", "day"],
    help="The kind of dates to return",
)

dates_parser.add_argument(
    "order",
    choices=["ASC", "DESC"],
    help="The order in which to retrieve the dates",
)

@search_command(dates_parser)
def dates(request: HttpRequest, events: QuerySet, argv: List[str], environment: Dict[str, Any]) -> QuerySet:
    """
    Return a QuerySet of dates based on the provided field and kind.

    Args:
        request (HttpRequest): The HTTP request object.
        events (QuerySet): The QuerySet to operate on.
        argv (List[str]): List of command-line arguments.
        environment (Dict[str, Any]): Dictionary used as a jinja2 environment (context) for rendering the arguments of a command.

    Returns:
        QuerySet: A QuerySet of dates.
    """
    log = logging.getLogger(__name__)
    log.info("In dates")
    args = dates_parser.parse_args(argv[1:])

    if not isinstance(events, QuerySet):
        log.critical(f"Type QuerySet expected, received {type(events)}")
        raise ValueError(
            f"dates can only operate on QuerySets like "
            "the output of the search command"
        )
    
    log.debug(f"Received {args=}")
    return events.dates(args.field, args.kind, args.order)
