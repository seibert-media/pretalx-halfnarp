import contextlib
import random
import secrets
from datetime import datetime, timedelta

from django.utils import timezone
from django.views.generic import TemplateView
from django_context_decorator import context
from pretalx.cfp.views.event import EventPageMixin
from pretalx.submission.models import SubmissionStates

from pretalx_halfnarp.models import Preference
from pretalx_halfnarp.views import HASH_COOKIE


class FrontendView(EventPageMixin, TemplateView):
    template_name = "pretalx_halfnarp/frontend.html"
    halfnarp_hash = None

    def get(self, request, *args, **kwargs):
        self.halfnarp_hash = self.request.COOKIES.get(HASH_COOKIE, None)
        if not self.halfnarp_hash:
            self.halfnarp_hash = secrets.token_hex(32)

        response = super().get(request, *args, **kwargs)
        response.set_cookie(
            HASH_COOKIE,
            self.halfnarp_hash,
            httponly=True,
            secure=True,
            samesite="Lax",
            max_age=timedelta(days=365).total_seconds(),
        )
        return response

    @context
    def submissions(self):
        submissions = list(
            self.request.event.submissions.filter(
                state__in=[SubmissionStates.ACCEPTED, SubmissionStates.CONFIRMED]
            )
        )
        random.Random(self.halfnarp_hash).shuffle(submissions)
        return submissions

    @context
    def preferred_submissions(self):
        try:
            preference = Preference.objects.get(
                hash=self.halfnarp_hash, event=self.request.event
            )
            return list(preference.preferred_submission_ids)
        except Preference.DoesNotExist:
            return []

    @context
    def voting_is_enabled(self):
        until = None
        with contextlib.suppress(AttributeError):
            until = self.request.event.settings.halfnarp_allow_voting_until
        if until is None:
            return not self.request.event.current_schedule

        # `until` is a date; voting is allowed through the end of the selected
        # day, interpreted in the event's own timezone.
        deadline = timezone.make_aware(
            datetime.combine(until + timedelta(days=1), datetime.min.time()),
            self.request.event.tz,
        )
        return timezone.now() < deadline
