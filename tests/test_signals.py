import pytest
from django.test import RequestFactory
from django.urls import reverse

from pretalx_halfnarp.signals import navbar_info, navbar_info_settings


def _request(user, event, url_name):
    url = reverse(f"plugins:pretalx_halfnarp:{url_name}", kwargs={"event": event.slug})
    request = RequestFactory().get(url)
    request.user = user
    request.event = event
    return request


@pytest.mark.django_db
def test_nav_event_for_orga(orga_user, event):
    result = navbar_info_settings(
        sender=event, request=_request(orga_user, event, "organiser")
    )
    assert len(result) == 1
    assert result[0]["active"] is True


@pytest.mark.django_db
def test_nav_event_for_unprivileged(other_user, event):
    result = navbar_info_settings(
        sender=event, request=_request(other_user, event, "organiser")
    )
    assert result == []


@pytest.mark.django_db
def test_nav_event_settings_for_orga(orga_user, event):
    result = navbar_info(sender=event, request=_request(orga_user, event, "settings"))
    assert len(result) == 1
    assert result[0]["active"] is True


@pytest.mark.django_db
def test_nav_event_settings_for_reviewer(review_user, event):
    result = navbar_info(sender=event, request=_request(review_user, event, "settings"))
    assert result == []
