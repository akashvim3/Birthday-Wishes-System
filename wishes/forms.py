from django import forms
from django.contrib.auth.models import User
from .models import (
    UserProfile, BirthdayWish, GroupWish, GroupWishContribution,
    CalendarEvent, WishTemplate
)
from datetime import datetime, timedelta


class UserProfileForm(forms.ModelForm):
    """User profile form with birthday and preferences"""

    class Meta:
        model = UserProfile
        fields = ['birthday', 'profile_picture', 'phone_number', 'bio', 'timezone']
        widgets = {
            'birthday': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500',
                'placeholder': '+1 (555) 123-4567'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500',
                'rows': 4,
                'placeholder': 'Tell us about yourself...'
            }),
            'timezone': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500'
            }),
        }


class BirthdayWishForm(forms.ModelForm):
    """Form for creating birthday wishes"""

    recipient = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500'
        })
    )

    class Meta:
        model = BirthdayWish
        fields = ['recipient', 'wish_type', 'text_content', 'card_template',
                  'scheduled_date', 'is_public', 'is_anonymous']
        widgets = {
            'wish_type': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500'
            }),
            'text_content': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500',
                'rows': 6,
                'placeholder': 'Write your heartfelt birthday wish here...'
            }),
            'card_template': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500'
            }),
            'scheduled_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-5 w-5 text-purple-600'
            }),
            'is_anonymous': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-5 w-5 text-purple-600'
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            # Exclude the current user from recipient choices
            self.fields['recipient'].queryset = User.objects.exclude(id=user.id)


class GroupWishForm(forms.ModelForm):
    """Form for creating group wishes"""

    class Meta:
        model = GroupWish
        fields = ['title', 'recipient', 'description', 'deadline',
                  'scheduled_send_date', 'allow_anonymous_contributions']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500',
                'placeholder': 'e.g., Birthday Surprise for John'
            }),
            'recipient': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500',
                'rows': 4,
                'placeholder': 'Describe what this group wish is about...'
            }),
            'deadline': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500'
            }),
            'scheduled_send_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500'
            }),
            'allow_anonymous_contributions': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-5 w-5 text-purple-600'
            }),
        }


class VoiceMessageForm(forms.Form):
    """Form for voice message upload"""
    voice_recording = forms.FileField(
        widget=forms.FileInput(attrs={
            'accept': 'audio/*',
            'class': 'hidden'
        })
    )


class CalendarEventForm(forms.ModelForm):
    """Form for creating calendar events"""

    class Meta:
        model = CalendarEvent
        fields = ['birthday_person', 'event_title', 'event_date',
                  'reminder_time', 'notes', 'location']
        widgets = {
            'birthday_person': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500'
            }),
            'event_title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500',
                'placeholder': 'Birthday Party'
            }),
            'event_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500'
            }),
            'reminder_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500',
                'rows': 3,
                'placeholder': 'Add any notes about the event...'
            }),
            'location': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500',
                'placeholder': 'Event location'
            }),
        }
