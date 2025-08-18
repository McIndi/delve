# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import logging
import argparse
from typing import Any, Dict, List, Union

from django.db.models.query import QuerySet
from django.http import HttpRequest

from events.util import resolve as resolve_events
from .decorators import search_command

parser = argparse.ArgumentParser(
    prog="resolve",
    description="Resolve the result set. This will unwrap any generators or QuerySets.",
)

@search_command(parser)
def resolve(request: HttpRequest, events: Union[QuerySet, List[Dict[str, Any]]], argv: List[str], environment: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Resolve the result set. This will unwrap any generators or QuerySets.

    Args:
        request (HttpRequest): The HTTP request object.
        events (Union[QuerySet, List[Dict[str, Any]]]): The result set to operate on.
        argv (List[str]): List of command-line arguments.
        environment (Dict[str, Any]): Dictionary used as a jinja2 environment (context) for rendering the arguments of a command.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries representing the resolved result set.
    """
    log = logging.getLogger(__name__)
    log.info(f"Received argv: {argv}")
    args = resolve.parser.parse_args(argv[1:])
    log.debug(f"Found args: {args}")
    events = resolve_events(events)
    return events
