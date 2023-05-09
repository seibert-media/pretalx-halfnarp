from django.conf.urls import url

from pretalx.event.models.event import SLUG_CHARS
from .views import frontend, frontend_preferences_api

urlpatterns = [
    url(f'^(?P<event>[{SLUG_CHARS}]+)/p/halfnarp$',
        frontend.FrontendView.as_view(), name='frontend'),
    url(f'^(?P<event>[{SLUG_CHARS}]+)/p/halfnarp/my-preferences$',
        frontend_preferences_api.FrontendMyPreferencesApi.as_view(), name='frontend_my_preferences_api'),
]
