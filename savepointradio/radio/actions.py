from django import forms
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone

from core.utils import create_success_message, quantify


def change_items(request, queryset, parent_field, calling_function,
                 m2m=None, remove=False):
    through_field = getattr(queryset.model, parent_field)
    child_model = through_field.field.related_model

    class ItemForm(forms.Form):
        # _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
        item = forms.ModelChoiceField(child_model.objects.all())

    if m2m:
        ItemFormSet = forms.inlineformset_factory(queryset.model,
                                                  through_field.through,
                                                  fields=(m2m,),
                                                  can_delete=False,
                                                  extra=10,)
    else:
        ItemFormSet = forms.formset_factory(ItemForm, max_num=1)
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
                    if m2m:
                        through_instance = getattr(parent, parent_field)
                        if request.POST['removal'] == 'True':
                            through_instance.remove(child[m2m])
                        else:
                            through_instance.add(child[m2m])
                    else:
                        setattr(parent, parent_field, child['item'])
                        parent.save()

            # Return with informative success message and counts
            message = create_success_message(queryset.model,
                                             queryset.count(),
                                             child_model,
                                             len(data),
                                             request.POST['removal'] == 'True')
            messages.success(request, message)
            return HttpResponseRedirect(request.get_full_path())
        else:
            messages.error(request, "See below for errors in the form.")
    # . . .otherwise, create empty formset.
    else:
        item_formset = ItemFormSet()
        # sel_act = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        # item_formset = ItemForm(initial={'_selected_action': sel_act})

    return render(request,
                  'admin/change_items_intermediate.html',
                  {'calling_function': calling_function,
                   'parent_queryset': queryset,
                   'item_formset': item_formset,
                   'parent_model': queryset.model,
                   'child_model': child_model,
                   'is_m2m': bool(m2m is not None),
                   'is_removal': remove, })


def publish_items(request, queryset):
    rows_updated = queryset.update(published_date=timezone.now())
    message = quantify(rows_updated, queryset.model)
    messages.success(request, '{} successfully published.'.format(message))


def remove_items(request, queryset, parent_field, calling_function):
    through_field = getattr(queryset.model, parent_field)
    child_model = through_field.field.related_model
    for parent in queryset:
        setattr(parent, parent_field, None)
        parent.save()
    message = create_success_message(queryset.model, queryset.count(),
                                     child_model, 1, True)
    messages.success(request, message)
