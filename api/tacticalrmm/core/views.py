import json
import re
from contextlib import suppress
from pathlib import Path
from zoneinfo import ZoneInfo

import psutil
import requests
from cryptography import x509
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone as djangotime
from django.views.decorators.csrf import csrf_exempt
from redis import from_url
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers

from core.decorators import monitoring_view
from core.tasks import sync_mesh_perms_task
from core.utils import get_core_settings, sysd_svc_is_running, token_is_valid, run_server_script, run_server_task
from logs.models import AuditLog
from tacticalrmm.constants import AuditActionType, PAStatus
from tacticalrmm.helpers import get_certs, notify_error
from tacticalrmm.permissions import (
    _has_perm_on_agent,
    _has_perm_on_client,
    _has_perm_on_site,
)

from .models import CodeSignToken, CoreSettings, CustomField, GlobalKVStore, URLAction
from autotasks.models import AutomatedTask, TaskResult
from scripts.models import Script

from .permissions import (
    CodeSignPerms,
    CoreSettingsPerms,
    CustomFieldPerms,
    ServerMaintPerms,
    URLActionPerms,
    ServerTaskPerms,
    RunServerTaskPerms
)
from .serializers import (
    CodeSignTokenSerializer,
    CoreSettingsSerializer,
    CustomFieldSerializer,
    KeyStoreSerializer,
    URLActionSerializer,
)


