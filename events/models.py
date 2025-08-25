# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import re
import sys
import shlex
import logging
from uuid import uuid4
from uuid import UUID as UUID
from io import StringIO

from django.db import models
from django.conf import settings
from django.db.models.query import QuerySet
from django.db.models.manager import Manager
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.module_loading import import_string

from jinja2 import Environment
from uuid_utils import uuid7

from .validators import JsonObjectValidator
from events.util import resolve


class FileUpload(models.Model):
    id = models.UUIDField(
        default=uuid4,
        primary_key=True,
        editable=False,
    )
    created = models.DateTimeField(
        auto_now_add=True,
    )
    modified = models.DateTimeField(
        auto_now=True,
    )
    title = models.CharField(
        max_length=1024,
        unique=True,
    )
    content = models.FileField(
        upload_to="uploads/",
    )

    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="file_uploads",
    )


class GlobalContext(models.Model):
    id = models.UUIDField(
        default=uuid4,
        primary_key=True,
        editable=False,
    )
    created = models.DateTimeField(
        auto_now_add=True,
    )
    modified = models.DateTimeField(
        auto_now=True,
    )

    context = models.JSONField(
        default=dict,
        blank=True,
        null=True,
    )
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="global_context",
        blank=True,
        null=True,
    )

    def clean(self):
        super().clean()
    
        if not isinstance(self.context, dict):
            raise ValidationError('Context must be a mapping (dict, object)')

class LocalContext(models.Model):
    id = models.UUIDField(
        default=uuid4,
        primary_key=True,
        editable=False,
    )
    created = models.DateTimeField(
        auto_now_add=True,
    )
    modified = models.DateTimeField(
        auto_now=True,
    )

    name = models.CharField(
        max_length=1024,
    )
    context = models.JSONField(
        default=dict,
        blank=True,
        null=True,
    )
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="local_contexts",
    )

    def clean(self):
        super().clean()
    
        if not isinstance(self.context, dict):
            raise ValidationError('Context must be a mapping (dict, object)')

class Query(models.Model):
    id = models.UUIDField(
        default=uuid4,
        primary_key=True,
        editable=False,
    )
    created = models.DateTimeField(
        auto_now_add=True,
    )
    modified = models.DateTimeField(
        auto_now=True,
    )

    name = models.CharField(
        max_length=1024,
        blank=True,
        null=True,
    )
    text = models.TextField()
    _save = models.BooleanField(
        default=False,
    )

    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="queries",
        null=True,
        blank=True,
    )

    def get_search_commands(self):
        log = logging.getLogger(__name__)
        log.debug(f"Found self.text: {self.text}")
        search_commands = re.split(r'(?<!\|)\|(?!\|)', self.text)
        search_commands = [search_command.replace('||', '|') for search_command in search_commands]
        log.debug(f"Found search_commands: {search_commands}")
        ret = []
        for search_command in search_commands:
            log.debug(f"Found search_command: {search_command}")
            argv = shlex.split(search_command, comments=True)
            log.debug(f"Found argv: {argv}")
            funcname = argv[0]
            log.debug(f"Found funcname: {funcname}")
            if funcname not in settings.DELVE_SEARCH_COMMANDS:
                raise ValueError(f"{funcname} is not a recognized search command.")
            funcpath = settings.DELVE_SEARCH_COMMANDS[funcname]
            log.debug(f"Found funcpath: {funcpath}")
            func = import_string(funcpath)
            log.debug(f"Found func: {func}")
            ret.append((search_command, func))
        return ret
    
    def resolve(self, request, context=None, events=None):
        log = logging.getLogger(__name__)
        # I need this so the import for events.models.Event happens after initialization
        search_commands = self.get_search_commands()
        log.debug(f"Found search_commands: {search_commands}")
        if events is not None:
            matching_events = events
        else:
            matching_events = []
        log.debug(f"Provisioning jinja2 context")
        environment = Environment()
        environment.trim_blocks = True
        environment.lstrip_blocks = True
        environment.strip_trailing_newlines = True
        try:
            environment_globals = request.user.global_context.context
        except AttributeError:
            environment_globals = {}
        log.debug(f"Building context: {context}")
        if context is None:
            log.debug(f"Found context to be None, provisioning empty context")
            context = {}
        elif isinstance(context, str):
            log.debug(f"Found context to be str, retrieving")
            context = LocalContext.objects.get(name=context, user=request.user)
            context = context.context
            log.debug(f"Found context: {context}")
        elif isinstance(context, dict):
            log.debug(f"Found context to be dict, using as-is.")
        else:
            raise ValueError(f"Unsupported type for context")

        # We have to patch sys.stdout and sys.stderr, to 
        # catch any output from exceptions
        for search_command, operation in search_commands:
            log.debug(f"Found search_command: {search_command}")
            search_command = environment.from_string(search_command, globals=environment_globals).render(context)
            log.debug(f"Rendered search_command: {search_command}")
            argv = shlex.split(search_command, comments=True)
            log.debug("swapping stdout and stderr")
            orig_stderr = sys.stderr
            orig_stdout = sys.stdout
            sys.stderr = StringIO()
            sys.stdout = StringIO()
            log.debug(f"Checking for search_command validators")
            if settings.DELVE_STRICT_VALIDATION:
                if operation.input_validators is not None:
                    log.debug(f"Found Input validators: {operation.input_validators}")
                    for validator in operation.input_validators:
                        log.debug(f"Verifying validator {validator} against events.")
                        validator(events=matching_events)
                        log.debug(f"Successfully validated against: {validator}")
                    log.debug(f"Successfully tested all validators for {operation}")
            try:
                log.debug(f"Attempting to apply operation: {operation}")
                matching_events = operation(request, matching_events, argv, context)
                log.debug(f"Successfully called operation: {operation}")
            except (Exception, SystemExit) as exception:
                logging.exception("An unhandled exception occurred.")
                try:
                    sys.stderr.seek(0)
                    sys.stdout.seek(0)
                except:
                    log.exception("An Unhandled exception occurred.")
                return [
                    {
                        "stdout": sys.stdout.read(),
                        "stderr": sys.stderr.read(),
                        "exception": str(exception),
                        "matching_events": events,
                    },
                ]
            finally:
                log.debug("replacing original stdout and stderr")
                sys.stderr = orig_stderr
                sys.stdout = orig_stdout
        # Resolve any QuerySets, generators, etc.
        log.debug(f"Attempting to resolve QuerySets, generators, etc.")
        matching_events = resolve(matching_events)
        log.debug(f"Finished resolution")
        return matching_events

