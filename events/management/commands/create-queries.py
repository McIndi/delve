# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

"""A CLI program to create an event in delve through the
delve REST API.
"""
import logging

from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.module_loading import import_string

from events.models import Query

class Command(BaseCommand):
    help = "Create the Queries needed for the DataPower Delve App"

    def add_arguments(self, parser):
        parser.add_argument(
            "app_name",
            type=str,
            help="The name of the app to create queries for",
        )
        parser.add_argument(
            '--overwrite',
            action='store_true',
            help='If specified, overwrite existing queries',
        )

    
    def handle(self, *args, **options):
        log = logging.getLogger(__name__)
        log.debug(f"Received {args=} {options=}")
        app_name = options.get("app_name", None)
        log.debug(f"App name: {app_name}")
        if app_name is None:
            log.error("App name is required")
            return
        if app_name not in settings.INSTALLED_APPS:
            log.error(f"App {app_name} not found in settings.INSTALLED_APPS")
            return

        try:
            queries = import_string(f"{app_name}.queries.QUERIES")
        except ImportError as e:
            log.error(f"Could not import queries module for app {app_name}: {e}")
            return
        for query in queries:
            if Query.objects.filter(name=query.name).exists():
                if options.get("overwrite"):
                    Query.objects.filter(name=query.name).delete()
                    query.save()
                    log.info(f"Overwrote query {query.name}")
                else:
                    log.info(f"Query {query.name} already exists, skipping")
                    continue
            else:
                query.save()
                log.info(f"Created query {query.name}")
        log.info("Finished creating queries")
