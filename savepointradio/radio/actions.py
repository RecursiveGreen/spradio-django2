from django.contrib import messages
from django.forms import inlineformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone

from core.utils import create_success_message, quantify


def change_m2m_items(request, queryset, parent_model, m2m_field,
                     child_field, calling_function, remove=False):
    through_model = getattr(parent_model, m2m_field)
    ItemFormSet = inlineformset_factory(parent_model,
                                        through_model.through,
                                        fields=(child_field,),
                                        can_delete=False,
                                        extra=10,)
    # If we clicked Submit, then continue. . .
    if 'apply' in request.POST:
        # Fill the formset with values from the POST request
        item_formset = ItemFormSet(request.POST)

        # Will only returned "cleaned_data" if form is valid, so check
        if item_formset.is_valid():
            # Remove the empty form data from the list
            data = list(filter(None, item_formset.cleaned_data))

            for child in data:
                for parent in queryset:
                    through = getattr(parent, m2m_field)
                    if request.POST['removal'] == 'True':
                        through.remove(child[child_field])
                    else:
                        through.add(child[child_field])

            # Return with informative success message and counts
            message = create_success_message(parent_model,
                                             queryset.count(),
                                             through_model.field.related_model,
                                             len(data),
                                             request.POST['removal'] == 'True')
            messages.success(request, message)
            return HttpResponseRedirect(request.get_full_path())
        else:
            messages.error(request, "See below for errors in the form.")
    # . . .otherwise, create empty formset.
    else:
        item_formset = ItemFormSet()

    return render(request,
                  'admin/change_m2m_intermediate.html',
                  {'calling_function': calling_function,
                   'parent_queryset': queryset,
                   'item_formset': item_formset,
                   'parent_model': parent_model,
                   'child_model': through_model.field.related_model,
                   'is_removal': remove, })


def publish_items(request, queryset):
    rows_updated = queryset.update(published_date=timezone.now())
    message = quantify(rows_updated, queryset.model)
    messages.success(request, '{} successfully published.'.format(message))
