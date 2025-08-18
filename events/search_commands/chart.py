# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import logging
import argparse
from itertools import groupby
from typing import Any, Dict, List, Union

from django.db.models.query import QuerySet
from django.http import HttpRequest

from events.validators import ListOfDicts
from events.util import resolve
from .decorators import search_command

parser = argparse.ArgumentParser(
    prog="chart",
    description="Return the JSON data to configure a Chart.js chart.",
)
parser.add_argument(
    "-t",
    "--type",
    default="bar",
    choices=("bar", "line"),
    help="The type of chart to make",
)
parser.add_argument(
    "-x",
    "--x-field",
    help="The field to plot on the X axis"
)
parser.add_argument(
    "-y",
    "--y-field",
    help="The field to plot on the Y axis"
)
parser.add_argument(
    "-b",
    "--by-field",
    help="The field to split into series",
)
parser.add_argument(
    "--time-x",
    choices=("minute", "hour", "day", "week", "month", "quarter", "year"),
    help="If specified, the data of the x axis will be treated as time"
)

@search_command(
    parser,
    input_validators=[ListOfDicts],
)
def chart(request: HttpRequest, events: Union[QuerySet, List[Dict[str, Any]]], argv: List[str], environment: Dict[str, Any]) -> Dict[str, Any]:
    """
    Return the JSON data to configure a Chart.js chart.

    Args:
        request (HttpRequest): The HTTP request object.
        events (Union[QuerySet, List[Dict[str, Any]]]): The result set to operate on.
        argv (List[str]): List of command-line arguments.
        environment (Dict[str, Any]): Dictionary used as a jinja2 environment (context) for rendering the arguments of a command.

    Returns:
        Dict[str, Any]: A dictionary representing the chart data in Chart.js format.
    """
    log = logging.getLogger(__name__)
    log.info("In search_command chart")
    args = chart.parser.parse_args(argv[1:])
    events = resolve(events)

    if args.by_field is not None:
        log.debug(f"Found by_field: {args.by_field}")
        datasets = []
        log.debug(f"sorting events by by_field")
        events.sort(key=lambda x: x[args.by_field])
        log.debug(f"Grouping by: {args.by_field}")
        for label, data_list in groupby(events, lambda x: x[args.by_field]):
            log.debug(f"Appending data for {label}")
            datasets.append(
                {
                    "label": label,
                    "data": [
                        {
                            args.x_field: data.get(args.x_field),
                            args.y_field: data.get(args.y_field),
                        } for data in data_list
                    ],
                }
            )
        log.debug("Done grouping data")
        data = {"datasets": datasets}
    else:
        log.debug("args.by_field is None")
        data = {
            "labels": [event[args.x_field] for event in events],
            "datasets": [
                {
                    "label": args.y_field,
                    "data": events,
                }
            ]
        }
    log.debug(f"Building response")
    ret = {
        "visualization": "chartjs",
        "type": args.type,
        "data": data,
        "options": {
            "plugins": {
                # "colors": {
                #     "forceOverride": True
                # }
           },
            "parsing": {
                "xAxisKey": args.x_field,
                "yAxisKey": args.y_field,
            },
        },
    }
    if args.time_x:
        log.debug(f"Found time_x: {args.time_x}")
        ret["options"]["scales"] = {
            "x": {
                "type": "time",
                "time": {
                    "unit": args.time_x,
                    "displayFormats": {
                        "minute": "MM-DD HH:mm:SS",
                        "hour":  "MM-DD HH",
                        "day": "YY-MM-DD",
                        "week": "YY-MM-DD",
                        "month": "YY-MM",
                        "quarter": "YY-MM",
                        "year": "yyyy",
                    },
                },
                "ticks": {
                    "source": "data"
                },
            },
        }
    return ret
