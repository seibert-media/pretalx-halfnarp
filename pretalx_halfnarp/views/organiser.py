from collections import Counter

from django.views.generic import TemplateView
from django_context_decorator import context

from pretalx.common.mixins.views import EventPermissionRequired
from pretalx.submission.models import Submission
from pretalx_halfnarp.models import Preference


class OrganiserView(EventPermissionRequired, TemplateView):
    permission_required = "orga.view_submissions"
    template_name = "pretalx_halfnarp/organiser.html"

    @context
    def num_preferences(self):
        return Preference.objects.count()

    @context
    def most_preferred_submissions(self):
        submissions_by_id = {
            submission.id: submission
            for submission in Submission.objects.all()
        }
        submission_id_counter = Counter()
        for preference in Preference.objects.all():
            for submission_id in preference.preferred_submission_ids:
                submission_id_counter[submission_id] += 1

        return [
            {
                "submission": submissions_by_id[item[0]],
                "count": item[1]
            }
            for item in submission_id_counter.most_common()
            if item[0] in submissions_by_id
        ]

    @context
    def most_correlated_submissions(self):
        return []
