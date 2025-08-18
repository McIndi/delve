# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import argparse
import logging
from typing import Any, Dict, List, Union

from django.db.models.query import QuerySet
from django.http import HttpRequest

from events.util import resolve
from events.search_commands.decorators import search_command

parser = argparse.ArgumentParser(
    prog="dedup",
    description="Deduplicate the result set based on the optional fields. First matching item is kept. (events should be sorted prior to calling this)",
)
parser.add_argument(
    nargs="*",
    dest="fields",
    help="The fields to use for deduplication",
)

@search_command(parser)
def dedup(request: HttpRequest, events: Union[QuerySet, List[Dict[str, Any]]], argv: List[str], environment: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Deduplicate the result set based on the optional fields. First matching item is kept.

    Args:
        request (HttpRequest): The HTTP request object.
        events (Union[QuerySet, List[Dict[str, Any]]]): The result set to operate on.
        argv (List[str]): List of command-line arguments.
        environment (Dict[str, Any]): Dictionary used as a jinja2 environment (context) for rendering the arguments of a command.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries with duplicate records removed.
    """
    log = logging.getLogger(__name__)
    log.debug(f"Found events: {events}")
    args = dedup.parser.parse_args(argv[1:])
    log.debug(f"Found args: {args}")

    events = resolve(events=events)

    if not args.fields:
        log.info("No fields specified, using default comparison")
        ret = []
        last_event = None
        for event in events:
            if event == last_event:
                pass
            else:
                ret.append(event)
                last_event = event
    else:
        log.debug(f"Deduplicating by fields: {args.fields}")
        last_event = None
        ret = []
        for event in events:
            new_event = {field: event.get(field) for field in args.fields}
            if new_event == last_event:
                log.debug(f"Removing event: {new_event}, considered equal to {last_event}")
                pass
            else:
                ret.append(event)
                last_event = new_event
    return ret
