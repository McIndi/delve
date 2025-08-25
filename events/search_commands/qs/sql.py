# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import logging
import argparse
from typing import Any, Dict, List

from django.db.models.query import QuerySet
from django.http import HttpRequest

from events.search_commands.decorators import search_command

sql_parser = argparse.ArgumentParser(
    prog="sql",
    description="Output the SQL query for the current QuerySet",
)

@search_command(sql_parser)
def sql(request: HttpRequest, events: QuerySet, argv: List[str], environment: Dict[str, Any]) -> str:
    """
    Output the SQL query for the current QuerySet.
    """
    log = logging.getLogger(__name__)
    log.info("In sql")
    if not isinstance(events, QuerySet):
        log.critical(f"Type QuerySet expected, received {type(events)}")
        raise ValueError("sql can only operate on QuerySets like the output of the search command")
    return str(events.query)