class GetEditCoreSettings(APIView):
    permission_classes = [IsAuthenticated, CoreSettingsPerms]

    def get(self, request):
        settings = CoreSettings.objects.first()
        return Response(CoreSettingsSerializer(settings).data)

    def put(self, request):
        data = request.data.copy()

        if getattr(settings, "HOSTED", False):
            data.pop("mesh_site")
            data.pop("mesh_token")
            data.pop("mesh_username")

        coresettings = CoreSettings.objects.first()
        serializer = CoreSettingsSerializer(instance=coresettings, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        sync_mesh_perms_task.delay()

        return Response("ok")


@api_view()
def version(request):
    return Response(settings.APP_VER)


@api_view()
def clear_cache(request):
    from core.utils import clear_entire_cache

    clear_entire_cache()
    return Response("Cache was cleared!")


@api_view()
def dashboard_info(request):
    from core.utils import token_is_expired
    from tacticalrmm.utils import get_latest_trmm_ver, runcmd_placeholder_text

    core_settings = get_core_settings()
    return Response(
        {
            "trmm_version": settings.TRMM_VERSION,
            "latest_trmm_ver": get_latest_trmm_ver(),
            "dark_mode": request.user.dark_mode,
            "show_community_scripts": request.user.show_community_scripts,
            "dbl_click_action": request.user.agent_dblclick_action,
            "default_agent_tbl_tab": request.user.default_agent_tbl_tab,
            "url_action": (
                request.user.url_action.id if request.user.url_action else None
            ),
            "client_tree_sort": request.user.client_tree_sort,
            "client_tree_splitter": request.user.client_tree_splitter,
            "loading_bar_color": request.user.loading_bar_color,
            "clear_search_when_switching": request.user.clear_search_when_switching,
            "hosted": getattr(settings, "HOSTED", False),
            "date_format": request.user.date_format,
            "default_date_format": core_settings.date_format,
            "token_is_expired": token_is_expired(),
            "open_ai_integration_enabled": bool(core_settings.open_ai_token),
            "dash_info_color": request.user.dash_info_color,
            "dash_positive_color": request.user.dash_positive_color,
            "dash_negative_color": request.user.dash_negative_color,
            "dash_warning_color": request.user.dash_warning_color,
            "run_cmd_placeholder_text": runcmd_placeholder_text(),
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated, CoreSettingsPerms])
def email_test(request):
    core = get_core_settings()

    msg, ok = core.send_mail(
        subject="Test from Tactical RMM", body="This is a test message", test=True
    )
    if not ok:
        return notify_error(msg)

    return Response(msg)


@api_view(["POST"])
@permission_classes([IsAuthenticated, ServerMaintPerms])
def server_maintenance(request):
    from tacticalrmm.utils import reload_nats

    if "action" not in request.data:
        return notify_error("The data is incorrect")

    if request.data["action"] == "reload_nats":
        reload_nats()
        return Response("Nats configuration was reloaded successfully.")

    if request.data["action"] == "rm_orphaned_tasks":
        from autotasks.tasks import remove_orphaned_win_tasks

        remove_orphaned_win_tasks.delay()
        return Response("The task has been initiated.")

    if request.data["action"] == "prune_db":
        from logs.models import AuditLog, PendingAction

        if "prune_tables" not in request.data:
            return notify_error("The data is incorrect.")

        tables = request.data["prune_tables"]
        records_count = 0
        if "audit_logs" in tables:
            auditlogs = AuditLog.objects.filter(action=AuditActionType.CHECK_RUN)
            records_count += auditlogs.count()
            auditlogs.delete()

        if "pending_actions" in tables:
            pendingactions = PendingAction.objects.filter(status=PAStatus.COMPLETED)
            records_count += pendingactions.count()
            pendingactions.delete()

        if "alerts" in tables:
            from alerts.models import Alert

            alerts = Alert.objects.all()
            records_count += alerts.count()
            alerts.delete()

        return Response(f"{records_count} records were pruned from the database")

    return notify_error("The data is incorrect")


class GetAddCustomFields(APIView):
    permission_classes = [IsAuthenticated, CustomFieldPerms]

    def get(self, request):
        if "model" in request.query_params.keys():
            fields = CustomField.objects.filter(model=request.query_params["model"])
        else:
            fields = CustomField.objects.all()
        return Response(CustomFieldSerializer(fields, many=True).data)

    def patch(self, request):
        if "model" in request.data.keys():
            fields = CustomField.objects.filter(model=request.data["model"])
            return Response(CustomFieldSerializer(fields, many=True).data)

        return notify_error("The request was invalid")

    def post(self, request):
        serializer = CustomFieldSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response("ok")


class GetUpdateDeleteCustomFields(APIView):
    permission_classes = [IsAuthenticated, CustomFieldPerms]

    def get(self, request, pk):
        custom_field = get_object_or_404(CustomField, pk=pk)

        return Response(CustomFieldSerializer(custom_field).data)

    def put(self, request, pk):
        custom_field = get_object_or_404(CustomField, pk=pk)

        serializer = CustomFieldSerializer(
            instance=custom_field, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response("ok")

    def delete(self, request, pk):
        get_object_or_404(CustomField, pk=pk).delete()

        return Response("ok")


class CodeSign(APIView):
    permission_classes = [IsAuthenticated, CodeSignPerms]

    def get(self, request):
        token = CodeSignToken.objects.first()
        return Response(CodeSignTokenSerializer(token).data)

    def patch(self, request):
        import requests

        try:
            r = requests.post(
                settings.CHECK_TOKEN_URL,
                json={"token": request.data["token"], "api": settings.ALLOWED_HOSTS[0]},
                headers={"Content-type": "application/json"},
                timeout=15,
            )
        except Exception as e:
            return notify_error(str(e))

        if r.status_code in (400, 401):
            return notify_error(r.json()["ret"])
        elif r.status_code == 200:
            t = CodeSignToken.objects.first()
            if t is None:
                CodeSignToken.objects.create(token=request.data["token"])
            else:
                serializer = CodeSignTokenSerializer(instance=t, data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
            return Response("Token was saved")

        try:
            ret = r.json()["ret"]
        except:
            ret = "Something went wrong"
        return notify_error(ret)

    def post(self, request):
        from agents.models import Agent
        from agents.tasks import send_agent_update_task

        token, is_valid = token_is_valid()
        if not is_valid:
            return notify_error("Invalid token")

        agent_ids: list[str] = list(
            Agent.objects.only("pk", "agent_id").values_list("agent_id", flat=True)
        )
        send_agent_update_task.delay(agent_ids=agent_ids, token=token, force=True)
        return Response("Agents will be code signed shortly")

    def delete(self, request):
        CodeSignToken.objects.all().delete()
        return Response("ok")


class GetAddKeyStore(APIView):
    permission_classes = [IsAuthenticated, CoreSettingsPerms]

    def get(self, request):
        keys = GlobalKVStore.objects.all()
        return Response(KeyStoreSerializer(keys, many=True).data)

    def post(self, request):
        serializer = KeyStoreSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response("ok")


class UpdateDeleteKeyStore(APIView):
    permission_classes = [IsAuthenticated, CoreSettingsPerms]

    def put(self, request, pk):
        key = get_object_or_404(GlobalKVStore, pk=pk)

        serializer = KeyStoreSerializer(instance=key, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response("ok")

    def delete(self, request, pk):
        get_object_or_404(GlobalKVStore, pk=pk).delete()

        return Response("ok")


class GetAddURLAction(APIView):
    permission_classes = [IsAuthenticated, CoreSettingsPerms]

    def get(self, request):
        actions = URLAction.objects.all()
        return Response(URLActionSerializer(actions, many=True).data)

    def post(self, request):
        serializer = URLActionSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response("ok")


class UpdateDeleteURLAction(APIView):
    permission_classes = [IsAuthenticated, CoreSettingsPerms]

    def put(self, request, pk):
        action = get_object_or_404(URLAction, pk=pk)

        serializer = URLActionSerializer(
            instance=action, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response("ok")

    def delete(self, request, pk):
        get_object_or_404(URLAction, pk=pk).delete()

        return Response("ok")


class RunURLAction(APIView):
    permission_classes = [IsAuthenticated, URLActionPerms]

    def patch(self, request):
        from requests.utils import requote_uri

        from agents.models import Agent
        from clients.models import Client, Site
        from tacticalrmm.utils import get_db_value, RE_DB_VALUE

        if "agent_id" in request.data.keys():
            if not _has_perm_on_agent(request.user, request.data["agent_id"]):
                raise PermissionDenied()

            instance = get_object_or_404(Agent, agent_id=request.data["agent_id"])
        elif "site" in request.data.keys():
            if not _has_perm_on_site(request.user, request.data["site"]):
                raise PermissionDenied()

            instance = get_object_or_404(Site, pk=request.data["site"])
        elif "client" in request.data.keys():
            if not _has_perm_on_client(request.user, request.data["client"]):
                raise PermissionDenied()

            instance = get_object_or_404(Client, pk=request.data["client"])
        else:
            return notify_error("received an incorrect request")

        action = get_object_or_404(URLAction, pk=request.data["action"])

        url_pattern = action.pattern

        for string, model, prop in re.findall(RE_DB_VALUE, url_pattern):
            value = get_db_value(string=f"{model}.{prop}", instance=instance)

            url_pattern = url_pattern.replace(string, str(value))

        AuditLog.audit_url_action(
            username=request.user.username,
            urlaction=action,
            instance=instance,
            debug_info={"ip": request._client_ip},
        )

        return Response(requote_uri(url_pattern))


class ServerTaskSerializer(serializers.ModelSerializer):

    task_result = serializers.SerializerMethodField()

    def get_task_result(self, obj):
        from autotasks.serializers import TaskResultSerializer
        from autotasks.models import TaskResult
        return (
            TaskResultSerializer(obj.task_result).data
            if isinstance(obj.task_result, TaskResult)
            else {}
        )
    
    def validate_actions(self, value):
        from autotasks.serializers import task_actions_validation
        return task_actions_validation(value)
       
    class Meta:
        model = AutomatedTask
        fields = (
            "id",
            "name",
            "actions",
            "crontab_schedule",
            "enabled",
            "custom_field",
            "collector_all_output",
            "continue_on_error",
            "email_alert",
            "text_alert",
            "dashboard_alert",
            "server_task",
            "alert_severity",
            "task_result"
        )

class GetAddServerTasks(APIView):
    permission_classes = [IsAuthenticated, ServerTaskPerms]

    def get(self, request):
        server_tasks = AutomatedTask.objects.filter(server_task=True)

        results = TaskResult.objects.filter(task__server_task=True)  # type: ignore

        # attach any taskresults to the object
        for task in server_tasks:
            for result in results:
                if result.task.id == task.pk:
                    task.task_result = result
                    break
    
        return Response(ServerTaskSerializer(server_tasks, many=True).data)

    def post(self, request):
        serializer = ServerTaskSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response("ok")


class UpdateDeleteServerTask(APIView):
    permission_classes = [IsAuthenticated, ServerTaskPerms]

    def get(self, request, pk):
        server_task = AutomatedTask.objects.filter(pk=pk, server_task=True)
        return Response(ServerTaskSerializer(server_task).data)

    def put(self, request, pk):
        server_task = get_object_or_404(AutomatedTask, pk=pk)

        serializer = ServerTaskSerializer(
            instance=server_task, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response("ok")

    def delete(self, request, pk):
        get_object_or_404(AutomatedTask, pk=pk).delete()

        return Response("ok")


class RunServerTask(APIView):
    permission_classes = [IsAuthenticated, RunServerTaskPerms]

    def post(self, request, pk):
        server_task = get_object_or_404(AutomatedTask, pk=pk)

        if not server_task.server_task:
            return notify_error("This task is not meant to be run on the server")
        
        output, execution_time = run_server_task(server_task_id=server_task.id)

        # TODO: Audit server task runs
        # AuditLog.audit_url_action(
        #     username=request.user.username,
        #     urlaction=action,
        #     instance=instance,
        #     debug_info={"ip": request._client_ip},
        # )

        return Response({
            "output": output,
            "execution_time": execution_time
        })
    
class RunServerScript(APIView):
    permission_classes = [IsAuthenticated, RunServerTaskPerms]

    def post(self, request, pk):
        script = get_object_or_404(Script, pk=pk)

        
        stdout, stderr, execution_time, retcode = run_server_script(script_id=script.id, args=request.data["args"], env_vars=request.data["env_vars"], timeout=request.data["timeout"])

        # TODO: Audit server task runs
        # AuditLog.audit_url_action(
        #     username=request.user.username,
        #     urlaction=action,
        #     instance=instance,
        #     debug_info={"ip": request._client_ip},
        # )

        return Response({
            "stdout": stdout,
            "stderr": stderr,
            "execution_time": execution_time,
            "retcode": retcode
        })
    
class TwilioSMSTest(APIView):
    permission_classes = [IsAuthenticated, CoreSettingsPerms]

    def post(self, request):
        core = get_core_settings()
        if not core.sms_is_configured:
            return notify_error(
                "All fields are required, including at least 1 recipient"
            )

        msg, ok = core.send_sms("TacticalRMM Test SMS", test=True)
        if not ok:
            return notify_error(msg)

        return Response(msg)


@csrf_exempt
@monitoring_view
def status(request):
    from agents.models import Agent
    from clients.models import Client, Site

    disk_usage: int = round(psutil.disk_usage("/").percent)
    mem_usage: int = round(psutil.virtual_memory().percent)

    cert_file, _ = get_certs()
    cert_bytes = Path(cert_file).read_bytes()

    cert = x509.load_pem_x509_certificate(cert_bytes)
    expires = cert.not_valid_after.replace(tzinfo=ZoneInfo("UTC"))
    now = djangotime.now()
    delta = expires - now

    redis_url = f"redis://{settings.REDIS_HOST}"
    redis_ping = False
    with suppress(Exception):
        with from_url(redis_url) as conn:
            conn.ping()
            redis_ping = True

    ret = {
        "version": settings.TRMM_VERSION,
        "latest_agent_version": settings.LATEST_AGENT_VER,
        "agent_count": Agent.objects.count(),
        "client_count": Client.objects.count(),
        "site_count": Site.objects.count(),
        "disk_usage_percent": disk_usage,
        "mem_usage_percent": mem_usage,
        "days_until_cert_expires": delta.days,
        "cert_expired": delta.days < 0,
        "redis_ping": redis_ping,
    }

    if settings.DOCKER_BUILD:
        ret["services_running"] = "not available in docker"
    else:
        ret["services_running"] = {
            "django": sysd_svc_is_running("rmm.service"),
            "mesh": sysd_svc_is_running("meshcentral.service"),
            "daphne": sysd_svc_is_running("daphne.service"),
            "celery": sysd_svc_is_running("celery.service"),
            "celerybeat": sysd_svc_is_running("celerybeat.service"),
            "redis": sysd_svc_is_running("redis-server.service"),
            "postgres": sysd_svc_is_running("postgresql.service"),
            "mongo": sysd_svc_is_running("mongod.service"),
            "nats": sysd_svc_is_running("nats.service"),
            "nats-api": sysd_svc_is_running("nats-api.service"),
            "nginx": sysd_svc_is_running("nginx.service"),
        }
    return JsonResponse(ret, json_dumps_params={"indent": 2})


class OpenAICodeCompletion(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        settings = get_core_settings()

        if not settings.open_ai_token:
            return notify_error(
                "Open AI API Key not found. Open Global Settings > Open AI."
            )

        if not request.data["prompt"]:
            return notify_error("Not prompt field found")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.open_ai_token}",
        }

        data = {
            "messages": [
                {
                    "role": "user",
                    "content": request.data["prompt"],
                },
            ],
            "model": settings.open_ai_model,
            "temperature": 0.5,
            "max_tokens": 1000,
            "n": 1,
            "stop": None,
        }

        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                data=json.dumps(data),
            )
        except Exception as e:
            return notify_error(str(e))

        response_data = json.loads(response.text)

        if "error" in response_data:
            return notify_error(
                f"The Open AI API returned an error: {response_data['error']['message']}"
            )

        return Response(response_data["choices"][0]["message"]["content"])
