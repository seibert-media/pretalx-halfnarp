import secrets
from datetime import timedelta

import jsonschema
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

        preferences = Preference.objects.get(hash=halfnarp_hash)
        if not preferences:
            return Response(status=404)

        return JsonResponse({
            'preferred_submissions': preferences.preferred_submission_ids
        }, safe=False)

    def post(self, request, event, *args, **kwargs):
        try:
            validate_preferences_data(request.data)
        except jsonschema.ValidationError as e:
            return Response(status=400, data=str(e))

        halfnarp_hash = self.request.COOKIES.get(HASH_COOKIE, None)
        if halfnarp_hash:
            update_preferences(halfnarp_hash, request.data)
            return Response()
        else:
            halfnarp_hash = create_preferences(request.data)

            r = Response()
            r.set_cookie(HASH_COOKIE, halfnarp_hash, httponly=True, secure=True, samesite="Strict",
                         max_age=timedelta(days=365).total_seconds())
            return r


def validate_preferences_data(request_data):
    schema = {
        "type": "object",
        "properties": {
            "preferred_submissions": {
                "type": "array",
                "items": {
                    "type": "number",
                },
            },
        },
        "required": ["preferred_submissions"]
    }
    jsonschema.validate(request_data, schema)


def update_preferences(halfnarp_hash, request_data):
    preference = Preference.objects.get(hash=halfnarp_hash)
    preference.set_preferred_submission_ids(request_data['preferred_submissions'])
    preference.save()


def create_preferences(request_data):
    halfnarp_hash = secrets.token_hex(64)
    preference = Preference()
    preference.hash = halfnarp_hash
    preference.set_preferred_submission_ids(request_data['preferred_submissions'])
    preference.save()
    return halfnarp_hash
