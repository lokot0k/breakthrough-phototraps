import json

from django.http import HttpRequest, JsonResponse, HttpResponse

from ..service import poll, IPPoll
from django.views.generic import View


class PollView(View):
    def get(self, request: HttpRequest, uuid, *args,
            **kwargs) -> JsonResponse | HttpResponse:
        # todo return chart data based on link
        fr = IPPoll.dump_by_url(uuid)
        return JsonResponse(
            {'success': 'true', 'message': 'unsupported method'})

    def post(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        body = json.loads(request.body)
        new_poll = poll.create(body['question'])
        return JsonResponse(
            {'success': 'true', 'message': 'poll created', 'url': "/" + new_poll.url})

    def head(self, request, *args, **kwargs):
        return JsonResponse(
            {'success': 'false', 'message': 'unsupported method'}, status=403)

    def put(self, request, *args, **kwargs):
        return JsonResponse(
            {'success': 'false', 'message': 'unsupported method'}, status=403)
