# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import logging

from django.core.management.utils import get_random_secret_key
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

class Command(BaseCommand):
    help = "Use cherrypy to serve the web app"

    def add_arguments(self, parser):
        ...        

    def handle(self, *args, **options):
        self.stdout.write(f"{get_random_secret_key()}\n")
        self.stdout.flush()
