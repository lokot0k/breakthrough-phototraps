from ..models import IPPoll


def dump_by_url(uuid: str):
    return IPPoll.objects.filter(poll__url=uuid)


def create(ip, poll, ans):
    ippoll = IPPoll.objects.create(ans=ans, ip=ip, poll=poll)
    ippoll.save()
    return ippoll