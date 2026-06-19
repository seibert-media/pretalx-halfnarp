import datetime as dt
import json

import pytest
from django.test import RequestFactory
from django.urls import reverse
from django_scopes import scopes_disabled

from pretalx.schedule.domain.release import freeze_schedule

from pretalx_halfnarp.models import Preference
from pretalx_halfnarp.views import HASH_COOKIE
from pretalx_halfnarp.views.frontend import FrontendView
from pretalx_halfnarp.views.organiser import OrganiserView


@pytest.mark.django_db
def test_frontend_sets_cookie_when_missing(client, event, submission):
    response = client.get(
        reverse("plugins:pretalx_halfnarp:frontend", kwargs={"event": event.slug})
    )
    assert response.status_code == 200
    assert HASH_COOKIE in response.cookies
    assert submission.title in response.content.decode()


@pytest.mark.django_db
def test_frontend_reuses_existing_cookie(client, event, submission, preference):
    client.cookies[HASH_COOKIE] = preference.hash
    response = client.get(
        reverse("plugins:pretalx_halfnarp:frontend", kwargs={"event": event.slug})
    )
    assert response.status_code == 200
    assert response.cookies[HASH_COOKIE].value == preference.hash
    assert submission.title in response.content.decode()


@pytest.mark.django_db
def test_frontend_no_submissions(client, event):
    response = client.get(
        reverse("plugins:pretalx_halfnarp:frontend", kwargs={"event": event.slug})
    )
    assert response.status_code == 200
    assert "does not have any submissions" in response.content.decode()


@pytest.mark.django_db
def test_voting_disabled_when_schedule_released(client, event, submission):
    with scopes_disabled():
        freeze_schedule(event.wip_schedule, "v1")
    response = client.get(
        reverse("plugins:pretalx_halfnarp:frontend", kwargs={"event": event.slug})
    )
    assert response.status_code == 200
    assert "voting period has ended" in response.content.decode()


@pytest.mark.django_db
def test_voting_enabled_until_future_date(client, event, submission):
    event.settings.set("halfnarp_allow_voting_until", "2099-12-31")
    response = client.get(
        reverse("plugins:pretalx_halfnarp:frontend", kwargs={"event": event.slug})
    )
    assert response.status_code == 200
    assert submission.title in response.content.decode()


@pytest.mark.django_db
def test_voting_enabled_on_selected_day(client, event, submission):
    today = dt.date.today().isoformat()
    event.settings.set("halfnarp_allow_voting_until", today)
    response = client.get(
        reverse("plugins:pretalx_halfnarp:frontend", kwargs={"event": event.slug})
    )
    assert response.status_code == 200
    assert submission.title in response.content.decode()


@pytest.mark.django_db
def test_voting_disabled_after_past_date(client, event, submission):
    event.settings.set("halfnarp_allow_voting_until", "2000-01-01")
    response = client.get(
        reverse("plugins:pretalx_halfnarp:frontend", kwargs={"event": event.slug})
    )
    assert response.status_code == 200
    assert "voting period has ended" in response.content.decode()


@pytest.mark.django_db
def test_voting_is_enabled_handles_attributeerror(event):
    class BrokenSettings:
        @property
        def halfnarp_allow_voting_until(self):
            raise AttributeError

    class FakeEvent:
        settings = BrokenSettings()
        current_schedule = None

    view = FrontendView()
    view.request = RequestFactory().get("/")
    view.request.event = FakeEvent()
    assert view.voting_is_enabled() is True


