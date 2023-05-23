from django.apps import AppConfig
from django.utils.translation import gettext_lazy


class PluginApp(AppConfig):
    name = "pretalx_halfnarp"
    verbose_name = "tbd"

    class PretalxPluginMeta:
        name = gettext_lazy("Pretalx Halfnarp")
        author = "Peter Körner"
        description = gettext_lazy(
            "Pretalx-Halfnarp is a Plugin that helps you to estimate the interest in your submissions and plan "
            "room-sizes accordingly by scheduling the most requested submissions into the larger rooms. It can "
            "also help you avoid overlaps by correlating submissions that are preferred by the same people so "
            "that you can plan them at different times. "
            ""
            "Halfnarp is an anagram of Fahrplan, a not-yet sorted Fahrplan"
        )
        visible = True
        version = "1.0.0"

    def ready(self):
        from . import signals  # NOQA
