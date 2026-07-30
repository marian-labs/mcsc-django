from django import forms
from .models import Grievance

class GrievanceForm(forms.ModelForm):
    class Meta:
        model = Grievance
        fields = ['title', 'category', 'description', 'attachment']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full rounded-lg border-outline-variant bg-surface-bright focus:border-primary focus:ring-2 focus:ring-primary-fixed/50 font-body-md text-body-md text-on-surface py-2.5 px-3',
                'placeholder': 'Briefly describe the issue'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full rounded-lg border-outline-variant bg-surface-bright focus:border-primary focus:ring-2 focus:ring-primary-fixed/50 font-body-md text-body-md text-on-surface py-2.5 px-3'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full rounded-lg border-outline-variant bg-surface-bright focus:border-primary focus:ring-2 focus:ring-primary-fixed/50 font-body-md text-body-md text-on-surface py-2.5 px-3 resize-none',
                'placeholder': 'Provide as much detail as possible to help us address the issue.',
                'rows': 4
            }),
            'attachment': forms.ClearableFileInput(attrs={
                'class': 'sr-only',
                'id': 'file-upload'
            })
        }
