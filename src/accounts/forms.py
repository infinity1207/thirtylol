# -*- coding: utf-8 -*-

from django import forms
from .models import UserProfile

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['mugshot']