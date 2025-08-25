# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import logging

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.conf import settings

from .models import (
    Event,
    BaseEvent,
    GlobalContext,
    LocalContext,
)

@receiver(pre_save, sender=GlobalContext)
def validate_global_context(sender, instance, **kwargs):
    instance.full_clean()
    
# @receiver(pre_save, sender=LocalContext)
# def validate_local_context(sender, instance, **kwargs):
#     instance.full_clean()
    
@receiver(post_save, sender=get_user_model())
def create_global_context(sender, instance, created, **kwargs):
    if created:
        GlobalContext.objects.create(user=instance, context={})
    elif not hasattr(instance, "global_context"):
        GlobalContext.objects.create(user=instance, context={})

@receiver(pre_save, sender=Event)
def extract_fields_and_process(sender, instance, **kwargs):
    log = logging.getLogger(__name__)
    log.debug(f"Found instance: {instance}")
    # Reference: https://stackoverflow.com/questions/11561722/django-what-is-the-role-of-modelstate
    created = instance._state.adding
    log.debug(f"instance found to be created: {created}")

    if created and settings.DELVE_ENABLE_EXTRACTIONS_ON_CREATE:
        log.debug(f"Extracting fields on new event: {instance}")
        instance.extract_fields()
    if created and settings.DELVE_ENABLE_PROCESSORSS_ON_CREATE:
        log.debug(f"Processing new event: {instance}")
        instance.process()
    if not created and settings.DELVE_ENABLE_EXTRACTIONS_ON_UPDATE:
        log.debug(f"Extracting fields on existing event: {instance}")
        instance.extract_fields()
    if not created and settings.DELVE_ENABLE_PROCESSORSS_ON_UPDATE:
        log.debug(f"Processing existing event: {instance}")
        instance.process()