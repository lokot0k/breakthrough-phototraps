from django.db import models
from ..models.poll import Poll


class IPPoll(models.Model):
    ip = models.CharField(max_length=50)
    poll = models.ForeignKey(Poll, on_delete=models.RESTRICT)
    ans = models.CharField(max_length=500)

    class Meta:
        unique_together = ('ip', 'poll',)
