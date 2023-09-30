from django.urls import path
from .views import ml, ml_disk

urlpatterns = [
    # path('', views.index, name="index"),
    # path('', poll.PollView.as_view(), name="poll"),
    # path('vote/', IPPoll.IPPollView.as_view(), name="IPPoll"),
    # path('<str:uuid>', poll.PollView.as_view(), name="poll_all"),
    path('do_good/', ml.MlView.as_view(), name="do_good"),
    path('do_good_url/', ml_disk.MlDiskView.as_view(), name="do_good_by_url")
]
