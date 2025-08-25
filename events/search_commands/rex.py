# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import re
import argparse
import logging
from typing import Any, Dict, List, Union

from django.db.models.query import QuerySet
from django.http import HttpRequest

from events.util import resolve

from .decorators import search_command

parser = argparse.ArgumentParser(
    prog="rex",
    description="Use regular expressions to extract values from a field and store in extracted_fields",
)
parser.add_argument(
    "-f", "--field",
    default="text",
    help="The field to run the regular expression against"
)
parser.add_argument(
    nargs="+",
    dest="expressions",
    help="The regular expressions to use for extraction",
)

@search_command(parser)
def rex(request: HttpRequest, events: Union[QuerySet, List[Dict[str, Any]]], argv: List[str], environment: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Use regular expressions to extract values from a field and store in extracted_fields.

    Args:
        request (HttpRequest): The HTTP request object.
        events (Union[QuerySet, List[Dict[str, Any]]]): The result set to operate on.
        argv (List[str]): List of command-line arguments.
        environment (Dict[str, Any]): Dictionary used as a jinja2 environment (context) for rendering the arguments of a command.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries with extracted values.
    """
    log = logging.getLogger(__name__)
    log.info("In search_command rex")
    events = resolve(events)
    args = rex.parser.parse_args(argv[1:])
    log.debug(f"Found args: {args}")
    expressions = [re.compile(expression) for expression in args.expressions]
    log.debug(f"Found expressions: {expressions}")
    for event in events:
        log.debug(f"Found event: {event}")
        for expression in expressions:
            try:
                results = expression.search(event[args.field])
            except:
                results = expression.search(event[args.field].decode())
            log.debug(f"Found results: {results}")
            if results:
                event.update(results.groupdict())
        yield event
