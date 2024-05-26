# djangoProject/Form.py
from django import forms


class ImageUploadForm(forms.ModelForm):
    class Meta:
        fields = ['image']
