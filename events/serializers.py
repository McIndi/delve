# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import logging

from django.db import IntegrityError
from django.conf import settings

from rest_framework import serializers
from rest_framework.exceptions import (
    ValidationError,
)
from rest_framework.fields import CurrentUserDefault

from .models import (
    Event,
    Query,
    GlobalContext,
    LocalContext,
    FileUpload,
)

class FileUploadSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=CurrentUserDefault(),
    )

    class Meta:
        model=FileUpload
        fields = [
            'id',
            'created',
            'modified',
            'title',
            'content',
            'user',
        ]
        read_only_fields = [
            'id',
            'created',
            'modified',
            'user',
        ]


class GlobalContextSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=CurrentUserDefault(),
    )

    class Meta:
        model=GlobalContext
        fields = [
            'id',
            'created',
            'modified',
            'context',
            'user',
        ]
        read_only_fields = [
            'id',
            'created',
            'modified',
            'user',
        ]

class LocalContextSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=CurrentUserDefault(),
    )
    context = serializers.JSONField()

    class Meta:
        model=LocalContext
        fields = [
            'id',
            'created',
            'modified',
            'name',
            'context',
            'user',
        ]
        read_only_fields = [
            'id',
            'created',
            'modified',
            'user',
        ]

class QuerySerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=CurrentUserDefault(),
    )

    class Meta:
        model=Query
        fields = [
            'id',
            'created',
            'modified',
            'text',
            'name',
            '_save',
            'user',
        ]
        read_only_fields = [
            'id',
            'created',
            'modified',
            'user',
        ]

class BulkEventSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        log = logging.getLogger("delve")
        result = []
        for attrs in validated_data:
            log.debug(f"Creating events, found {attrs=}")
            result.append(self.child.create(attrs))
        # result = [self.child.create(attrs) for attrs in validated_data]
        try:
            self.child.Meta.model.objects.bulk_create(result)
        except IntegrityError as e:
            raise ValidationError(e)
        return result

class EventSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    user = serializers.HiddenField(
        default=CurrentUserDefault(),
    )

    class Meta:
        model = Event
        list_serializer_class = BulkEventSerializer
        fields = [
            'id',
            'created',
            # 'modified',
            'index',
            'source',
            'sourcetype',
            'host',
            'text',
            'user',
            'extracted_fields',
        ]
        read_only_fields = [
            'id',
            'created',
            # 'modified',
            'user'
        ]
    
    def create(self, validated_data):
        instance = Event(**validated_data)
        if settings.DELVE_ENABLE_EXTRACTIONS_ON_CREATE:
            instance.extract_fields()
        if settings.DELVE_ENABLE_PROCESSORSS_ON_CREATE:
            instance.process()
        if isinstance(self._kwargs["data"], dict):
            instance.save()
        return instance

    def update(self, instance, validated_data):
        for key, value in validated_data.items(): 
            setattr(instance, key, value)
        if settings.DELVE_ENABLE_EXTRACTIONS_ON_UPDATE:
            instance.extract_fields()
        if settings.DELVE_ENABLE_PROCESSORSS_ON_UPDATE:
            instance.process()
        instance.save()
        return instance
