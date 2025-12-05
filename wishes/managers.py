from django.db import models
from django.utils import timezone


class BirthdayManager(models.Manager):
    """Custom manager for birthday-related queries"""

    def get_upcoming_birthdays(self, days=30):
        """Get birthdays within the next 'days' days"""
        today = timezone.now().date()
        upcoming = []

        profiles = self.exclude(birthday__isnull=True)

        for profile in profiles:
            if profile.birthday:
                next_birthday = profile.get_next_birthday()
                if next_birthday and (next_birthday - today).days <= days:
                    upcoming.append(profile)

        return sorted(upcoming, key=lambda x: x.get_next_birthday())

    def get_today_birthdays(self):
        """Get all birthdays that occur today"""
        today = timezone.now().date()
        return self.filter(
            birthday__month=today.month,
            birthday__day=today.day
        )

    def get_this_month_birthdays(self):
        """Get all birthdays in the current month"""
        today = timezone.now().date()
        return self.filter(birthday__month=today.month)

    def get_by_age_range(self, min_age=None, max_age=None):
        """Filter profiles by age range"""
        today = timezone.now().date()
        profiles = []

        for profile in self.exclude(birthday__isnull=True):
            age = profile.get_age()
            if age:
                if min_age and max_age:
                    if min_age <= age <= max_age:
                        profiles.append(profile)
                elif min_age:
                    if age >= min_age:
                        profiles.append(profile)
                elif max_age:
                    if age <= max_age:
                        profiles.append(profile)

        return profiles


class WishManager(models.Manager):
    """Custom manager for birthday wishes"""

    def get_sent_wishes(self):
        """Get all sent wishes"""
        return self.filter(status='sent')

    def get_scheduled_wishes(self):
        """Get all scheduled wishes"""
        return self.filter(status='scheduled')

    def get_pending_wishes(self):
        """Get wishes scheduled for today or past"""
        now = timezone.now()
        return self.filter(
            status='scheduled',
            scheduled_date__lte=now
        )

    def get_user_sent_wishes(self, user):
        """Get wishes sent by a specific user"""
        return self.filter(sender=user, status='sent')

    def get_user_received_wishes(self, user):
        """Get wishes received by a specific user"""
        return self.filter(recipient=user, status='sent')

    def get_public_wishes(self):
        """Get all public wishes"""
        return self.filter(is_public=True, status='sent')
