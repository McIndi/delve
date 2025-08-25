# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import ast
# TODO: import logging
import inspect
from types import GeneratorType

from django.db.models.query import QuerySet
from django.contrib.auth.models import Permission
from django.db import models
from django.http import HttpRequest, HttpResponse

from events.util import cast

def has_permission_for_model(permission_string: str, model: models.Model, request: HttpRequest) -> bool:
    permission_names = [
        f"{model._meta.app_label}.{perm.codename}" for perm in
        Permission.objects.filter(
            content_type__model=model._meta.model_name
        )
        if permission_string in perm.codename
    ]
    if len(permission_names) > 1:
        raise ValueError(f"Ambiguous permissions found: {permission_names}")
    elif len(permission_names) < 1:
        raise ValueError(f"No {permission_string} permissions found for {model}")
    else:
        if not request.user.has_perm(permission_names[0]):
            return False
    return True


# def cast(value):
#     if value.isdigit():
#         return int(value)
#     elif value.replace(".", "", 1).isdigit():
#         return float(value)
#     elif value in ["True", "False"]:
#         return True if value=="True" else False
#     elif value.startswith(("[", "{")):
#         return ast.literal_eval(value)
#     return value

def is_results(data):
    if isinstance(data, GeneratorType) or inspect.isgeneratorfunction(data) or isinstance(data, list) or isinstance(data, QuerySet):
        return True
    return False

def ensure_list(data):
    if isinstance(data, GeneratorType) or inspect.isgeneratorfunction(data):
        return list(data)
    elif isinstance(data, QuerySet):
        return list(data.values())
    elif isinstance(data, list):
        return data
    else:
        raise ValueError(f"Cannot convert {type(data)} to list.")
