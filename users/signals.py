# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission

from .models import UserProfile

@receiver(post_save, sender=get_user_model())
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    elif not hasattr(instance, "profile"):
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=get_user_model())
def assign_user_group(sender, instance, created, **kwargs):
    if created:
        users_group, group_created = Group.objects.get_or_create(name='Users')
        if group_created:
            permissions = [
                Permission.objects.get(codename="add_event"),
                Permission.objects.get(codename="change_event"),
                Permission.objects.get(codename="view_event"),
                Permission.objects.get(codename="delete_event"),

                Permission.objects.get(codename="add_localcontext"),
                Permission.objects.get(codename="change_localcontext"),
                Permission.objects.get(codename="view_localcontext"),
                Permission.objects.get(codename="delete_localcontext"),

                Permission.objects.get(codename="add_globalcontext"),
                Permission.objects.get(codename="change_globalcontext"),
                Permission.objects.get(codename="view_globalcontext"),
                Permission.objects.get(codename="delete_globalcontext"),

                Permission.objects.get(codename="add_fileupload"),
                Permission.objects.get(codename="change_fileupload"),
                Permission.objects.get(codename="view_fileupload"),
                Permission.objects.get(codename="delete_fileupload"),

                Permission.objects.get(codename="add_query"),
                Permission.objects.get(codename="change_query"),
                Permission.objects.get(codename="view_query"),
                Permission.objects.get(codename="delete_query"),
            ]
            users_group.permissions.add(*permissions)
        instance.groups.add(users_group)