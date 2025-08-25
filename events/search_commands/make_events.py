# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import json
import argparse
import logging
from typing import Any, Dict, List, Union

from django.db.models.query import QuerySet
from django.http import HttpRequest

from events.models import Event
from events.serializers import EventSerializer
from events.util import resolve
from .decorators import search_command
from .util import has_permission_for_model

parser = argparse.ArgumentParser(
    prog="make_events",
    description="Generate events based on the current result set.",
)
parser.add_argument(
    "-i", "--index",
    default="default",
    help="The index to assign to the new events, you can use dollarsign notation to assign the value of a field.",
)
parser.add_argument(
    "-o", "--host",
    default="127.0.0.1",
    help="The host to assign to the new events, you can use dollarsign notation to assign the value of a field. (ie. $management_hostname)",
)
parser.add_argument(
    "-s", "--source",
    default="events",
    help="The source to assign to the new events, you can use dollarsign notation to assign the value of a field. (ie. $management_hostname)",
)
parser.add_argument(
    "-t", "--sourcetype",
    default="json",
    help="The sourcetype to assign to the new events, you can use dollarsign notation to assign the value of a field. (ie. $content_type)",
)
parser.add_argument(
    "-S", "--save",
    action="store_true",
    help="If specified, the events will be saved."
)
parser.add_argument(
    "-d", "--drop",
    action="append",
    help="If specified, provide the name of a field to drop before creating the events."
)

@search_command(parser)
def make_events(request: HttpRequest, events: Union[QuerySet, List[Dict[str, Any]]], argv: List[str], environment: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate events based on the current result set.

    Args:
        request (HttpRequest): The HTTP request object.
        events (Union[QuerySet, List[Dict[str, Any]]]): The result set to operate on.
        argv (List[str]): List of command-line arguments.
        environment (Dict[str, Any]): Dictionary used as a jinja2 environment (context) for rendering the arguments of a command.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries representing the generated events.
    """
    if not has_permission_for_model('add', Event, request):
        raise PermissionError(f"Permission Denied")

    args = make_events.parser.parse_args(argv[1:])
    log = logging.getLogger(__name__)
    index = args.index
    host = args.host
    source = args.source
    sourcetype = args.sourcetype
    events = resolve(events)
    for orig_event in events:
        event = {
            "host": host if "$" not in host else orig_event.get(host.replace("$", "")),
            "source": source if "$" not in source else orig_event.get(source.replace("$", "")),
            "sourcetype": sourcetype if "$" not in sourcetype else orig_event.get(sourcetype.replace("$", "")),
            "index": index if "$" not in index else orig_event.get(index.replace("$", "")),
            "user": request.user,
        }
        if args.drop:
            update_dict = {k: v for k, v in orig_event.items() if k not in args.drop}
        else:
            update_dict = dict(orig_event.items())
        event.update(
            {
                "text": json.dumps(update_dict),
                "extracted_fields": update_dict,
            },
        )
        event = Event(**event)
        if args.save:
            event.save()
        serializer = EventSerializer(event)
        yield serializer.data
