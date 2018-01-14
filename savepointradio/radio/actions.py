from django.contrib import messages
from django.utils import timezone

from core.utils import build_message_start


def publish_items(request, queryset):
    rows_updated = queryset.update(published_date=timezone.now())
    message = build_message_start(rows_updated, queryset.model)
    messages.success(request, '{} successfully published.'.format(message))
