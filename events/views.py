# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import logging

from django.http import HttpResponse
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

import markdown

from .forms import (
    QueryForm,
    GlobalContextForm,
    LocalContextForm,
    FileUploadForm,
)
from .models import Event

def http_405():
    return HttpResponse(
        "<p>Method Not Allowed</p>",
        content_type="text/html",
        status=405,
    )

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@login_required()
def docs(request, manual, filename):
    log = logging.getLogger(__name__)
    log.debug(f"Requested documentation file: {filename}, from manual: {manual}")
    path = settings.DELVE_DOCUMENTATION_DIRECTORY.joinpath(manual).joinpath(filename)
    log.debug(f"Path to documentation file: {path}")
    if path.exists():
        log.debug(f"Found documentation file: {path}")
        content = path.read_text()
    else:
        log.debug(f"Documentation file not found: {path}")
        content = "Sorry, couldn't find that for you."
    # formatter = markdown.HtmlFormatter(noclasses=True)
    html = markdown.markdown(
        content,
        extensions=[
            'codehilite',
            'fenced_code',
            'tables',
        ],
    )
    return render(
        request,
        'events/markdown_template.html',
        {
            'content': html,
        },
    )

@login_required()
def edit_global_context(request):
    if request.method == "POST":
        global_context_form = GlobalContextForm(request.POST, instance=request.user.global_context)
        if global_context_form.is_valid():
            global_context_form.save()
            messages.add_message(
                request=request,
                level=messages.SUCCESS,
                message="Globals successfully updated."
            )
    elif request.method == "GET":
        global_context_form = GlobalContextForm(instance=request.user.global_context)
    else:
        return http_405()
    return render(
        request,
        "events/edit-global-context.html",
        {
            "global_context_form": global_context_form,
        }
    )

@login_required()
def explore(request):
    log = logging.getLogger(__name__)
    if request.method == "GET":
        log.debug(f"Found request.GET: {request.GET}")
        query_form = QueryForm(request.GET or None)
        current_context_form = LocalContextForm()
        file_upload_form = FileUploadForm()
    else:
        return http_405()
    return render(
        request,
        'events/explore.html',
        {
            'query_form': query_form,
            'current_context_form': current_context_form,
            'file_upload_form': file_upload_form,
        }
    )

@login_required()
@csrf_exempt
def ingress(request, index, source, sourcetype):
    log = logging.getLogger(__name__)
    if request.method != "POST":
        return http_405()
    host = get_client_ip(request=request)
    event = Event.objects.create(
        index=index,
        host=host,
        source=source,
        sourcetype=sourcetype,
        text=request.body.decode(),
    )
    if settings.DELVE_ENABLE_EXTRACTIONS_ON_CREATE:
        event.extract_fields()
    if settings.DELVE_ENABLE_PROCESSORSS_ON_CREATE:
        event.process()
    event.save()
    return HttpResponse(
        "<h1>Created!</h1>",
        content_type="text/html",
        status=201,
    )

def index(request):
    if request.method == "GET":
        return render(
            request,
            'project/base.html',
            {},
        )
    else:
        return http_405()
