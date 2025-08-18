# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import logging
import argparse
from typing import Any, Dict, List

from django.db.models.query import QuerySet
from django.http import HttpRequest

from events.search_commands.decorators import search_command

latest_parser = argparse.ArgumentParser(
    prog="latest",
    description="Return the latest record in the QuerySet based on the provided field",
)

latest_parser.add_argument(
    "field",
    help="The field to determine the latest record",
)

@search_command(latest_parser)
def latest(request: HttpRequest, events: QuerySet, argv: List[str], environment: Dict[str, Any]) -> Dict[str, Any]:
    """
    Return the latest record in the QuerySet based on the provided field.

    Args:
        request (HttpRequest): The HTTP request object.
        events (QuerySet): The QuerySet to operate on.
        argv (List[str]): List of command-line arguments.
        environment (Dict[str, Any]): Dictionary used as a jinja2 environment (context) for rendering the arguments of a command.

    Returns:
        Dict[str, Any]: The latest record in the QuerySet.
    """
    log = logging.getLogger(__name__)
    log.info("In latest")
    args = latest_parser.parse_args(argv[1:])

    if not isinstance(events, QuerySet):
        log.critical(f"Type QuerySet expected, received {type(events)}")
        raise ValueError(
            f"latest can only operate on QuerySets like "
            "the output of the search command"
        )
    
    log.debug(f"Received {args=}")
    return events.latest(args.field)
