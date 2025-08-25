# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import argparse
import logging
import json
import html
from typing import Any, Dict, List, Union

from django.db.models.query import QuerySet
from django.http import HttpRequest

from events.util import resolve, cast

from .decorators import search_command

def _pull_fields(event: Dict[str, Any], fields: List[str]) -> Dict[str, Any]:
    ret = {}
    for field in fields:
        ret[field] = event.get(field, None) 
    return ret

def encode(obj: Any) -> str:
    try:
        obj = cast(obj)
    except:
        pass

    if isinstance(obj, str):
        return json.dumps(html.escape(obj))
    try:
        return json.dumps(obj)
    except TypeError:
        return json.dumps(str(obj))

parser = argparse.ArgumentParser(
    prog="table",
    description="Return the JSON configuration to make a table using datatables",
)
parser.add_argument(
    "-f",
    "--fields",
    nargs="*",
    help="The fields to include in the table",
)

@search_command(parser)
def table(request: HttpRequest, events: Union[QuerySet, List[Dict[str, Any]]], argv: List[str], environment: Dict[str, Any]) -> Dict[str, Any]:
    """
    Return the JSON configuration to make a table using datatables.

    Args:
        request (HttpRequest): The HTTP request object.
        events (Union[QuerySet, List[Dict[str, Any]]]): The result set to operate on.
        argv (List[str]): List of command-line arguments.
        environment (Dict[str, Any]): Dictionary used as a jinja2 environment (context) for rendering the arguments of a command.

    Returns:
        Dict[str, Any]: A dictionary representing the JSON configuration for the table.
    """
    log = logging.getLogger(__name__)
    args = table.parser.parse_args(argv[1:])
    fields = args.fields
    events = resolve(events)

    if fields is not None:
        events = [
            _pull_fields(event, fields) for event in events
        ]
        columns = fields
    else:
        # resolve, up above, ensures that the keys are the same for all events
        columns = events[0].keys()
    events = [
        [encode(event.get(column, None)) for column in columns] for event in events
    ]
    columns = [{"title": column} for column in columns]
    return {
        "visualization": "table",
        "columns": columns,
        "data": events,
        "autowidth": True,
        "colReorder": True,
        "order": [],
        "columnDefs": [
            {
                "targets": "_all",
                "className": 'dt-body-left'
            }
        ],
        "layout": {
            "topEnd": None,
            "topStart": {
                "buttons": [
                    'colvis',
                    'print',
                    'copy',
                    'csv',
                    'excel',
                ]
            },
            "top": [
                'pageLength',
                'info',
                'paging',
                'search',
            ],
            "bottom": [
                'paging',
            ],
            "bottomStart": None,
            "bottomEnd": None,
        }
    }

