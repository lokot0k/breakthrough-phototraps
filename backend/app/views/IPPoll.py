import json

from django.http import HttpRequest, JsonResponse, HttpResponse

from ..service import poll
from django.views.generic import View


class IPPollView(View):
    def get(self, request: HttpRequest, *args,
            **kwargs) -> JsonResponse | HttpResponse:

        return JsonResponse(
            {'success': 'false', 'message': 'unsupported method'}, status=403)

    def post(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        body = json.loads(request.body)
        new_ippoll = poll.create(body['question'])
        return JsonResponse(
            {'success': 'true', 'message': 'poll created', 'url': "/" + new_poll.url})

    def head(self, request, *args, **kwargs):
        return JsonResponse(
            {'success': 'false', 'message': 'unsupported method'}, status=403)

    def put(self, request, *args, **kwargs):
        return JsonResponse(
            {'success': 'false', 'message': 'unsupported method'}, status=403)
