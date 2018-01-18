from django.db import models


class RequestManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def unplayed(self):
        return self.get_queryset().filter(queued_at__isnull=True,
                                          played_at__isnull=True)

    def next_request(self):
        return self.unplayed().earliest('created_date')
