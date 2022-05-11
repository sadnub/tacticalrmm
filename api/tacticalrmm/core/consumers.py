from typing import Dict, Any, cast
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from django.db.models import F
from django.utils import timezone as djangotime
from django.conf import settings
from core.utils import get_core_settings
from tacticalrmm.utils import get_latest_trmm_ver

from agents.models import Agent


class MainConnection(AsyncJsonWebsocketConsumer):
    async def connect(self) -> None:

        self.user = self.scope["user"]

        if isinstance(self.user, AnonymousUser):
            await self.close()

        await self.accept()
        await self.send_json(await self.send_agent_count())
        await self.send_json(await self.send_dashboard_info())

    async def disconnect(self, close_code: int) -> None:
        await self.close(close_code)

    async def receive_json(self, data: Dict[str, Any]) -> None:
        if "message" in data.keys():
            if data["message"] == "agent_count":
                await self.send_json(await self.send_agent_count())
            elif data["message"] == "dashboard_info":
                await self.send_json(await self.send_dashboard_info())

    @database_sync_to_async
    def send_agent_count(self) -> Dict[str, Any]:
        total_server_agents_count = (
            Agent.objects.filter_by_role(self.user) # type: ignore
            .filter(monitoring_type="server")
            .count()
        )
        offline_server_agents_count = (
            Agent.objects.filter_by_role(self.user) # type: ignore
            .filter(monitoring_type="server")
            .filter(
                last_seen__lt=djangotime.now()
                - (djangotime.timedelta(minutes=1) * cast(int, F("offline_time")))
            )
            .count()
        )
        total_workstation_agents_count = (
            Agent.objects.filter_by_role(self.user) # type: ignore
            .filter(monitoring_type="workstation")
            .count()
        )
        offline_workstation_agents_count = (
            Agent.objects.filter_by_role(self.user) # type: ignore
            .filter(monitoring_type="workstation")
            .filter(
                last_seen__lt=djangotime.now()
                - (djangotime.timedelta(minutes=1) * cast(int, F("offline_time")))
            )
            .count()
        )

        return {
            "message": "agent_count",
            "server_offline_count": offline_server_agents_count,
            "workstation_offline_count": offline_workstation_agents_count,
            "server_count": total_server_agents_count,
            "workstation_count": total_workstation_agents_count,
        }

    @database_sync_to_async
    def send_dashboard_info(self) -> Dict[str, Any]:

        return {
            "message": "dashboard_info",
            "trmm_version": settings.TRMM_VERSION,
            "latest_trmm_version": get_latest_trmm_ver(),
            "dark_mode": self.user.dark_mode,
            "show_community_scripts": self.user.show_community_scripts,
            "dbl_click_action": self.user.agent_dblclick_action,
            "default_agent_tbl_tab": self.user.default_agent_tbl_tab,
            "url_action": self.user.url_action.id
            if self.user.url_action
            else None,
            "client_tree_sort": self.user.client_tree_sort,
            "client_tree_splitter": self.user.client_tree_splitter,
            "loading_bar_color": self.user.loading_bar_color,
            "clear_search_when_switching": self.user.clear_search_when_switching,
            "hosted": getattr(settings, "HOSTED", False),
            "date_format": self.user.date_format,
            "default_date_format": get_core_settings().date_format,
        }  
            