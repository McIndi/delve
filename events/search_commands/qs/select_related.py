# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import logging
import argparse
from typing import Any, Dict, List

from django.db import models
from django.db.models.query import QuerySet
from django.http import HttpRequest

from events.search_commands.decorators import search_command
from events.search_commands.util import has_permission_for_model

select_related_parser = argparse.ArgumentParser(
    prog="select_related",
    description="Perform a SQL join and include the fields of the related object in the QuerySet",
) 
select_related_parser.add_argument(
    "related_fields",
    nargs="*",
    help="The related fields to include in the QuerySet",
)

@search_command(select_related_parser)
def select_related(request: HttpRequest, events: QuerySet, argv: List[str], environment: Dict[str, Any]) -> QuerySet:
    """
    Perform a SQL join and include the fields of the related object in the QuerySet.

    Args:
        request (HttpRequest): The HTTP request object.
        events (QuerySet): The QuerySet to operate on.
        argv (List[str]): List of command-line arguments.
        environment (Dict[str, Any]): Dictionary used as a jinja2 environment (context) for rendering the arguments of a command.

    Returns:
        QuerySet: A QuerySet with the related fields included.
    """
    log = logging.getLogger(__name__)
    log.info("In select_related")
    args = select_related_parser.parse_args(argv[1:])

    if not isinstance(events, QuerySet):
        log.critical(f"Type QuerySet expected, received {type(events)}")
        raise ValueError(
            f"select_related can only operate on QuerySets like "
            "the output of the search command"
        )
    event_model = events.query.model
    log.debug(f"{event_model=}")
    
    # Get forward relations (ForeignKey fields)
    forward_relations = [
        f for f in event_model._meta.fields 
        if isinstance(f, models.ForeignKey)
    ]
    
    # Get reverse relations
    reverse_relations = event_model._meta.related_objects
    
    # Combine both types of relations
    related_fields = {}
    for relation in forward_relations:
        related_fields[relation.name] = relation.related_model
    for relation in reverse_relations:
        related_fields[relation.name] = relation.related_model
        
    log.debug(f"Related fields: {related_fields}")
    
    for related_field in args.related_fields:
        log.debug(f"\t{related_field=}")
        base_field = related_field.split('__')[0]  # Handle nested relationships like 'user__username'
        if base_field not in related_fields:
            log.debug(f"\t{base_field=} not in {event_model.__name__}")
            raise ValueError(f"Related field {base_field} not found in {event_model.__name__}")
        else:
            log.debug(f"\t{base_field=} found in {event_model.__name__}")
            model = related_fields[base_field]
            log.debug(f"\t{model=}")
            if not has_permission_for_model('view', model, request):
                log.debug(f"\t{model=} does not have view permission")
                raise PermissionError("Permission denied")

    log.debug(f"Received {args=}")
    return events.select_related(*args.related_fields)
