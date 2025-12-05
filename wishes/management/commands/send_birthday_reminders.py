from django.core.management.base import BaseCommand
from django.utils import timezone
from wishes.models import UserProfile
from wishes.utils import send_birthday_notification


class Command(BaseCommand):
    help = 'Send birthday reminders for upcoming birthdays'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=1,
            help='Number of days in advance to send reminders (default: 1)'
        )

    def handle(self, *args, **options):
        days = options['days']
        self.stdout.write(f'Checking for birthdays in the next {days} days...')

        profiles = UserProfile.objects.get_upcoming_birthdays(days=days)

        count = 0
        for profile in profiles:
            next_birthday = profile.get_next_birthday()
            days_until = (next_birthday - timezone.now().date()).days

            if days_until <= days:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Birthday reminder: {profile.user.username} - {days_until} days'
                    )
                )
                count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Successfully processed {count} birthday reminders'))