def generate_uuid7():
    """Generate a UUID v7 that's compatible with Django's UUIDField"""
    return UUID(str(uuid7()))

class BaseEvent(models.Model):
    id = models.UUIDField(
        default=generate_uuid7,
        primary_key=True,
        editable=False,
    )
    # id = models.BigAutoField(
    #     primary_key=True,
    # )
    created = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )
    # modified = models.DateTimeField(
    #     auto_now=True,
    # ) 

    index = models.CharField(
        default="default",
        max_length=255,
        db_index=True,
    )
    source = models.CharField(
        default="default",
        max_length=255,
        db_index=True,
    )
    sourcetype = models.CharField(
        default="text",
        max_length=255,
    )
    host = models.CharField(
        default="127.0.0.1",
        max_length=255,
        db_index=True,
    )

    text = models.TextField()
    extracted_fields = models.JSONField(
        blank=True,
        null=True,
        default=dict,
    )

    class Meta:
        abstract = True
        # fields = (
        #     "created",
        #     "index",
        #     "source",
        #     "sourcetype",
        #     "host",
        #     "text",
        #     "extracted_fields",
        # )
    
    def extract_fields(self):
        log = logging.getLogger(__name__)
        log.debug("Inside extract_fields")
        extraction_map = settings.DELVE_EXTRACTION_MAP
        log.debug(f"Found {extraction_map=}")
        ret = {}
        for sourcetype, extractions in extraction_map.items():
            log.debug(f"Found {sourcetype=}, {extractions=}")
            if sourcetype == self.sourcetype:
                log.debug(f"Found {sourcetype=} matches {self.sourcetype=}")
                if not isinstance(extractions, (tuple, list)):
                    extractions = [extractions]
                for extraction in extractions:
                    log.debug(f"Performing {extraction=}")
                    if isinstance(extraction, str):
                        log.debug(f"Importing {extraction=}")
                        update_value = import_string(extraction)(self.text)
                    else:
                        log.debug(f"Using {extraction=} as is.")
                        update_value = extraction(self.text)
                    
                    if not isinstance(update_value, dict):
                        update_value = {"value": update_value}
                    ret.update(update_value)
        self.extracted_fields.update(ret)
        return ret

    def process(self):
        log = logging.getLogger(__name__)
        log.debug("Inside process")
        processor_map = settings.DELVE_PROCESSOR_MAP
        log.debug(f"Found {processor_map=}")
        ret = []
        for sourcetype, processors in processor_map.items():
            log.debug(f"Found {sourcetype=}, {processors=}")
            if sourcetype == self.sourcetype:
                log.debug(f"Found {sourcetype=} matches {self.sourcetype=}")
                if not isinstance(processors, (tuple, list)):
                    processors = [processors]
                for processor in processors:
                    if isinstance(processor, str):
                        log.debug(f"Importing {processor}")
                        ret.append(import_string(processor)(self))
                    else:
                        ret.append(processor(self))
        return ret
            
class Event(BaseEvent):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="events",
    )
