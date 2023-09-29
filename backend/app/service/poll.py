import uuid
from ..models.poll import Poll

def create(question: str ):
    new_uuid = str(uuid.uuid4())
    poll = Poll.objects.create(question_text=question, url=new_uuid)
    poll.save()
    return poll
