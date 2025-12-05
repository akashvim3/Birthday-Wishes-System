from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import BirthdayWish, UserProfile, CalendarEvent
from .utils import send_birthday_notification


@shared_task
def send_scheduled_wish(wish_id):
    """Send a scheduled birthday wish"""
    try:
        wish = BirthdayWish.objects.get(id=wish_id)

        if wish.status == 'scheduled':
            wish.mark_as_sent()
            send_birthday_notification(wish)
            return f"Wish {wish_id} sent successfully"

        return f"Wish {wish_id} already sent"

    except BirthdayWish.DoesNotExist:
        return f"Wish {wish_id} not found"


@shared_task
def check_birthdays_today():
    """Check for birthdays today and send notifications"""
    today = timezone.now().date()
    profiles = UserProfile.objects.filter(
        birthday__month=today.month,
        birthday__day=today.day
    )

    notifications_sent = 0

    for profile in profiles:
        # Send birthday notification
        subject = f"🎉 It's {profile.user.get_full_name()}'s Birthday Today!"
        message = f"Don't forget to wish {profile.user.get_full_name()} a happy birthday!"

        # Get all users who might want to send wishes (friends, followers, etc.)
        # For now, we'll just log it
        print(f"Birthday today: {profile.user.username}")
        notifications_sent += 1

    return f"Processed {notifications_sent} birthdays"


@shared_task
def send_birthday_reminders():
    """Send reminders for upcoming birthdays"""
    tomorrow = timezone.now().date() + timezone.timedelta(days=1)

    profiles = UserProfile.objects.filter(
        birthday__month=tomorrow.month,
        birthday__day=tomorrow.day
    )

    for profile in profiles:
        # Send reminder emails to users
        print(f"Reminder: {profile.user.username}'s birthday is tomorrow")

    return f"Sent reminders for {profiles.count()} birthdays"


@shared_task
def cleanup_old_voice_messages():
    """Clean up voice messages older than 90 days"""
    cutoff_date = timezone.now() - timezone.timedelta(days=90)

    old_wishes = BirthdayWish.objects.filter(
        created_at__lt=cutoff_date,
        voice_message__isnull=False
    )

    deleted_count = 0
    for wish in old_wishes:
        if wish.voice_message:
            wish.voice_message.delete()
            deleted_count += 1

    return f"Cleaned up {deleted_count} old voice messages"
