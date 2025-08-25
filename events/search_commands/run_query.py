# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import re
import argparse
import logging
from typing import Any, Dict, List, Union

from django.db.models.query import QuerySet
from django.http import HttpRequest

from events.models import Query
from events.util import resolve
from .decorators import search_command

parser = argparse.ArgumentParser(
    prog="run_query",
    description="Run a named query. If any events are received, the results of "
                "the query are appended to the events received.",
)
parser.add_argument(
    "name",
    help="The name of the saved query to run",
)

@search_command(parser)
def run_query(request: HttpRequest, events: Union[QuerySet, List[Dict[str, Any]]], argv: List[str], environment: Dict[str, Any]) -> Union[QuerySet, List[Dict[str, Any]]]:
    """
    Run a named query. If any events are received, the results of the query are appended to the events received.

    Args:
        request (HttpRequest): The HTTP request object.
        events (Union[QuerySet, List[Dict[str, Any]]]): The result set to operate on.
        argv (List[str]): List of command-line arguments.
        environment (Dict[str, Any]): Dictionary used as a jinja2 environment (context) for rendering the arguments of a command.

    Returns:
        Union[QuerySet, List[Dict[str, Any]]]: A QuerySet or list of events with the results of the named query appended.
    """
    log = logging.getLogger(__name__)
    events = resolve(events)
    args = run_query.parser.parse_args(argv[1:])
    log.debug(f"Found args: {args}")
    name = args.name
    log.debug(f"found name: {name}")
    try:
        query = Query.objects.get(name=name)
    except Query.DoesNotExist:
        log.exception("Named query does not exist for specified user.")
        raise
    new_events = query.resolve(request=request, events=events, context=environment)
    if events:
        if isinstance(new_events, list):
            return events + new_events
        else:
            return events + [new_events]
    else:
        return new_events
