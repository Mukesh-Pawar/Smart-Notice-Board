from django import forms
from django.utils import timezone

from .models import Notice
from .services import DURATION_OPTIONS


class NoticeForm(forms.ModelForm):
    duration = forms.ChoiceField(choices=[
        ('1h', '1 hour'), ('6h', '6 hours'), ('12h', '12 hours'),
        ('24h', '24 hours'), ('2d', '2 days'), ('7d', '7 days'), ('custom', 'Custom duration'),
    ], initial='24h')
    custom_duration_minutes = forms.IntegerField(required=False, min_value=1, max_value=10080, label='Custom duration (minutes)')

    class Meta:
        model = Notice
        fields = ['title', 'message', 'priority', 'start_time']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'e.g. Practical Examination Schedule'}),
            'message': forms.Textarea(attrs={'rows': 6, 'placeholder': 'Enter the notice message...'}),
            'priority': forms.Select(),
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            for key, minutes in DURATION_OPTIONS.items():
                if self.instance.duration_minutes == minutes:
                    self.fields['duration'].initial = key
                    break
            else:
                self.fields['duration'].initial = 'custom'
                self.fields['custom_duration_minutes'].initial = self.instance.duration_minutes
            if self.instance.start_time:
                local_dt = timezone.localtime(self.instance.start_time)
                self.fields['start_time'].initial = local_dt.strftime('%Y-%m-%dT%H:%M')

    def clean(self):
        cleaned = super().clean()
        duration = cleaned.get('duration')
        if duration == 'custom':
            minutes = cleaned.get('custom_duration_minutes')
            if not minutes:
                self.add_error('custom_duration_minutes', 'Enter a custom duration.')
            cleaned['duration_minutes'] = minutes
        elif duration:
            cleaned['duration_minutes'] = DURATION_OPTIONS[duration]
        start = cleaned.get('start_time')
        if start and start < timezone.now() - timezone.timedelta(minutes=1):
            # Allow small clock differences but do not allow clearly stale schedules.
            self.add_error('start_time', 'Start time cannot be in the past.')
        return cleaned

    def get_duration_minutes(self):
        return self.cleaned_data['duration_minutes']
