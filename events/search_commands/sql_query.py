# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import logging
import argparse
import json
from typing import Any, Dict, List, Union

from django.db.models.query import QuerySet
from django.http import HttpRequest

import records

from events.util import resolve
from .decorators import search_command

parser = argparse.ArgumentParser(
    prog="sql_query",
    description="Perform a SQL query against the specified database.",
)
parser.add_argument(
    "connection_string",
    help="The database connection string, "
         "(ie. mysql+pymysql://user:pass@some_mariadb/dbname)",
)
parser.add_argument(
    "sql_query",
    help="The SQL query to issue."
)

@search_command(parser)
def sql_query(request: HttpRequest, events: Union[QuerySet, List[Dict[str, Any]]], argv: List[str], environment: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Perform a SQL query against the specified database.

    Args:
        request (HttpRequest): The HTTP request object.
        events (Union[QuerySet, List[Dict[str, Any]]]): The result set to operate on.
        argv (List[str]): List of command-line arguments.
        environment (Dict[str, Any]): Dictionary used as a jinja2 environment (context) for rendering the arguments of a command.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries representing the results of the SQL query.
    """
    log = logging.getLogger(__name__)
    events = resolve(events)
    if events:
        raise ValueError(f"sql_query must be the first command in the Query")
    log.debug(f"Parsing args")
    args = sql_query.parser.parse_args(argv[1:])
    log.debug(f"Found sql query: '{args.sql_query}'")
    log.debug("Finished parsing args, connecting to database")
    db = records.Database(args.connection_string)
    log.debug("Querying the database")
    rows = db.query(args.sql_query)
    log.debug("returning results")
    return json.loads(rows.export('json'))
