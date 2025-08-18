# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages


from .forms import (
    UserProfileForm,
)

# class CustomUserCreationForm(UserCreationForm):
#     class Meta:
#         model = get_user_model()
#         fields = [
#             'username',
#             'password1',
#             'password2',
#         ]

# class SignUpView(CreateView):
#     form_class = CustomUserCreationForm
#     success_url = reverse_lazy("login")
#     template_name = "registration/signup.html"


def http_405():
    return HttpResponse(
        "<p>Method Not Allowed</p>",
        content_type="text/html",
        status=405,
    )

@login_required()
def edit_user_profile(request):
    if request.method == "POST":
        user_profile_form = UserProfileForm(request.POST, instance=request.user.profile)
        if user_profile_form.is_valid():
            user_profile_form.save()
            messages.add_message(
                request=request,
                level=messages.SUCCESS,
                message="Profile successfully updated."
            )
    elif request.method == "GET":
        user_profile_form = UserProfileForm(instance=request.user.profile)
    else:
        return http_405()
    return render(
        request,
        "users/edit_user_profile.html",
        {
            "user_profile_form": user_profile_form,
        }
    )