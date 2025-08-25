# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import logging
import argparse
from typing import Any, Dict, List

from django.db.models.query import QuerySet
from django.http import HttpRequest

from events.search_commands.decorators import search_command
from ._util import parse_field_expressions, generate_keyword_args

aggregate_parser = argparse.ArgumentParser(
    prog="aggregate",
    description="Perform aggregation on the result set",
) 
aggregate_parser.add_argument(
    "field_expressions",
    nargs="*",
    help="The field/expression to aggregate from the result set",
)

@search_command(aggregate_parser)
def aggregate(request: HttpRequest, events: QuerySet, argv: List[str], environment: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform aggregation on the result set.

    Args:
        request (HttpRequest): The HTTP request object.
        events (QuerySet): The QuerySet to operate on.
        argv (List[str]): List of command-line arguments.
        environment (Dict[str, Any]): Jinja2 environment (context) for rendering command arguments.

    Returns:
        Dict[str, Any]: A dictionary of aggregated values.
    """
    log = logging.getLogger(__name__)
    log.info("In aggregate")
    args = aggregate_parser.parse_args(argv[1:])

    if not isinstance(events, QuerySet):
        log.critical(f"Type QuerySet expected, received {type(events)}")
        raise ValueError(
            f"aggregate can only operate on QuerySets like "
            "the output of the search command"
        )
    
    log.debug(f"Received {args=}")
    parsed_expressions = parse_field_expressions(args.field_expressions)
    log.debug(f"Parsed expressions: {parsed_expressions}")
    positional_args, keyword_args = generate_keyword_args(parsed_expressions)
    log.debug(f"Generated positional_args: {positional_args}, keyword_args: {keyword_args}")
    return events.aggregate(*positional_args, **keyword_args)
