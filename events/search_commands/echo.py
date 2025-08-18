# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import argparse
import logging
from typing import Any, Dict, List, Union

from django.db.models.query import QuerySet
from django.http import HttpRequest

from .decorators import search_command

parser = argparse.ArgumentParser(
    prog="echo",
    description="Return the given expressions as an event appended to the result set.",
)
parser.add_argument(
    nargs="+",
    dest="expressions",
    help="The expressions to return as events",
)

@search_command(parser)
def echo(request: HttpRequest, events: Union[QuerySet, List[Dict[str, Any]]], argv: List[str], environment: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Return the given expressions as an event appended to the result set.

    Args:
        request (HttpRequest): The HTTP request object.
        events (Union[QuerySet, List[Dict[str, Any]]]): The result set to operate on.
        argv (List[str]): List of command-line arguments.
        environment (Dict[str, Any]): Dictionary used as a jinja2 environment (context) for rendering the arguments of a command.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries with the given expressions as events.
    """
    log = logging.getLogger(__name__)
    args = echo.parser.parse_args(argv[1:])
    log.debug(f"Found environment: {environment}")
    ret = []
    for expression in args.expressions:
        log.debug(f"Found expression: {type(expression)}({expression})")
        ret.append(
            {
                "expression": expression,
            }
        )
    for event in events:
        yield event
    for item in ret:
        yield item