# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import logging
import argparse
import re
from typing import Any, Dict, List, Union

from django.db.models.query import QuerySet
from django.http import HttpRequest

from events.util import resolve
from .util import cast
from .decorators import search_command

lookup_map = {
    "exact": lambda lhs, rhs: lhs == rhs,
    "iexact": lambda lhs, rhs: lhs.lower() == rhs.lower(),
    "contains": lambda lhs, rhs: rhs in lhs,
    "icontains": lambda lhs, rhs: rhs.lower() in lhs.lower(),
    "in": lambda lhs, rhs: lhs in rhs,
    "gt": lambda lhs, rhs: lhs > rhs,
    "gte": lambda lhs, rhs: lhs >= rhs,
    "lt": lambda lhs, rhs: lhs < rhs,
    "lte": lambda lhs, rhs: lhs <= rhs,
    "ne": lambda lhs, rhs: lhs != rhs,
    "eq": lambda lhs, rhs: lhs == rhs,
    "startswith": lambda lhs, rhs: lhs.startswith(rhs),
    "istartswith": lambda lhs, rhs: lhs.lower().startswith(rhs.lower()),
    "endswith": lambda lhs, rhs: lhs.endswith(rhs),
    "iendswith": lambda lhs, rhs: lhs.lower().endswith(rhs.lower),
    "isnull": lambda lhs, rhs: lhs is None if rhs is True else lhs is not None,
    "regex": lambda lhs, rhs: re.search(rhs, lhs),
    "iregex": lambda lhs, rhs: re.search(rhs, lhs, re.I),
}

def resolve_field_lookup(expression: str, item: Dict[str, Any]) -> Any:
    log = logging.getLogger(__name__)
    if "__" not in expression or not expression.endswith(tuple([i for i in lookup_map.keys()])):
        log.debug(f"Found expression: {expression}, appending lookup.")
        expression = f"{expression}__exact"
        log.debug(f"Expression modified to: {expression}")
    ret = item
    log.debug(f"Found ret: {ret}")
    for subexpr in expression.split("__")[:-1]:
        log.debug(f"ret: {ret}, subexpr: {subexpr}")
        try:
            ret = ret[subexpr]
        except KeyError:
            ret = None
            continue
        log.debug(f"Built ret: {ret}")
    return expression.split("__")[-1], ret

parser = argparse.ArgumentParser(
    prog="filter",
    description="Reduce the result set by removing events that don't meet the specified criteria.",
)
parser.add_argument(
    "terms",
    nargs="*",
    help="Provide one or more search terms, must be in the form KEY=VALUE where key is a reference to a field and VALUE is the value. For KEY, django field lookups are (kind of) supported.",
)
parser.add_argument(
    "--no-cast",
    action="store_true",
    help="If specified, the value will not be cast to a type before completing the test",
)

@search_command(parser)
def filter(request: HttpRequest, events: Union[QuerySet, List[Dict[str, Any]]], argv: List[str], environment: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Reduce the result set by removing events that don't meet the specified criteria.

    Args:
        request (HttpRequest): The HTTP request object.
        events (Union[QuerySet, List[Dict[str, Any]]]): The result set to operate on.
        argv (List[str]): List of command-line arguments.
        environment (Dict[str, Any]): Dictionary used as a jinja2 environment (context) for rendering the arguments of a command.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries with events that meet the specified criteria.
    """
    log = logging.getLogger(__name__)
    log.debug(f"Received {events} events")
    events = resolve(events)
    log.debug(f"Resolved events: {events}")
    log.debug(f"Received argv: {argv}")
    if "filter" in argv:
        argv.pop(argv.index("filter"))
    args = filter.parser.parse_args(argv)
    log.debug(f"Found args: {args}")

    for event in events:
        log.debug(f"Found event: {event}")
        allowed = True
        for term in args.terms:
            log.debug(f"Found term: {term}")
            expression, rhs = term.split("=")
            if expression.startswith("!"):
                negate = True
                expression = expression.lstrip("!")
            else:
                negate = False
            log.debug(f"Found expression: {expression}, rhs: {rhs}")
            predicate, lhs = resolve_field_lookup(expression=expression, item=event)
            log.debug(f"Found predicate: {predicate}, lhs: {lhs}")
            if predicate not in lookup_map:
                raise ValueError(f"Sorry, {predicate} is not a valid lookup, please choose one of {lookup_map.keys()}")
            predicate = lookup_map[predicate]
            log.debug(f"predicate resolved: {predicate}")

            if not args.no_cast:
                rhs = cast(rhs)
                log.debug(f"Cast rhs: {rhs} to {type(rhs)}")
            if negate:
                if predicate(lhs, rhs):
                    log.debug(f"negated {predicate}({lhs}, {rhs}) returned: {predicate(lhs, rhs)}")
                    allowed = False
                    break
            else:
                if not predicate(lhs, rhs):
                    log.debug(f"{predicate}({lhs}, {rhs}) returned: {predicate(lhs, rhs)}")
                    allowed = False
                    break
        if allowed:
            yield event
