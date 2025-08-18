# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import argparse
import logging
import inspect
from types import GeneratorType
from collections import defaultdict

from django.db.models.manager import Manager
from django.db.models.query import QuerySet

from events.util import resolve

from .decorators import search_command

parser = argparse.ArgumentParser(
    prog="merge",
    description="combine multiple events based on a field",
)
parser.add_argument(
    nargs="+",
    dest="fields",
)

def get_nested_value(data, field):
    """
    Retrieve the value from a nested dictionary using double-underscore notation.

    Args:
        data: The dictionary to retrieve the value from.
        field: The field name with double-underscore notation.

    Returns:
        The value of the nested field, or None if any part of the path is missing.
    """
    log = logging.getLogger(__name__)
    item = data
    for segment in field.split("__"):
        log.debug(f"Trying segment: {segment}")
        try:
            item = item[segment]
            log.debug(f"Found segment {segment}: {item}")
        except KeyError:
            log.debug(f"Received KeyError, field {segment} not in {item}")
            return None
    return item

@search_command(parser)
def merge(request, events, argv, environment):
    log = logging.getLogger(__name__)
    args = merge.parser.parse_args(argv[1:])
    log.debug(f"Found args: {args}")
    events = resolve(events)
    log.debug(f"Found events to be list or generator function.")
    
    merged_events = defaultdict(lambda: defaultdict(list))
    
    for event in events:
        key_dict = {field: get_nested_value(event, field) for field in args.fields}
        key = tuple(key_dict.values())
        
        if key not in merged_events:
            merged_events[key].update({field: value for field, value in key_dict.items()})
        
        for field, value in event.items():
            if field not in args.fields:
                if value not in merged_events[key][field]:
                    merged_events[key][field].append(value)
    
    for merged_event in merged_events.values():
        log.debug(f"Yielding merged event: {merged_event}")
        yield merged_event