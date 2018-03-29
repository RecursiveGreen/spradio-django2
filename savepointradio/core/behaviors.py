from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class Disableable(models.Model):
    """
    Mixin for models that can be disabled with a specified reason.
    """
    disabled = models.BooleanField(_('disabled state'), default=False)
    disabled_date = models.DateTimeField(_('disabled on'),
                                         default=None,
                                         blank=True,
                                         null=True)
    disabled_reason = models.TextField(_('reason for disabling'), blank=True)

    class Meta:
        abstract = True

    def disable(self, reason=''):
        self.disabled = True
        self.disabled_date = timezone.now()
        self.disabled_reason = reason
        self.save(update_fields=['disabled',
                                 'disabled_date',
                                 'disabled_reason'])

    def enable(self):
        self.disabled = False
        self.disabled_date = None
        self.disabled_reason = ''
        self.save(update_fields=['disabled',
                                 'disabled_date',
                                 'disabled_reason'])

    def _is_enabled(self):
        return not self.disabled
    _is_enabled.boolean = True
    is_enabled = property(_is_enabled)


class Publishable(models.Model):
    """
    Mixin for models that can be published to restrict accessibility before an
    appointed date/time.
    """
    published_date = models.DateTimeField(_('published for listening'),
                                          default=None,
                                          blank=True,
                                          null=True)

    class Meta:
        abstract = True

    def publish(self, date=None):
        if date is None:
            date = timezone.now()
        self.published_date = date
        self.save(update_fields=['published_date'])

    def _is_published(self):
        if self.published_date is not None:
            return self.published_date < timezone.now()
        return False
    _is_published.boolean = True
    is_published = property(_is_published)


class Timestampable(models.Model):
    """
    Mixin for keeping track of when an object was created and last modified.
    """
    created_date = models.DateTimeField(_('added on'), auto_now_add=True)
    modified_date = models.DateTimeField(_('last modified'), auto_now=True)

    class Meta:
        abstract = True
