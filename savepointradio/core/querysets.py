from django.db import models
from django.utils import timezone


class EnabledQuerySet(models.QuerySet):
    """
    Queryset to select all objects that are enabled or not.
    """
    def enabled(self):
        return self.filter(disabled=False)

    def disabled(self):
        return self.filter(disabled=True)


class PublishedQuerySet(models.QuerySet):
    """
    Queryset to select all objects that have been published or not.
    """
    def published(self):
        results = self.filter(
                       models.Q(published_date__isnull=False) &
                       models.Q(published_date__lte=timezone.now())
                  )
        return results

    def unpublished(self):
        results = self.filter(
                       models.Q(published_date__isnull=True) |
                       models.Q(published_date__gte=timezone.now())
                  )
        return results
