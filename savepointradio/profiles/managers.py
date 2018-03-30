from django.db import models


class RequestManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def unplayed(self):
        return self.get_queryset().filter(queued_at__isnull=True,
                                          played_at__isnull=True)

    def played(self):
        return self.get_queryset().filter(models.Q(queued_at__isnull=False) |
                                          models.Q(played_at__isnull=False))

    def get_played_requests(self, limit=None):
        if limit:
            return self.played()[0:limit]
        return self.played()

    def next_request(self):
        return self.unplayed().earliest('created_date')
