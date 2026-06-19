import pytest
from django_scopes import scopes_disabled

from pretalx_halfnarp.models import Preference


@pytest.mark.django_db
def test_preference_ids_roundtrip(event):
    with scopes_disabled():
        pref = Preference(hash="abc", event=event)
        pref.preferred_submission_ids = [3, 1, 2]
        pref.save()
        pref.refresh_from_db()
        assert pref.preferred_submissions == "3,1,2"
        assert list(pref.preferred_submission_ids) == [3, 1, 2]


@pytest.mark.django_db
def test_preference_ids_empty(event):
    with scopes_disabled():
        pref = Preference(hash="empty", event=event, preferred_submissions="")
        assert pref.preferred_submission_ids == []
