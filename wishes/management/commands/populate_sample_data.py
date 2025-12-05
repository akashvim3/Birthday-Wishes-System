from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from wishes.models import UserProfile, GiftSuggestion, WishTemplate
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = 'Populate database with sample data for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')

        # Create sample users
        self.create_sample_users()

        # Create gift suggestions
        self.create_gift_suggestions()

        # Create wish templates
        self.create_wish_templates()

        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))

    def create_sample_users(self):
        """Create sample users with profiles"""
        users_data = [
            ('john_doe', 'john@example.com', 'John', 'Doe', datetime(1990, 3, 15)),
            ('jane_smith', 'jane@example.com', 'Jane', 'Smith', datetime(1992, 7, 22)),
            ('bob_wilson', 'bob@example.com', 'Bob', 'Wilson', datetime(1988, 11, 5)),
        ]

        for username, email, first_name, last_name, birthday in users_data:
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password='password123',
                    first_name=first_name,
                    last_name=last_name
                )

                UserProfile.objects.update_or_create(
                    user=user,
                    defaults={'birthday': birthday.date()}
                )

                self.stdout.write(f'Created user: {username}')

    def create_gift_suggestions(self):
        """Create sample gift suggestions"""
        gifts = [
            {
                'title': 'Wireless Headphones',
                'description': 'Premium noise-cancelling wireless headphones',
                'category': 'electronics',
                'price_range': '$150-$300',
                'age_group': '18-35',
                'gender_preference': 'unisex'
            },
            {
                'title': 'Bestseller Novel',
                'description': 'Latest bestselling fiction novel',
                'category': 'books',
                'price_range': '$15-$30',
                'age_group': '25-60',
                'gender_preference': 'unisex'
            },
            {
                'title': 'Smartwatch',
                'description': 'Feature-rich fitness tracking smartwatch',
                'category': 'electronics',
                'price_range': '$200-$400',
                'age_group': '20-50',
                'gender_preference': 'unisex'
            },
        ]

        for gift_data in gifts:
            GiftSuggestion.objects.get_or_create(
                title=gift_data['title'],
                defaults=gift_data
            )

        self.stdout.write(f'Created {len(gifts)} gift suggestions')

    def create_wish_templates(self):
        """Create sample wish templates"""
        templates = [
            {
                'title': 'Heartfelt Birthday Wish',
                'occasion': 'birthday',
                'category': 'heartfelt',
                'content': 'Wishing you a day filled with love, laughter, and all the happiness your heart can hold. Happy Birthday!'
            },
            {
                'title': 'Funny Birthday Wish',
                'occasion': 'birthday',
                'category': 'funny',
                'content': "You're not getting older, you're just becoming a classic! Happy Birthday! 🎂"
            },
            {
                'title': 'Professional Birthday Wish',
                'occasion': 'birthday',
                'category': 'professional',
                'content': 'Wishing you continued success and happiness on your special day. Happy Birthday!'
            },
        ]

        for template_data in templates:
            WishTemplate.objects.get_or_create(
                title=template_data['title'],
                defaults=template_data
            )

        self.stdout.write(f'Created {len(templates)} wish templates')
