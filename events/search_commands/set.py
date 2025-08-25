# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import argparse
import logging
from typing import Any, Dict, List, Union

from django.db.models.query import QuerySet
from django.http import HttpRequest

from .util import cast
from .decorators import search_command

parser = argparse.ArgumentParser(
    prog="set",
    description="Set environment variables."
)
parser.add_argument(
    nargs="+",
    dest="expressions",
    help="The key-value pairs to set as environment variables",
)

@search_command(parser)
def set(request: HttpRequest, events: Union[QuerySet, List[Dict[str, Any]]], argv: List[str], environment: Dict[str, Any]) -> Union[QuerySet, List[Dict[str, Any]]]:
    """
    Set Jinja2 environment variables.

    Args:
        request (HttpRequest): The HTTP request object.
        events (Union[QuerySet, List[Dict[str, Any]]]): The result set to operate on.
        argv (List[str]): List of command-line arguments.
        environment (Dict[str, Any]): Dictionary used as a jinja2 environment (context) for rendering the arguments of a command.

    Returns:
        Union[QuerySet, List[Dict[str, Any]]]: The original result set with environment variables set.
    """
    log = logging.getLogger(__name__)
    log.debug(f"Found events: {events}")
    args = set.parser.parse_args(argv[1:])
    log.debug(f"Found args: {args}")
    for expression in args.expressions:
        log.debug(f"Found expression: {expression}")
        key, value = expression.split("=", 1)
        log.debug(f"Found key, value: {key}, {value}")
        environment[key] = cast(value)
    return events
