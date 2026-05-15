import datetime as dt

import pytest
from django.core import management
from django_scopes import scopes_disabled

from pretalx.event.domain.event import initialise_event
from pretalx.event.domain.plugins import enable_plugin
from pretalx.event.models import Event, Organiser, Team
from pretalx.person.models import SpeakerProfile, User
from pretalx.submission.models import Submission, SubmissionStates

from pretalx_halfnarp.models import Preference


@pytest.fixture(scope="session", autouse=True)
def collect_static(request):
    management.call_command("collectstatic", "--noinput", "--clear")


@pytest.fixture
def organiser():
    with scopes_disabled():
        o = Organiser.objects.create(name="Super Organiser", slug="superorganiser")
        Team.objects.create(
            name="Organisers",
            organiser=o,
            can_create_events=True,
            can_change_teams=True,
            can_change_organiser_settings=True,
            can_change_event_settings=True,
            can_change_submissions=True,
        )
        Team.objects.create(name="Reviewers", organiser=o, is_reviewer=True)
    return o


@pytest.fixture
def event(organiser):
    today = dt.date.today()
    with scopes_disabled():
        event = Event.objects.create(
            name="Fancy testevent",
            is_public=True,
            slug="test",
            email="orga@orga.org",
            date_from=today,
            date_to=today + dt.timedelta(days=3),
            organiser=organiser,
        )
        initialise_event(event)
        enable_plugin(event, "pretalx_halfnarp")
        event.save()
        for team in organiser.teams.all():
            team.limit_events.add(event)
    return event


@pytest.fixture
def orga_user(event):
    with scopes_disabled():
        user = User.objects.create_user(
            password="orgapassw0rd", email="orgauser@orga.org", name="Orga User"
        )
        team = event.organiser.teams.filter(
            can_change_organiser_settings=True, is_reviewer=False
        ).first()
        team.members.add(user)
        team.save()
    return user


@pytest.fixture
def review_user(event):
    with scopes_disabled():
        user = User.objects.create_user(
            password="reviewpassw0rd", email="reviewuser@orga.org", name="Review User"
        )
        team = event.organiser.teams.filter(
            can_change_organiser_settings=False, is_reviewer=True
        ).first()
        team.members.add(user)
        team.save()
    return user


@pytest.fixture
def other_user(event):
    with scopes_disabled():
        return User.objects.create_user(
            password="otherpassw0rd", email="other@example.org", name="Nobody"
        )


@pytest.fixture
def orga_client(orga_user, client):
    client.force_login(orga_user)
    return client


@pytest.fixture
def review_client(review_user, client):
    client.force_login(review_user)
    return client


@pytest.fixture
def other_client(other_user, client):
    client.force_login(other_user)
    return client


@pytest.fixture
def speaker(event):
    with scopes_disabled():
        user = User.objects.create_user(
            password="speakerpassw0rd", email="speaker@example.org", name="Jane Speaker"
        )
        return SpeakerProfile.objects.create(user=user, event=event)


@pytest.fixture
def submission(event, speaker):
    with scopes_disabled():
        sub = Submission.objects.create(
            event=event,
            title="Accepted Submission",
            submission_type=event.cfp.default_type,
            state=SubmissionStates.ACCEPTED,
            abstract="A fascinating talk.",
        )
        sub.speakers.add(speaker)
    return sub


@pytest.fixture
def other_submission(event, speaker):
    with scopes_disabled():
        sub = Submission.objects.create(
            event=event,
            title="Confirmed Submission",
            submission_type=event.cfp.default_type,
            state=SubmissionStates.CONFIRMED,
        )
        sub.speakers.add(speaker)
    return sub


@pytest.fixture
def preference(event, submission, other_submission):
    with scopes_disabled():
        pref = Preference(hash="testhash", event=event)
        pref.preferred_submission_ids = [submission.id, other_submission.id]
        pref.save()
    return pref
