# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import logging
import argparse
from typing import Any, Dict, List

from django.db.models.query import QuerySet
from django.http import HttpRequest

from events.search_commands.decorators import search_command

distinct_parser = argparse.ArgumentParser(
    prog="distinct",
    description="Return distinct records from the QuerySet",
)

distinct_parser.add_argument(
    "field_names",
    nargs="*",
    help="The field names to use for distinct records. "
         "When you specify field names, you must provide "
         "an order_by() in the QuerySet, and the fields in "
         "order_by() must start with the fields in distinct(), "
         "in the same order.",
)

@search_command(distinct_parser)
def distinct(request: HttpRequest, events: QuerySet, argv: List[str], environment: Dict[str, Any]) -> QuerySet:
    """
    Return distinct records from the QuerySet.

    Args:
        request (HttpRequest): The HTTP request object.
        events (QuerySet): The QuerySet to operate on.
        argv (List[str]): List of command-line arguments.
        environment (Dict[str, Any]): Dictionary used as a jinja2 environment (context) for rendering the arguments of a command.

    Returns:
        QuerySet: A QuerySet with distinct records.
    """
    log = logging.getLogger(__name__)
    log.info("In distinct")
    args = distinct_parser.parse_args(argv[1:])

    if not isinstance(events, QuerySet):
        log.critical(f"Type QuerySet expected, received {type(events)}")
        raise ValueError(
            f"distinct can only operate on QuerySets like "
            "the output of the search command"
        )
    
    log.debug(f"Received {args=}")
    return events.distinct(*args.field_names)
