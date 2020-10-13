from django.urls import path
from . import views

urlpatterns = [
    path("<int:pk>/getwinupdates/", views.get_win_updates),
    path("<int:pk>/runupdatescan/", views.run_update_scan),
    path("editpolicy/", views.edit_policy),
    path("winupdater/", views.win_updater),
    path("results/", views.results),
    path("<int:pk>/installnow/", views.install_updates),
]
