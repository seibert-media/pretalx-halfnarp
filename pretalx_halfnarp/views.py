from django_context_decorator import context
from django.views.generic import TemplateView

from pretalx.cfp.views.event import EventPageMixin
from pretalx.submission.models import SubmissionStates


class FrontendView(EventPageMixin, TemplateView):
    template_name = "pretalx_halfnarp/frontend.html"

    @context
    def submissions(self):
        return self.request.event.submissions.filter(
            state__in=[SubmissionStates.ACCEPTED, SubmissionStates.CONFIRMED]
        )
