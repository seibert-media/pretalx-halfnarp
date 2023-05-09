import secrets

from django.http import JsonResponse
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from pretalx.cfp.views.event import EventPageMixin
from pretalx_halfnarp.models import Preference
from pretalx_halfnarp.views import HASH_COOKIE


class FrontendMyPreferencesApi(EventPageMixin, APIView):
    permission_classes = [AllowAny]

    def get(self, request, event, *args, **kwargs):
        halfnarp_hash = self.request.COOKIES.get(HASH_COOKIE, None)
        if not halfnarp_hash:
            return Response(status=404)

        preferences = get_preferences(halfnarp_hash)
        if not preferences:
            return Response(status=404)

        return JsonResponse(preferences, safe=False)

    def post(self, request, event, *args, **kwargs):
        if not preferences_data_is_valid(request.data):
            return Response(status=400)

        halfnarp_hash = self.request.COOKIES.get(HASH_COOKIE, None)
        if halfnarp_hash:
            update_preferences(halfnarp_hash, request.data)
            return Response()
        else:
            halfnarp_hash = create_preferences(request.data)

            r = Response()
            r.set_cookie(HASH_COOKIE, halfnarp_hash, httponly=True, secure=True, samesite="Strict")
            return r


def preferences_data_is_valid(request_data):
    return type(request_data) == list and all(type(i) == int for i in request_data)


def get_preferences(halfnarp_hash):
    preference = Preference.objects.get(hash=halfnarp_hash)
    if not preference:
        return None

    return [int(i) for i in preference.preferred_submissions.split(',')]


def update_preferences(halfnarp_hash, request_data):
    preference = Preference.objects.get(hash=halfnarp_hash)
    preference.preferred_submissions = ','.join([str(i) for i in request_data])
    preference.save()


def create_preferences(request_data):
    halfnarp_hash = secrets.token_hex(64)
    preference = Preference()
    preference.hash = halfnarp_hash
    preference.preferred_submissions = ','.join([str(i) for i in request_data])
    preference.save()
    return halfnarp_hash
