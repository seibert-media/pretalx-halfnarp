from django.db import models


class Preference(models.Model):
    hash = models.CharField(max_length=64, db_index=True)
    created = models.DateTimeField(null=True, auto_now_add=True)
    modified = models.DateTimeField(null=True, auto_now=True)
    preferred_submissions = models.TextField()

    @property
    def preferred_submission_ids(self):
        if self.preferred_submissions:
            return map(int, self.preferred_submissions.split(','))

        return []

    def set_preferred_submission_ids(self, submission_ids):
        self.preferred_submissions = ','.join([str(i) for i in submission_ids])
