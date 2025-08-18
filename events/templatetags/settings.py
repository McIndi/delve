# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

from django import template
from django.conf import settings

register = template.Library()

# settings value
@register.simple_tag
def settings(name):
    return getattr(settings, name, "")
