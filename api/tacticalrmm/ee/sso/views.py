"""
Copyright (c) 2023-present Amidaware Inc.
This file is subject to the EE License Agreement.
For details, see: https://license.tacticalrmm.com/ee
"""

import re

from allauth.socialaccount.models import SocialApp
from django.contrib.auth import logout
from django.shortcuts import get_object_or_404
from knox.views import LoginView as KnoxLoginView
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer, ReadOnlyField
from rest_framework.views import APIView
from python_ipware import IpWare

from accounts.permissions import AccountsPerms
from logs.models import AuditLog
from tacticalrmm.utils import get_core_settings
from .permissions import SSOLoginPerms

class SocialAppSerializer(ModelSerializer):
    server_url = ReadOnlyField(source="settings.server_url")
    role = ReadOnlyField(source="settings.role")

    class Meta:
        model = SocialApp
        fields = [
            "id",
            "name",
            "provider",
            "provider_id",
            "client_id",
            "secret",
            "server_url",
            "settings",
            "role",
        ]


class GetAddSSOProvider(APIView):
    permission_classes = [IsAuthenticated, AccountsPerms]

    def get(self, request):
        providers = SocialApp.objects.all()
        return Response(SocialAppSerializer(providers, many=True).data)

    class InputSerializer(ModelSerializer):
        server_url = ReadOnlyField()
        role = ReadOnlyField()

        class Meta:
            model = SocialApp
            fields = [
                "name",
                "client_id",
                "secret",
                "server_url",
                "provider",
                "provider_id",
                "settings",
                "role"
            ]

    # removed any special characters and replaces spaces with a hyphen
    def generate_provider_id(self, string):
        id = re.sub(r"[^A-Za-z0-9\s]", "", string)
        id = id.replace(" ", "-")
        return id

    def post(self, request):
        data = request.data

        # need to move server_url into json settings
        data["settings"] = {}
        data["settings"]["server_url"] = data["server_url"]
        data["settings"]["role"] = data["role"] if data["role"] else None

        # set provider to 'openid_connect'
        data["provider"] = "openid_connect"

        # generate a url friendly provider id from the name
        data["provider_id"] = self.generate_provider_id(data["name"])

        serializer = self.InputSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response("ok")


class GetUpdateDeleteSSOProvider(APIView):
    permission_classes = [IsAuthenticated, AccountsPerms]

    class InputSerialzer(ModelSerializer):
        server_url = ReadOnlyField()
        role = ReadOnlyField()

        class Meta:
            model = SocialApp
            fields = ["client_id", "secret", "server_url", "settings", "role"]

    def put(self, request, pk):
        provider = get_object_or_404(SocialApp, pk=pk)
        data = request.data

        # need to move server_url into json settings
        data["settings"] = {}
        data["settings"]["server_url"] = data["server_url"]
        data["settings"]["role"] = data["role"] if data["role"] else None

        serializer = self.InputSerialzer(
            instance=provider, data=data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response("ok")

    def delete(self, request, pk):
        provider = get_object_or_404(SocialApp, pk=pk)
        provider.delete()
        return Response("ok")


class GetAccessToken(KnoxLoginView):
    permission_classes = [SSOLoginPerms]
    authentication_classes = [SessionAuthentication]

    def post(self, request, format=None):
        
        core = get_core_settings()
        
        # check for auth method before signing in
        if (
            core.sso_enabled
            and "account_authentication_methods" in request.session
            and len(request.session["account_authentication_methods"]) > 0
        ):
            login_method = request.session["account_authentication_methods"][0]

            # get token
            response = super().post(request, format=None)
            response.data["username"] = request.user.username
            response.data["provider"] = login_method["provider"]

            AuditLog.audit_user_login_successful_sso(
                request.user.username, login_method["provider"], login_method
            )

            # log ip
            ipw = IpWare()
            client_ip, _ = ipw.get_client_ip(request.META)
            if client_ip:
                request.user.last_login_ip = str(client_ip)
                request.user.save(update_fields=["last_login_ip"])

            # invalid user session since we have an access token now
            logout(request)

            return Response(response.data)
        else:
            logout(request)
            return Response(
                "No pending login session found", status.HTTP_403_FORBIDDEN
            )


class GetUpdateSSOSettings(APIView):
    permission_classes = [IsAuthenticated, AccountsPerms]

    def get(self, request):

        core_settings = get_core_settings()

        return Response(
            {
                "block_local_user_logon": core_settings.block_local_user_logon,
                "sso_enabled": core_settings.sso_enabled
            }
        )

    def post(self, request):

        data = request.data

        core_settings = get_core_settings()

        core_settings.block_local_user_logon = data["block_local_user_logon"]
        core_settings.sso_enabled = data["sso_enabled"]
        core_settings.save(update_fields=["block_local_user_logon", "sso_enabled"])

        return Response("ok")
