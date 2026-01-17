from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
import uuid

from .models import (
    UserProfile, BirthdayWish, GroupWish, GroupWishContribution,
    GiftSuggestion, CalendarEvent, ChatMessage, WishTemplate
)


class ComprehensiveModelTests(TestCase):
    """Comprehensive tests for all models in the Birthday Wishes System"""

    def test_user_profile_model(self):
        """Test UserProfile model functionality"""
        print("Testing UserProfile model...")
        
        # Create a user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Test creating a profile
        profile = UserProfile.objects.create(
            user=user,
            birthday=datetime(1990, 5, 15).date()
        )
        
        self.assertEqual(profile.user.username, 'testuser')
        self.assertIsNotNone(profile.birthday)
        
        # Test age calculation
        age = profile.get_age()
        self.assertIsNotNone(age)
        self.assertGreater(age, 0)
        
        # Test next birthday calculation
        next_birthday = profile.get_next_birthday()
        self.assertIsNotNone(next_birthday)
        self.assertGreaterEqual(next_birthday, timezone.now().date())
        
        print(f"  ✓ UserProfile created with age {age}")

    def test_birthday_wish_model(self):
        """Test BirthdayWish model functionality"""
        print("Testing BirthdayWish model...")
        
        # Create users
        sender = User.objects.create_user(
            username='sender',
            password='pass123'
        )
        recipient = User.objects.create_user(
            username='recipient',
            password='pass123'
        )
        
        # Test creating a wish
        wish = BirthdayWish.objects.create(
            sender=sender,
            recipient=recipient,
            wish_type='text',
            text_content='Happy Birthday!',
            status='draft'
        )
        
        self.assertEqual(wish.sender, sender)
        self.assertEqual(wish.recipient, recipient)
        self.assertEqual(wish.status, 'draft')
        
        # Test mark as sent
        wish.mark_as_sent()
        self.assertEqual(wish.status, 'sent')
        self.assertIsNotNone(wish.sent_date)
        
        print(f"  ✓ BirthdayWish created and sent, ID: {str(wish.id)[:8]}")

    def test_group_wish_model(self):
        """Test GroupWish model functionality"""
        print("Testing GroupWish model...")
        
        # Create users
        creator = User.objects.create_user(
            username='creator',
            password='pass123'
        )
        recipient = User.objects.create_user(
            username='group_recipient',
            password='pass123'
        )
        
        # Test creating a group wish
        group_wish = GroupWish.objects.create(
            title='Test Group Wish',
            recipient=recipient,
            creator=creator,
            description='A test group wish',
            deadline=timezone.now() + timedelta(days=7),
            scheduled_send_date=timezone.now() + timedelta(days=8),
            allow_anonymous_contributions=False
        )
        
        # Generate invitation code
        group_wish.generate_invitation_code()
        
        self.assertEqual(group_wish.title, 'Test Group Wish')
        self.assertEqual(group_wish.recipient, recipient)
        self.assertEqual(group_wish.creator, creator)
        self.assertEqual(len(group_wish.invitation_code), 12)
        
        print(f"  ✓ GroupWish created with code: {group_wish.invitation_code}")

    def test_gift_suggestion_model(self):
        """Test GiftSuggestion model functionality"""
        print("Testing GiftSuggestion model...")
        
        # Test creating a gift suggestion
        gift = GiftSuggestion.objects.create(
            title='Smartwatch',
            description='A modern smartwatch',
            category='electronics',
            price_range='$100-$200',
            age_group='20-30',
            gender_preference='unisex',
            interests=['technology', 'fitness']
        )
        
        self.assertEqual(gift.title, 'Smartwatch')
        self.assertEqual(gift.category, 'electronics')
        self.assertIn('technology', gift.interests)
        
        print(f"  ✓ GiftSuggestion created: {gift.title}")

    def test_calendar_event_model(self):
        """Test CalendarEvent model functionality"""
        print("Testing CalendarEvent model...")
        
        # Create user and profile
        user = User.objects.create_user(
            username='cal_user',
            password='pass123'
        )
        profile = UserProfile.objects.create(
            user=user,
            birthday=datetime(1990, 5, 15).date()
        )
        
        # Test creating a calendar event
        event = CalendarEvent.objects.create(
            user=user,
            birthday_person=profile,
            event_title="Test Birthday",
            event_date=timezone.now() + timedelta(days=10),
            notes="Test event for birthday"
        )
        
        self.assertEqual(event.event_title, "Test Birthday")
        self.assertEqual(event.user, user)
        self.assertEqual(event.birthday_person, profile)
        
        print(f"  ✓ CalendarEvent created: {event.event_title}")

    def test_chat_message_model(self):
        """Test ChatMessage model functionality"""
        print("Testing ChatMessage model...")
        
        # Create user
        user = User.objects.create_user(
            username='chat_user',
            password='pass123'
        )
        
        # Test creating a chat message
        message = ChatMessage.objects.create(
            user=user,
            message='Hello, how do I write a birthday message?',
            response='Sure, I can help you write a personalized birthday message!',
            session_id='test_session_123'
        )
        
        self.assertEqual(message.user, user)
        self.assertIn('birthday', message.response.lower())
        
        print(f"  ✓ ChatMessage created with session: {message.session_id}")

    def test_wish_template_model(self):
        """Test WishTemplate model functionality"""
        print("Testing WishTemplate model...")
        
        # Test creating a wish template
        template = WishTemplate.objects.create(
            title='Happy Birthday Template',
            occasion='birthday',
            content='Wishing you a wonderful birthday filled with joy and happiness!',
            category='heartfelt'
        )
        
        self.assertEqual(template.title, 'Happy Birthday Template')
        self.assertEqual(template.occasion, 'birthday')
        self.assertIn('wonderful', template.content)
        
        print(f"  ✓ WishTemplate created: {template.title}")

    def test_user_profile_manager(self):
        """Test custom manager functionality"""
        print("Testing UserProfile custom manager...")
        
        # Create users and profiles
        user1 = User.objects.create_user(
            username='user1',
            password='pass123'
        )
        profile1 = UserProfile.objects.create(
            user=user1,
            birthday=datetime(1990, 5, 15).date()
        )
        
        user2 = User.objects.create_user(
            username='user2',
            password='pass123'
        )
        profile2 = UserProfile.objects.create(
            user=user2,
            birthday=datetime(1995, 6, 20).date()
        )
        
        # Test upcoming birthdays
        upcoming = UserProfile.objects.get_upcoming_birthdays(days=365)
        self.assertIn(profile1, upcoming)
        self.assertIn(profile2, upcoming)
        
        print("  ✓ Custom manager functionality tested")

    def test_birthday_wish_manager(self):
        """Test BirthdayWish custom manager functionality"""
        print("Testing BirthdayWish custom functionality...")
        
        sender = User.objects.create_user(
            username='sender_test',
            password='pass123'
        )
        recipient = User.objects.create_user(
            username='recipient_test',
            password='pass123'
        )
        
        # Create a wish
        wish = BirthdayWish.objects.create(
            sender=sender,
            recipient=recipient,
            text_content='Test content',
            status='sent'
        )
        
        # Test that the wish was created properly
        self.assertIsNotNone(wish.created_at)
        self.assertEqual(wish.text_content, 'Test content')
        
        print("  ✓ BirthdayWish functionality tested")


class URLTests(TestCase):
    """Test URL accessibility"""
    
    def test_homepage_accessibility(self):
        """Test that homepage loads correctly"""
        print("Testing homepage accessibility...")
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        print("  ✓ Homepage accessible")
    
    def test_dashboard_accessibility(self):
        """Test that dashboard redirects for unauthenticated users"""
        print("Testing dashboard accessibility...")
        response = self.client.get('/dashboard/')
        # Should redirect to login since user is not authenticated
        self.assertEqual(response.status_code, 302)
        print("  ✓ Dashboard properly redirects unauthenticated users")


class ViewTests(TestCase):
    """Test views functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_profile_view(self):
        """Test profile view"""
        print("Testing profile view...")
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, 200)
        print("  ✓ Profile view accessible")


def run_comprehensive_tests():
    """Run all tests and report results"""
    print("Starting comprehensive tests for Birthday Wishes System...\n")
    
    # Django test runner will handle this automatically when called with python manage.py test
    print("Tests will be run automatically by Django's test framework.")
    print("Run 'python manage.py test wishes.comprehensive_tests' to execute these tests.")