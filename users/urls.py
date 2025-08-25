# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

from django.urls import path

from .views import (
    edit_user_profile,
)


urlpatterns = [
    path("profile/", edit_user_profile, name="profile"),
]
