# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import argparse
import logging
import json 

from django.conf import settings
from django.utils.module_loading import import_string
from django.utils.text import Truncator

from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response

from .serializers import (
    EventSerializer,
    QuerySerializer,
    GlobalContextSerializer,
    LocalContextSerializer,
    FileUploadSerializer,
)

from .models import (
    Event,
    Query,
    GlobalContext,
    LocalContext,
    FileUpload,
)
from .util import resolve

log = logging.getLogger(__name__)

class FileUploadViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for uploading files for use as data sources.
    """
    queryset = FileUpload.objects.all()
    serializer_class = FileUploadSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

class GlobalContextViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing queries.
    """
    queryset = GlobalContext.objects.all()
    serializer_class = GlobalContextSerializer

    update_data_pk_field = 'user'

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        create = True
        try:
            instance = self.queryset.filter(user=request.user).get()
            create = False
        except LocalContext.DoesNotExist:
            create = True

        if create:
            return super().create(request, *args, **kwargs)
        else:
            kwarg_field: str = self.lookup_url_kwarg or self.lookup_field
            self.kwargs[kwarg_field] = getattr(instance, kwarg_field)
            return self.update(request, *args, **kwargs)


class LocalContextViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing queries.
    """
    queryset = LocalContext.objects.all()
    serializer_class = LocalContextSerializer

    update_data_pk_field = 'id'

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        create = True
        try:
            instance = self.queryset.filter(name=request.data.get("name")).get()
            create = False
        except LocalContext.DoesNotExist:
            create = True

        if create:
            return super().create(request, *args, **kwargs)
        else:
            kwarg_field: str = self.lookup_url_kwarg or self.lookup_field
            self.kwargs[kwarg_field] = getattr(instance, kwarg_field)
            return self.update(request, *args, **kwargs)


class SearchCommandViewSet(viewsets.ViewSet):
    basename = "search_commands"

    def list(self, request):
        log = logging.getLogger(__name__)
        search_commands = settings.DELVE_SEARCH_COMMANDS
        log.debug(f"Found {len(search_commands)} search_commands")
        ret = []
        for name, path in search_commands.items():
            log.debug(f"Found name: {name}, path: {path}")
            func = import_string(path)
            log.debug(f"Found func: {func}")
            try:
                parser = getattr(func, "parser")
                log.debug(f"Found parser")
            except:
                log.exception(f"An unhandled exception occurred. returning blank search command")
                ret.append(
                    {
                        "name": name,
                        "prog": None,
                        "usage": None,
                        "description": None,
                        "help": None,
                    }
                )
                continue
            if parser._subparsers is not None:
                log.debug(f"Found subparsers")
                ret.append(
                    {
                        "name": name,
                        "prog": parser.prog,
                        "usage": parser.format_usage(),
                        "description": parser.description,
                        "help": parser.format_help(),
                    }
                )
                for action in parser._subparsers._actions:
                    log.debug(f"Found subparser action: {action}")
                    if  isinstance(action, argparse._SubParsersAction):
                        for _name, subparser in action.choices.items():
                            log.debug(f"Found subparser action: {_name}")
                            ret.append(
                                {
                                    "name": f"{name} {_name}",
                                    "prog": subparser.prog,
                                    "usage": subparser.format_usage(),
                                    "description": subparser.description,
                                    "help": subparser.format_help(),
                                }
                            )
                continue
                
            ret.append(
                {
                    "name": name,
                    "prog": parser.prog,
                    "usage": parser.format_usage(),
                    "description": parser.description,
                    "help": parser.format_help(),
                }
            )
        return Response(ret)


class EventViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing events.
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_queryset(self):
        # return self.queryset.filter(user=self.request.user)
        return self.queryset
    
    def get_serializer(self, *args, **kwargs):
        data = kwargs.get('data', None)
        if data and isinstance(data, list):
            log.debug(f"Found data: {data}")
            kwargs['many'] = isinstance(data, list)
            log.debug(f"Found kwargs['many']: {kwargs['many']}")
        if "context" in kwargs:
            kwargs["context"].update({"request": self.request})
        else:
            kwargs["context"] = {"request": self.request}
        serializer = EventSerializer(*args, **kwargs)
        log.debug(f"Found serializer: {serializer}")
        return serializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(status=status.HTTP_201_CREATED, headers=headers)
        
class QueryView(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing queries.
    """
    queryset = Query.objects.all()
    serializer_class = QuerySerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

class ResolveQueryView(APIView):
    queryset = Query.objects.all()

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def post(self, request, format=None):
        log = logging.getLogger(__name__)
        log.debug(f"Received {request=}, {format=}")
        name = request.data.get("name")
        user = request.user
        log.debug(f"Found {name=}, {user=}")
        if Query.objects.filter(name=name, user=user).exists():
            log.debug(f"Found existing query with {name=}, {user=}")
            instance=Query.objects.get(name=name, user=user)
            log.debug(f"Found {instance=}")
            query_serialized = QuerySerializer(
                data=request.data,
                context={"request": request},
                instance=instance,
            )
            log.debug(f"Built {query_serialized}")
        else:
            log.debug(f"No existing query with {name=}, {user=}")
            query_serialized = QuerySerializer(
                data=request.data,
                context={"request": request},
            )
            log.debug(f"Built {query_serialized}")

        log.debug(f"Found query_serialized: {query_serialized}")

        if "local_context" in request.data:
            log.debug(f"Found local_context")
            local_context = request.data.pop("local_context")
            log.debug(f"Found {local_context=}")
            local_context = json.loads(local_context)
            log.debug(f"Parsed json {local_context=}")
        else:
            log.debug(f"No local_context")
            local_context = {}

        if query_serialized.is_valid():
            log.debug(f"Found data: {query_serialized.validated_data}")
            # Overwriting name with the validated data
            name = query_serialized.validated_data.get("name")
            log.debug(f"validated name: {name}")
            try:
                query = Query.objects.get(name=name, user=user)
                log.debug(f"Found {query=}")
                for key, value in query_serialized.validated_data.items():
                    log.debug(f"Setting {key=} to {value=} on {query=}")
                    setattr(query, key, value)
            except Query.DoesNotExist:
                log.debug(f"No query found for {name=}, {user=}")
                query = Query(**query_serialized.validated_data)
                log.debug(f"Found {query=}")
            _save = query_serialized.validated_data.get("_save")
            log.debug(f"Found {_save=}")
            if _save:
                log.debug(f"Saving query")
                query.save()
                log.debug(f"Save completed")

            try:
                events = query.resolve(request, context=local_context)
            except Exception as exception:
                str_exception = str(exception)
                if len(str_exception) > 4096:
                    str_exception = Truncator(str_exception).chars(2048)
                return Response(
                    [
                        {
                            # "__traceback__": traceback.format_exc(),
                            "exception": str_exception,
                            # "exception": "HERE",
                        }
                    ]
                )
            return Response(resolve(events))
        else:
            log.debug(f"Found query_serialized.errors: {query_serialized.errors}")
            return Response(
                query_serialized.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )
