import jsonschema
from django.http import JsonResponse
from pretalx.cfp.views.event import EventPageMixin
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from pretalx_halfnarp.models import Preference
from pretalx_halfnarp.views import HASH_COOKIE


class FrontendMyPreferencesApi(EventPageMixin, APIView):
    permission_classes = [AllowAny]

    def get(self, request, event, *args, **kwargs):
        halfnarp_hash = request.COOKIES.get(HASH_COOKIE, None)
        if not halfnarp_hash:
            return Response(status=404)

        preferences = Preference.objects.get(hash=halfnarp_hash)
        if not preferences:
            return Response(status=404)

        return JsonResponse(
            {"preferred_submissions": preferences.preferred_submission_ids}, safe=False
        )

    def post(self, request, event, *args, **kwargs):
        try:
            validate_preferences_data(request.data)
        except jsonschema.ValidationError as e:
            return Response(status=400, data=str(e))

        halfnarp_hash = request.COOKIES.get(HASH_COOKIE, None)
        if not halfnarp_hash:
            return Response(400)

        try:
            preference = Preference.objects.get(hash=halfnarp_hash)
        except Preference.DoesNotExist:
            preference = Preference()
            preference.hash = halfnarp_hash

        preference.set_preferred_submission_ids(request.data["preferred_submissions"])
        preference.save()

        return Response(status=204)


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
        "required": ["preferred_submissions"],
    }
    jsonschema.validate(request_data, schema)
