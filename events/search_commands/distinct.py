# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import argparse
import logging
from collections import defaultdict
from typing import Any, Dict, List, Union

from django.db.models.query import QuerySet
from django.http import HttpRequest

from events.util import resolve

from .decorators import search_command

parser = argparse.ArgumentParser(
    prog="distinct",
    description="Return one event with fields containing the unique values of the specified fields.",
)
parser.add_argument(
    nargs="+",
    dest="fields",
    help="The fields to use for distinct records",
)

@search_command(parser)
def distinct(request: HttpRequest, events: Union[QuerySet, List[Dict[str, Any]]], argv: List[str], environment: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Return one event with fields containing the unique values of the specified fields.

    Args:
        request (HttpRequest): The HTTP request object.
        events (Union[QuerySet, List[Dict[str, Any]]]): The result set to operate on.
        argv (List[str]): List of command-line arguments.
        environment (Dict[str, Any]): Dictionary used as a jinja2 environment (context) for rendering the arguments of a command.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries with distinct records.
    """
    events = resolve(events)
    args = distinct.parser.parse_args(argv[1:])
    logging.debug(f"Found args: {args}")
    ret_dict = defaultdict(set)
    for event in events:
        for field in args.fields:
            item = event
            for segment in field.split("__"):
                try:
                    item = item[segment]
                except KeyError:
                    item = None
            if item is not None:
                ret_dict[field].add(item)
    return [{
        key: list(value)
        for key, value in ret_dict.items()
    }]
