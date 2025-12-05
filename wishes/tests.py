from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta
from .models import (
    UserProfile, BirthdayWish, GroupWish,
    GiftSuggestion, CalendarEvent
)


class UserProfileModelTest(TestCase):
    """Test cases for UserProfile model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            birthday=datetime(1990, 5, 15).date()
        )

    def test_profile_creation(self):
        """Test that profile is created correctly"""
        self.assertEqual(self.profile.user.username, 'testuser')
        self.assertIsNotNone(self.profile.birthday)

    def test_get_age(self):
        """Test age calculation"""
        age = self.profile.get_age()
        self.assertIsNotNone(age)
        self.assertGreater(age, 0)

    def test_get_next_birthday(self):
        """Test next birthday calculation"""
        next_birthday = self.profile.get_next_birthday()
        self.assertIsNotNone(next_birthday)
        self.assertGreaterEqual(next_birthday, timezone.now().date())


class BirthdayWishModelTest(TestCase):
    """Test cases for BirthdayWish model"""

    def setUp(self):
        self.sender = User.objects.create_user(
            username='sender',
            password='pass123'
        )
        self.recipient = User.objects.create_user(
            username='recipient',
            password='pass123'
        )

    def test_wish_creation(self):
        """Test creating a birthday wish"""
        wish = BirthdayWish.objects.create(
            sender=self.sender,
            recipient=self.recipient,
            wish_type='text',
            text_content='Happy Birthday!',
            status='draft'
        )
        self.assertEqual(wish.sender, self.sender)
        self.assertEqual(wish.recipient, self.recipient)
        self.assertEqual(wish.status, 'draft')

    def test_mark_as_sent(self):
        """Test marking wish as sent"""
        wish = BirthdayWish.objects.create(
            sender=self.sender,
            recipient=self.recipient,
            text_content='Happy Birthday!',
            status='draft'
        )
        wish.mark_as_sent()
        self.assertEqual(wish.status, 'sent')
        self.assertIsNotNone(wish.sent_date)


class ViewsTestCase(TestCase):
    """Test cases for views"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_index_view(self):
        """Test homepage loads correctly"""
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

    def test_dashboard_requires_login(self):
        """Test dashboard requires authentication"""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_dashboard_authenticated(self):
        """Test dashboard loads for authenticated users"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')

    def test_create_wish_view(self):
        """Test create wish page"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('create_wish'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_wish.html')


class GiftSuggestionModelTest(TestCase):
    """Test cases for GiftSuggestion model"""

    def test_gift_creation(self):
        """Test creating a gift suggestion"""
        gift = GiftSuggestion.objects.create(
            title='Smartwatch',
            description='A modern smartwatch',
            category='electronics',
            price_range='$100-$200',
            age_group='20-30',
            gender_preference='unisex'
        )
        self.assertEqual(gift.title, 'Smartwatch')
        self.assertEqual(gift.category, 'electronics')
