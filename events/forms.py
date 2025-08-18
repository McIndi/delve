# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

from django import forms
# from django.core.files import uploadhandler

from .models import (
    Query,
    Event,
    FileUpload,
    GlobalContext,
    LocalContext,
)

class FileUploadForm(forms.ModelForm):
    class Meta:
        model = FileUpload
        fields = (
            'title',
            'content',
        )

class GlobalContextForm(forms.ModelForm):
    class Meta:
        model = GlobalContext
        fields = [
            'context',
        ]

class LocalContextForm(forms.ModelForm):
    class Meta:
        model = LocalContext
        fields = [
            'context',
            'name',
        ]

class QueryForm(forms.ModelForm):
    text = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
            }
        )
    )
    name = forms.CharField(
        max_length=1024,
        required=False,
    )
    _save = forms.BooleanField(
        required=False,
    )

    class Meta:
        model = Query
        fields = [
            'text',
            'name',
            '_save',
        ]
        

class ChartForm(forms.Form):
    type = forms.ChoiceField(
        choices=(
            ('bar', 'bar'),
            ('line', 'line'),
        )
    )
    x_field = forms.CharField(
        max_length=255,
    )
    y_field = forms.CharField(
        max_length=255,
    )
    by_field = forms.CharField(
        max_length=255,
    )
    
    class Meta:
        fields = [
            'type',
            'x_field',
            'y_field',
        ]

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'index',
            'host',
            'source',
            'sourcetype',
            'text',
        ]