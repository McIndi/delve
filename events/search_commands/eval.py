# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import logging
import argparse
from typing import Any, Dict, List, Union

from django.db.models.query import QuerySet
from django.http import HttpRequest

from events.util import resolve

from .util import cast
from .decorators import search_command

parser = argparse.ArgumentParser(
    prog="eval",
    description="Set the value of a field on each event."
)
parser.add_argument(
    "expressions",
    nargs="+",
    help="Provide one or more expressions to evaluate",
)

@search_command(parser)
def eval(request: HttpRequest, events: Union[QuerySet, List[Dict[str, Any]]], argv: List[str], environment: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Set the value of a field on each event.

    Args:
        request (HttpRequest): The HTTP request object.
        events (Union[QuerySet, List[Dict[str, Any]]]): The result set to operate on.
        argv (List[str]): List of command-line arguments.
        environment (Dict[str, Any]): Dictionary used as a jinja2 environment (context) for rendering the arguments of a command.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries with the evaluated expressions set as fields.
    """
    log = logging.getLogger(__name__)
    events = resolve(events)
    log.info(f"Received argv: {argv}")
    args = eval.parser.parse_args(argv[1:])
    log.debug(f"Found args: {args}")
    ret = []
    for event in events:
        log.debug(f"Found event: {event}")
        for expression in args.expressions:
            log.info(f"Found expression: {expression}")
            lhs, rhs = expression.split("=", 1)
            log.info(f"Found lhs, rhs: {lhs}, {rhs}")
            if rhs.startswith("$"):
                rhs_symbol = rhs.replace("$", "")
                if rhs_symbol in event:
                    event[lhs] = cast(event[rhs_symbol])
                else:
                    event[lhs] = cast(rhs)    
            else:
                event[lhs] = cast(rhs)
        yield event
