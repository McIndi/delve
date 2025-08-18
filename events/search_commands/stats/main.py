# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import argparse

from .avg import (
    avg,
    add_avg_parser_arguments,
)
from .count import (
    count,
    add_count_parser_arguments
)

from events.search_commands.decorators import search_command

parser = argparse.ArgumentParser(
    prog="stats",
    description="A collection of statistics related subcommands."
)
subcommands = parser.add_subparsers(dest='subparser_name')

avg_parser = subcommands.add_parser(
    "avg",
    description="Take the average of a field and store "
                "it as an additional field on each event",
)
add_avg_parser_arguments(avg_parser)

count_parser = subcommands.add_parser(
    "count",
    description="Take the count of values for a fields and store as "
         "an additional field on each event."
)
add_count_parser_arguments(count_parser)

@search_command(parser)
def stats(request, events, argv, environment):

    if "stats" in argv:
        argv.pop(argv.index("stats"))
    args = stats.parser.parse_args(argv)
    match args.subparser_name:
        case "avg":
            return avg(events, args, environment)
        case "count":
            return count(events, args, environment)
    
