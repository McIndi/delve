# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import argparse

from .decorators import search_command
from events.validators import ListOfDicts

parser = argparse.ArgumentParser(
    prog="fake_data",
    description="Return generated data of the specified type"
)
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument(
    "--dict",
    action="store_true",
    help="If specified, a simple dictionary will be returned",
)
group.add_argument(
    "--list",
    action="store_true",
    help="If specified, a simple list of values will be returned",
)
group.add_argument(
    "--empty-list",
    action="store_true",
    help="If specified, an empty list will be returned",
)
group.add_argument(
    "--list-of-dicts",
    action="store_true",
    help="If specified, a list of simple dictionaries will be returned",
)
group.add_argument(
    "--string",
    action="store_true",
    help="If specified, a simple string will be returned",
)
group.add_argument(
    "--integer",
    action="store_true",
    help="If specified, a simple integer will be returned",
)
group.add_argument(
    "--float",
    action="store_true",
    help="If specified, a simple float will be returned",
)
group.add_argument(
    "--boolean",
    action="store_true",
    help="If specified, a boolean value will be returned",
)

@search_command(parser, input_validators=[ListOfDicts])
def fake_data(request, events, argv, environment):
    if "fake_data" in argv:
        argv.pop(argv.index("fake_data"))
    args = fake_data.parser.parse_args(argv)
    if args.dict:
        return {
            "foo": 1,
            "bar": "baz"
        }
    elif args.empty_list:
        return []
    elif args.list:
        return ["foo", "bar", "baz"]
    elif args.list_of_dicts:
        return [
            {
                "foo": 1,
                "bar": "foo",
            },
            {
                "foo": 2,
                "bar": "bar",
            },
            {
                "foo": 3,
                "bar": "foobar",
            },
        ]
    elif args.string:
        return "The quick brown fox jumped over the lazy dog."
    elif args.integer:
        return 123
    elif args.float:
        return 123.456
    elif args.boolean:
        return False
    
