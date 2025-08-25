# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Permission
from .models import (
    User,
    UserProfile,
)

admin.site.register(User, UserAdmin)
admin.site.register(UserProfile)
admin.site.register(Permission)
