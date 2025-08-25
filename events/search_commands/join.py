# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import argparse
from datetime import timedelta
import logging
from typing import Any, Dict, List, Union

from django.db.models import Q
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.utils import timezone
from django.utils.module_loading import import_string
from django.contrib.auth.models import Permission

from events.util import resolve
from .decorators import search_command
from .util import (
    cast,
    has_permission_for_model,
)

parser = argparse.ArgumentParser(
    prog="join",
    description="Join the current result set to the results of this command",
)
group = parser.add_mutually_exclusive_group(required=False)
group.add_argument(
    "--last-15-minutes",
    action="store_true",
)
group.add_argument(
    "--last-hour",
    action="store_true",
)
group.add_argument(
    "--last-day",
    action="store_true",
)
group.add_argument(
    "--last-week",
    action="store_true",
)
group.add_argument(
    "--last-month",
    action="store_true",
)
parser.add_argument(
    "--order-by",
    action="append",
    help="If provided, it should be the name of a field. "
         "Events will be ordered by that field. Can be "
         "specified multiple times and the ordering will "
         "be applied in order.",
)
parser.add_argument(
    "-t", "--type",
    choices=(
        "left",
        "right",
        "full",
        "inner",
    ),
    default="left",
    help="Specify the type of join to perform. (Default: left)",
)
parser.add_argument(
    "-f", "--fields",
    help="Specify the fields to join on. "
         "Specify in the format of LEFT_FIELD,RIGHT_FIELD",
)
parser.add_argument(
    "--model",
    default="events.models.Event",
    help="The import_string formatted model to query."
)
parser.add_argument(
    "terms",
    nargs="*",
    help="Provide one or more search terms, "
         "must be in the form KEY=VALUE where key "
         "is a reference to a field and VALUE is the value. "
         "For KEY, django field lookups are supported.",
)

@search_command(parser)
def join(request: HttpRequest, events: Union[QuerySet, List[Dict[str, Any]]], argv: List[str], environment: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Join the current result set to the results of this command.

    Args:
        request (HttpRequest): The HTTP request object.
        events (Union[QuerySet, List[Dict[str, Any]]]): The result set to operate on.
        argv (List[str]): List of command-line arguments.
        environment (Dict[str, Any]): Dictionary used as a jinja2 environment (context) for rendering the arguments of a command.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries with joined events.
    """
    log = logging.getLogger(__name__)
    events = resolve(events)
    log.info(f"Received argv: {argv}")
    if "join" in argv:
        argv.pop(argv.index("join"))
    args = join.parser.parse_args(argv)

    if not events:
        raise ValueError(f"No events found to join.")

    log.info(f"Parsed args: {args}")

    search_filters = []
    search_excludes = []
    if args.terms:
        for kv_pair in args.terms:
            log.info(f"Received kv_pair: {kv_pair}")
            key, value = kv_pair.split("=", 1)
            value = cast(value)
            if key.startswith("!"):
                key = key.lstrip("!")
                search_excludes.append(Q(**{key: value}))
            else:
                search_filters.append(Q(**{key: value}))
    model = import_string(args.model)

    if not has_permission_for_model('view', model, request):
        raise PermissionError("Permission denied")

    ret = model.objects
    for search_filter in search_filters:
        ret = ret.filter(search_filter)
    for search_exclude in search_excludes:
        ret = ret.exclude(search_exclude)

    if args.last_15_minutes:
        ret = ret.filter(
            created__gte=timezone.now() - timedelta(minutes=15)
        )
    elif args.last_hour:
        ret = ret.filter(
            created__gte=timezone.now() - timedelta(hours=1)
        )
    elif args.last_day:
        ret = ret.filter(
            created__gte=timezone.now() - timedelta(days=1)
        )
    elif args.last_week:
        ret = ret.filter(
            created__gte=timezone.now() - timedelta(weeks=1)
        )
    elif args.last_month:
        ret = ret.filter(
            created__gte=timezone.now() - timedelta(days=30)
        )

    if args.order_by:
        order_by = [i.strip() for i in args.order_by if i.strip()]
        log.critical(f"FOUND ORDER_BY: {order_by}")
        ret = ret.order_by(*order_by)

    left = events
    right = list(ret.values())
    left_field, right_field = args.fields.split(",")
    if args.type == "left":
        for left_row in left:
            match = False
            for right_row in right:
                if left_row.get(left_field, False) == right_row.get(right_field, "False"):
                    new_row = left_row.copy()
                    new_row.update(
                        {k: v for k, v in right_row.items() if k != right_field}
                    )
                    yield new_row
                    match = True
            if not match:
                yield left_row
    elif args.type == "right":
        for right_row in right:
            match = False
            for left_row in left:
                if right_row.get(right_field, False) == left_row.get(left_field, "False"):
                    new_row = right_row.copy()
                    new_row.update(
                        {k: v for k, v in left_row.items() if k != left_field}
                    )
                    yield new_row
                    match = True
            if not match:
                yield right_row
    elif args.type == "full":
        raise NotImplementedError(f"Sorry {args.type} currently not supported")
    elif args.type == "inner":
        raise NotImplementedError(f"Sorry {args.type} currently not supported")
