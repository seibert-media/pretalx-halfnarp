from django.urls import re_path
from pretalx.event.models.event import SLUG_CHARS

from .views import frontend, frontend_preferences_api, organiser

urlpatterns = [
    re_path(
        f"^(?P<event>[{SLUG_CHARS}]+)/p/halfnarp/$",
        frontend.FrontendView.as_view(),
        name="frontend",
    ),
    re_path(
        f"^(?P<event>[{SLUG_CHARS}]+)/p/halfnarp/my-preferences/$",
        frontend_preferences_api.FrontendMyPreferencesApi.as_view(),
        name="frontend_my_preferences_api",
    ),
    re_path(
        f"^orga/event/(?P<event>[{SLUG_CHARS}]+)/p/halfnarp/$",
        organiser.OrganiserView.as_view(),
        name="organiser",
    ),
    re_path(
        f"^orga/event/(?P<event>[{SLUG_CHARS}]+)/settings/p/halfnarp/$",
        organiser.HalfnarpSettingsView.as_view(),
        name="settings",
    ),
]