@pytest.mark.django_db
def test_api_get_without_cookie(client, event):
    response = client.get(
        reverse(
            "plugins:pretalx_halfnarp:frontend_my_preferences_api",
            kwargs={"event": event.slug},
        )
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_api_get_without_preference(client, event):
    client.cookies[HASH_COOKIE] = "no-such-hash"
    response = client.get(
        reverse(
            "plugins:pretalx_halfnarp:frontend_my_preferences_api",
            kwargs={"event": event.slug},
        )
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_api_get_with_preference(client, event, preference, submission):
    client.cookies[HASH_COOKIE] = preference.hash
    response = client.get(
        reverse(
            "plugins:pretalx_halfnarp:frontend_my_preferences_api",
            kwargs={"event": event.slug},
        )
    )
    assert response.status_code == 200
    assert submission.id in response.json()["preferred_submissions"]


@pytest.mark.django_db
def test_api_post_invalid_data(client, event):
    client.cookies[HASH_COOKIE] = "somehash"
    response = client.post(
        reverse(
            "plugins:pretalx_halfnarp:frontend_my_preferences_api",
            kwargs={"event": event.slug},
        ),
        data=json.dumps({"preferred_submissions": "not-a-list"}),
        content_type="application/json",
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_api_post_without_cookie(client, event, submission):
    response = client.post(
        reverse(
            "plugins:pretalx_halfnarp:frontend_my_preferences_api",
            kwargs={"event": event.slug},
        ),
        data=json.dumps({"preferred_submissions": [submission.id]}),
        content_type="application/json",
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_api_post_creates_preference(client, event, submission):
    client.cookies[HASH_COOKIE] = "freshhash"
    response = client.post(
        reverse(
            "plugins:pretalx_halfnarp:frontend_my_preferences_api",
            kwargs={"event": event.slug},
        ),
        data=json.dumps({"preferred_submissions": [submission.id]}),
        content_type="application/json",
    )
    assert response.status_code == 204
    with scopes_disabled():
        pref = Preference.objects.get(hash="freshhash", event=event)
        assert list(pref.preferred_submission_ids) == [submission.id]


@pytest.mark.django_db
def test_api_post_updates_preference(client, event, preference, submission):
    client.cookies[HASH_COOKIE] = preference.hash
    response = client.post(
        reverse(
            "plugins:pretalx_halfnarp:frontend_my_preferences_api",
            kwargs={"event": event.slug},
        ),
        data=json.dumps({"preferred_submissions": [submission.id]}),
        content_type="application/json",
    )
    assert response.status_code == 204
    with scopes_disabled():
        preference.refresh_from_db()
        assert list(preference.preferred_submission_ids) == [submission.id]


@pytest.mark.django_db
def test_organiser_dashboard(orga_client, event, preference, submission):
    response = orga_client.get(
        reverse("plugins:pretalx_halfnarp:organiser", kwargs={"event": event.slug})
    )
    assert response.status_code == 200
    assert submission.title in response.content.decode()


@pytest.mark.django_db
def test_organiser_dashboard_empty(orga_client, event):
    response = orga_client.get(
        reverse("plugins:pretalx_halfnarp:organiser", kwargs={"event": event.slug})
    )
    assert response.status_code == 200
    assert "no votes yet" in response.content.decode()


@pytest.mark.django_db
def test_organiser_dashboard_ignores_deleted_submissions(orga_client, event):
    with scopes_disabled():
        pref = Preference(hash="ghosthash", event=event)
        pref.preferred_submission_ids = [99999]
        pref.save()
    response = orga_client.get(
        reverse("plugins:pretalx_halfnarp:organiser", kwargs={"event": event.slug})
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_organiser_dashboard_visible_to_reviewer(review_client, event):
    response = review_client.get(
        reverse("plugins:pretalx_halfnarp:organiser", kwargs={"event": event.slug})
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_organiser_dashboard_forbidden_for_unprivileged(other_client, event):
    response = other_client.get(
        reverse("plugins:pretalx_halfnarp:organiser", kwargs={"event": event.slug})
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_organiser_get_object(event):
    view = OrganiserView()
    view.request = RequestFactory().get("/")
    view.request.event = event
    assert view.get_object() == event


@pytest.mark.django_db
def test_settings_view_get(orga_client, event):
    response = orga_client.get(
        reverse("plugins:pretalx_halfnarp:settings", kwargs={"event": event.slug})
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_settings_view_post(orga_client, event):
    response = orga_client.post(
        reverse("plugins:pretalx_halfnarp:settings", kwargs={"event": event.slug}),
        {"halfnarp_allow_voting_until": "2099-12-31"},
        follow=True,
    )
    assert response.status_code == 200
    assert event.settings.halfnarp_allow_voting_until == dt.date(2099, 12, 31)


@pytest.mark.django_db
def test_settings_view_forbidden_for_reviewer(review_client, event):
    response = review_client.get(
        reverse("plugins:pretalx_halfnarp:settings", kwargs={"event": event.slug})
    )
    assert response.status_code == 404
