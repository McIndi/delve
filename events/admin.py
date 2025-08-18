# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

from django.contrib import admin

from .models import (
    Query,
    Event,
    GlobalContext,
    LocalContext,
    FileUpload,
)

@admin.register(FileUpload)
class FileUploadAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "created",
        "modified",
        "user",
        "content",
        "title",
    )
    search_fields = (
        "id",
        "created",
        "modified",
        "user",
        "title",
    )

@admin.register(GlobalContext)
class GlobalContextAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "created",
        "modified",
        "user",
        "context",
    )
    search_fields = (
        "id",
        "created",
        "modified",
        "user",
        "context",
    )

@admin.register(LocalContext)
class LocalContextAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "created",
        "modified",
        "user",
        "name",
        "context",
    )
    search_fields = (
        "id",
        "created",
        "modified",
        "user",
        "name",
        "context",
    )

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "created",
        # "modified",
        "host",
        "index",
        "source",
        "sourcetype",
        "text",
        "extracted_fields",
    )
    search_fields = (
        "id",
        "created",
        # "modified",
        "host",
        "index",
        "source",
        "sourcetype",
        "text",
        "extracted_fields",
    )

@admin.register(Query)
class QueryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "id",
        "created",
        "modified",
        "text",
    )
    search_fields = (
        "id",
        "created",
        "modified",
        "text",
    )
