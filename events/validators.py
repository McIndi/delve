# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import logging
from typing import (
    Dict,
    List,
    Any,
    Optional,
    Union,
    Annotated,
)

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.db.models.query import QuerySet
from django.utils.module_loading import import_string
from django.db.models import Model

from pydantic import BaseModel, conlist
from annotated_types import Len

class ListOfDicts(BaseModel):
    events: List[Dict[str, Any]]

class QuerySet(BaseModel, arbitrary_types_allowed=True):
    events: QuerySet

class ListOfEvents(BaseModel, arbitrary_types_allowed=True):
    events: List[Model]

class QuerySetOrListOfDictsOrEvents(BaseModel, arbitrary_types_allowed=True):
    events: QuerySet|List[Dict[str, Any]]|List[Model]

class NonEmptyListOfDictsOrQuerySet(BaseModel, arbitrary_types_allowed=True):
    events: Annotated[List[Dict[str, Any]]|QuerySet, Len(min_length=1)]

class ListOfAny(BaseModel):
    events: List[Any]

class ListOfInts(BaseModel):
    events: List[int]

class ListOfStrs(BaseModel):
    events: List[str]

class QuerySetOrListOfDicts(BaseModel, arbitrary_types_allowed=True):
    events: QuerySet|List[Dict[str, Any]]

class MustBeFirst(BaseModel):
    events: Annotated[list[str], Len(min_length=0, max_length=0)]

@deconstructible
class JsonObjectValidator:
    def __init__(self, types):
        self.types = types

    def __call__(self, value):
        log = logging.getLogger(__name__)
        # print(f"Found value: {type(value)}({value})")
        if not isinstance(value, dict):
            raise ValidationError("Value must be a dictionary.")
