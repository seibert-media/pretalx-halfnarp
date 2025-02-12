from collections import Counter

from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic import FormView, TemplateView
from django_context_decorator import context
from pretalx.common.views.mixins import EventPermissionRequired
from pretalx.submission.models import Submission

from pretalx_halfnarp.forms import HalfnarpSettingsForm
from pretalx_halfnarp.models import Preference


class HalfnarpSettingsView(EventPermissionRequired, FormView):
    template_name = "pretalx_halfnarp/settings.html"
    permission_required = "orga.change_settings"
    form_class = HalfnarpSettingsForm

    def get_success_url(self) -> str:
        return reverse(
            "plugins:pretalx_halfnarp:settings",
            kwargs={
                "event": self.request.event.slug,
            },
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return {
            "obj": self.request.event,
            "attribute_name": "settings",
            "locales": self.request.event.locales,
            **kwargs,
        }

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class OrganiserView(EventPermissionRequired, TemplateView):
    permission_required = "orga.view_submissions"
    template_name = "pretalx_halfnarp/organiser.html"

    @context
    @cached_property
    def num_preferences(self):
        return Preference.objects.filter(event=self.request.event).count()

    @context
    @cached_property
    def most_preferred_submissions(self):
        submissions_by_id = {
            submission.id: submission
            for submission in Submission.objects.filter(
                event=self.request.event
            ).prefetch_related("speakers")
        }
        submission_id_counter = Counter()
        for preference in Preference.objects.filter(event=self.request.event):
            submission_id_counter.update(preference.preferred_submission_ids)

        return [
            {"submission": submissions_by_id[id], "count": count}
            for id, count in submission_id_counter.most_common()
        ]

    @context
    @cached_property
    def most_correlated_submissions(self):
        return []

    def get_object(self):
        return self.request.event
