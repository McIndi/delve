# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import logging 
from itertools import groupby
from operator import itemgetter
from types import GeneratorType
import inspect
from itertools import chain
import sys
from io import StringIO

from django.db.models.query import QuerySet

from events.util import resolve

def add_count_parser_arguments(count_parser):
    count_parser.add_argument(
        "field",
        nargs="?",
        help="The fields to count, if no field is specified, "
             "the count of events will be returned.  If a field "
             "is specified, then null or missing values will not "
             "be counted",
    )
    count_parser.add_argument(
        "--distinct",
        action="store_true",
        help="If specified, only distinct values will be counted, "
             "to use distinct, a field must be specified.",
    )
    count_parser.add_argument(
        "--by",
        nargs="+",
        help="If specified, the average returned will be by the specified field",
    )
    count_parser.add_argument(
        "--field-name",
        help="If specified, the average will be stored under the specified key "
             "similar to SQL AS keyword",
    )

# def resolve_to_list_of_dicts(events):
#     log = logging.getLogger(__name__)
#     if isinstance(events, QuerySet):
#         log.debug(f"Casting matching events, detected {type(events)}")
#         events = list(events.values())
#     elif isinstance(events, GeneratorType) or inspect.isgeneratorfunction(events):
#         log.debug(f"Casting matching events, detected {type(events)}({events})")
#         log.debug("swapping stdout and stderr")
#         orig_stderr = sys.stderr
#         orig_stdout = sys.stdout
#         sys.stderr = StringIO()
#         sys.stdout = StringIO()
#         try:
#             events = list(events)
#         except (Exception, SystemExit) as exception:
#             log.exception(f"Exception raised: {exception}")
#             raise
#         finally:
#             log.debug("replacing original stdout and stderr")
#             sys.stderr = orig_stderr
#             sys.stdout = orig_stdout

#     if isinstance(events, list):
#         # keys is a set of all keys from all events in events
#         log.debug(f"Found events: {events}")
#         # Peek at the data type of the first item
#         if events and isinstance(events[0], dict):
#             keys = set(chain.from_iterable(events))
#             log.debug(f"Found keys: {keys}")
#             for event in events:
#                 # Add None to fill any missing values
#                 if isinstance(event, dict):
#                     log.debug(f"Adding missing keys")
#                     try:
#                         event.update({key: event.get(key, None) for key in keys})
#                     except:
#                         log.exception(f"Found item: {type(event)}({event})")
#                         raise
#     return events


def count(events, args, environment):
    log = logging.getLogger(__name__)
    events = resolve(events)

    if args.by:
        ret = []
        events.sort(key=itemgetter(*args.by))
        for key, event_group in groupby(events, key=itemgetter(*args.by)):
            event_group = list(event_group)
            if args.distinct:
                count = len(set(str(i) for i in event_group))
                for event in event_group:
                    field_name = args.field_name if args.field_name else "count"
                    ret.append(
                        {
                            "key": key,
                            field_name: count,
                            **event,
                        }
                    )
            else:
                count = len(event_group)
                for event in event_group:
                    field_name = args.field_name if args.field_name else "count"
                    ret.append(
                        {
                            "key": key,
                            field_name: count,
                            **event,
                        }
                    )
        return ret
    else:
        if args.distinct:
            return len(set(str(e) for e in events))
        else:
            return len(events)
