from django import forms
from django.conf import settings

from ckeditor.widgets import CKEditorWidget

from toolsettings.forms import UserSelectWidget

from ..models import Job


class JobForm(forms.ModelForm):
    class Meta:
        model = Job

        # note: change also below in JobDuplicateForm
        exclude = ['name', 'description', 'event', 'coordinators',
                   'badge_defaults', 'archived_number_coordinators',
                   'order', ]
        widgets = {
            'job_admins': UserSelectWidget,
        }

        # According to the documentation django-modeltranslations copies the
        # widget from the original field.
        # But when setting BLEACH_DEFAULT_WIDGET this does not happen.
        # Therefore set it manually...
        for lang, name in settings.LANGUAGES:
            widgets["description_{}".format(lang)] = CKEditorWidget()

    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event')

        super(JobForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(JobForm, self).save(False)  # event is missing

        # add event
        instance.event = self.event

        if commit:
            instance.save()

        self.save_m2m()  # save m2m, otherwise job_admins is lost

        return instance


class JobDeleteForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = []

    def delete(self):
        self.instance.delete()


class JobDuplicateForm(JobForm):
    def __init__(self, *args, **kwargs):
        self.other_job = kwargs.pop('other_job')
        kwargs['event'] = self.other_job.event
        super(JobDuplicateForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        super(JobDuplicateForm, self).save(commit=True)  # we have to save

        for shift in self.other_job.shift_set.all():
            new_shift = shift
            new_shift.pk = None
            new_shift.job = self.instance
            new_shift.save()


class JobSortForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self._event = kwargs.pop('event')

        super().__init__(*args, **kwargs)

        counter = self._event.job_set.count()
        for job in self._event.job_set.all():
            field_id = 'order_job_%s' % job.pk

            self.fields[field_id] = forms.IntegerField(min_value=0, initial=counter)
            self.fields[field_id].widget = forms.HiddenInput()

            counter -= 1

    def save(self):
        cleaned_data = super().clean()

        for job in self._event.job_set.all():
            field_id = 'order_job_%s' % job.pk
            job.order = cleaned_data.get(field_id)
            print("!!!" + str(job.pk) + " " + str(job.order))
            job.save()