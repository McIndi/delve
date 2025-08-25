# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import re
import argparse
from typing import Any, Dict, List, Union

from django.db.models.query import QuerySet
from django.http import HttpRequest

from events.util import resolve

from .decorators import search_command

parser = argparse.ArgumentParser(
    prog="replace",
    description="Replace text matching a regular expression with a provided string.",
)
parser.add_argument(
    "-f",
    "--field",
    help="The field to perform the replacement on",
)
parser.add_argument(
    "expression",
    help="The regular expression to match",
)
parser.add_argument(
    "replacement",
    help="The string to replace the matched text with",
)

@search_command(parser)
def replace(request: HttpRequest, events: Union[QuerySet, List[Dict[str, Any]]], argv: List[str], environment: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Replace text matching a regular expression with a provided string.

    Args:
        request (HttpRequest): The HTTP request object.
        events (Union[QuerySet, List[Dict[str, Any]]]): The result set to operate on.
        argv (List[str]): List of command-line arguments.
        environment (Dict[str, Any]): Dictionary used as a jinja2 environment (context) for rendering the arguments of a command.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries with the specified text replaced.
    """
    events = resolve(events)
    args = replace.parser.parse_args(argv[1:])
    field = args.field
    expression = re.compile(args.expression)
    replacement = args.replacement
    for event in events:
        event[field] = expression.sub(replacement, event[field])
        yield event
