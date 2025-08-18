# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import logging
import argparse
from typing import Any, Dict, List

from django.db.models.query import QuerySet
from django.http import HttpRequest

from events.search_commands.decorators import search_command

limit_parser = argparse.ArgumentParser(
    prog="limit",
    description="Limit the number of records in the QuerySet",
)

limit_parser.add_argument(
    "limit",
    type=int,
    help="The maximum number of records to return",
)

limit_parser.add_argument(
    "--offset",
    type=int,
    default=0,
    help="The number of records to skip before starting to return records",
)

@search_command(limit_parser)
def limit(request: HttpRequest, events: QuerySet, argv: List[str], environment: Dict[str, Any]) -> QuerySet:
    """
    Limit the number of records in the QuerySet.

    Args:
        request (HttpRequest): The HTTP request object.
        events (QuerySet): The QuerySet to operate on.
        argv (List[str]): List of command-line arguments.
        environment (Dict[str, Any]): Dictionary used as a jinja2 environment (context) for rendering the arguments of a command.

    Returns:
        QuerySet: A QuerySet with the limited number of records.
    """
    log = logging.getLogger(__name__)
    log.info("In limit")
    args = limit_parser.parse_args(argv[1:])

    if not isinstance(events, QuerySet):
        log.critical(f"Type QuerySet expected, received {type(events)}")
        raise ValueError(
            f"limit can only operate on QuerySets like "
            "the output of the search command"
        )
    
    log.debug(f"Received {args=}")
    return events[args.offset:args.offset + args.limit]
