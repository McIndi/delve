# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

"""
URL configuration for delve project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path("accounts/", include("users.urls")),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('events.urls')),
] + static(
    settings.STATIC_URL,
    document_root=settings.STATIC_ROOT,
)

if settings.DEBUG:
    try:
        from debug_toolbar.toolbar import debug_toolbar_urls
        urlpatterns += debug_toolbar_urls()
    except:
        print(
            "Debug is enabled but Debug toolbar is not installed or not "
            "configured properly. Install it with 'pip install "
            "django-debug-toolbar' and add 'debug_toolbar' to INSTALLED_APPS."
        )
