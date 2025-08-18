# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import logging
import argparse
from typing import Any, Dict, List

from django.db.models.query import QuerySet
from django.http import HttpRequest

from events.search_commands.decorators import search_command

datetimes_parser = argparse.ArgumentParser(
    prog="datetimes",
    description="Return a list of datetime objects representing all available datetimes in the QuerySet",
)
datetimes_parser.add_argument(
    "field",
    help="The field to retrieve datetimes from",
)
datetimes_parser.add_argument(
    "kind",
    choices=["year", "month", "week", "day", "hour", "minute", "second"],
    help="The kind of datetimes to retrieve",
)
datetimes_parser.add_argument(
    "order",
    choices=["ASC", "DESC"],
    help="The order in which to retrieve the datetimes",
)
datetimes_parser.add_argument(
    "--tz",
    default=None,
    help="The timezone to use for the datetimes",
)

@search_command(datetimes_parser)
def datetimes(request: HttpRequest, events: QuerySet, argv: List[str], environment: Dict[str, Any]) -> QuerySet:
    """
    Return a list of datetime objects representing all available datetimes in the QuerySet.

    Args:
        request: The HTTP request object.
        events: The QuerySet to operate on.
        argv: List of command-line arguments.
        environment: Dictionary used as a jinja2 environment (context) for rendering the arguments of a command.

    Returns:
        QuerySet: A QuerySet of datetime objects.
    """
    log = logging.getLogger(__name__)
    log.info("In datetimes")
    args = datetimes_parser.parse_args(argv[1:])

    if not isinstance(events, QuerySet):
        log.critical(f"Type QuerySet expected, received {type(events)}")
        raise ValueError(
            f"datetimes can only operate on QuerySets like "
            "the output of the search command"
        )
    
    log.debug(f"Received {args=}")
    return events.datetimes(args.field, args.kind, args.order, tzinfo=args.tz)
