from django import forms
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from .models import Grievance

ALLOWED_EXTENSIONS = ['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'webp', 'txt', 'zip', 'rar']
MAX_FILE_SIZE = 3 * 1024 * 1024  # 3 MB

class GrievanceForm(forms.ModelForm):
    attachment = forms.FileField(
        required=False,
        validators=[FileExtensionValidator(allowed_extensions=ALLOWED_EXTENSIONS)],
        widget=forms.ClearableFileInput(attrs={
            'class': 'sr-only',
            'id': 'file-upload'
        })
    )

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
        }

    def clean_attachment(self):
        attachment = self.cleaned_data.get('attachment')
        if attachment:
            if attachment.size > MAX_FILE_SIZE:
                raise ValidationError("File size must not exceed 3 MB.")
        return attachment
