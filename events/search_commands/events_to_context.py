# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import sys
import logging
import argparse
from typing import Any, Dict, List, Union

from django.db.models.query import QuerySet
from django.http import HttpRequest

from events.util import resolve
from .decorators import search_command

parser = argparse.ArgumentParser(
    prog="events_to_context",
    description="Put the current result set into the local context for use in jinja templating.",
)
parser.add_argument(
    "-z", "--return-empty",
    action="store_true",
    help="If specified, events received will be loaded into the local context and an empty list will be returned. By default, events received will be returned after processing."
)

@search_command(parser)
def events_to_context(request: HttpRequest, events: Union[QuerySet, List[Dict[str, Any]]], argv: List[str], environment: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Put the current result set into the local context for use in jinja templating.

    Args:
        request (HttpRequest): The HTTP request object.
        events (Union[QuerySet, List[Dict[str, Any]]]): The result set to operate on.
        argv (List[str]): List of command-line arguments.
        environment (Dict[str, Any]): Dictionary used as a jinja2 environment (context) for rendering the arguments of a command.

    Returns:
        List[Dict[str, Any]]: The original result set or an empty list if --return-empty is specified.
    """
    log = logging.getLogger(__name__)
    log.info(f"Received argv: {argv}")
    args = events_to_context.parser.parse_args(argv[1:])
    log.debug(f"Found args: {args}")
    events = resolve(events)
    environment["events"] = events
    if args.return_empty:
        return []
    return events

