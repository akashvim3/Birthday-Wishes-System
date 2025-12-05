from datetime import datetime

from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def days_until(date):
    """Calculate days until a given date"""
    if not date:
        return None

    today = timezone.now().date()
    if isinstance(date, datetime):
        date = date.date()

    delta = date - today
    return delta.days


@register.filter
def birthday_age(birthday):
    """Calculate age from birthday"""
    if not birthday:
        return None

    today = timezone.now().date()
    age = today.year - birthday.year

    if (today.month, today.day) < (birthday.month, birthday.day):
        age -= 1

    return age


@register.simple_tag
def wish_count(user):
    """Get total wishes sent by user"""
    from wishes.models import BirthdayWish
    return BirthdayWish.objects.filter(sender=user, status='sent').count()


@register.simple_tag
def received_wish_count(user):
    """Get total wishes received by user"""
    from wishes.models import BirthdayWish
    return BirthdayWish.objects.filter(recipient=user, status='sent').count()


@register.inclusion_tag('wishes/components/upcoming_birthday_card.html')
def show_upcoming_birthdays(limit=5):
    """Display upcoming birthdays widget"""
    from wishes.models import UserProfile

    upcoming = UserProfile.objects.get_upcoming_birthdays(days=30)[:limit]
    return {'birthdays': upcoming}


@register.filter
def get_item(dictionary, key):
    """Get item from dictionary"""
    return dictionary.get(key)
