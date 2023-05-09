from django.views.generic import TemplateView
from django_context_decorator import context

from pretalx.cfp.views.event import EventPageMixin
from pretalx.submission.models import SubmissionStates
from pretalx_halfnarp.models import Preference
from pretalx_halfnarp.views import HASH_COOKIE


class FrontendView(EventPageMixin, TemplateView):
    template_name = "pretalx_halfnarp/frontend.html"

    @context
    def submissions(self):
        return self.request.event.submissions.filter(
            state__in=[SubmissionStates.ACCEPTED, SubmissionStates.CONFIRMED]
        )

    @context
    def preferred_talks(self):
        halfnarp_hash = self.request.COOKIES.get(HASH_COOKIE, None)
        if halfnarp_hash:
            preference = Preference.objects.get(hash=halfnarp_hash)
            if preference:
                return list(preference.preferred_submission_ids)

        return []
