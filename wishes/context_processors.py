from django.utils import timezone
from .models import UserProfile


def birthday_context(request):
    """Add birthday-related context to all templates"""
    context = {}

    if request.user.is_authenticated:
        # Get upcoming birthdays count
        upcoming = UserProfile.objects.get_upcoming_birthdays(days=7)
        context['upcoming_birthdays_count'] = len(upcoming)

        # Get today's birthdays
        today_birthdays = UserProfile.objects.get_today_birthdays()
        context['today_birthdays'] = today_birthdays
        context['today_birthdays_count'] = today_birthdays.count()

    return context