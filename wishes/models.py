from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
import uuid


class BirthdayManager(models.Manager):
    """Custom manager for birthday-related queries"""

    def get_upcoming_birthdays(self, days=30):
        """Get birthdays within the next 'days' days"""
        today = timezone.now().date()
        upcoming = []

        profiles = self.all()
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


class UserProfile(models.Model):
    """Extended user profile with birthday information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    birthday = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    notification_preferences = models.JSONField(default=dict)
    timezone = models.CharField(max_length=50, default='UTC')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = BirthdayManager()

    class Meta:
        ordering = ['user__username']
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def get_next_birthday(self):
        """Calculate the next birthday date"""
        if not self.birthday:
            return None

        today = timezone.now().date()
        next_birthday = self.birthday.replace(year=today.year)

        if next_birthday < today:
            next_birthday = next_birthday.replace(year=today.year + 1)

        return next_birthday

    def get_age(self):
        """Calculate current age"""
        if not self.birthday:
            return None

        today = timezone.now().date()
        age = today.year - self.birthday.year

        if (today.month, today.day) < (self.birthday.month, self.birthday.day):
            age -= 1

        return age


class BirthdayWish(models.Model):
    """Main wish model with various types of wishes"""

    WISH_TYPE_CHOICES = [
        ('text', 'Text Message'),
        ('voice', 'Voice Message'),
        ('video', 'Video Message'),
        ('card', 'Digital Card'),
        ('group', 'Group Wish'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_wishes')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_wishes')
    wish_type = models.CharField(max_length=10, choices=WISH_TYPE_CHOICES, default='text')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')

    # Content fields
    text_content = models.TextField(blank=True)
    voice_message = models.FileField(upload_to='voice_messages/', null=True, blank=True)
    video_message = models.FileField(upload_to='video_messages/', null=True, blank=True)
    card_template = models.CharField(max_length=50, blank=True)

    # Scheduling
    scheduled_date = models.DateTimeField(null=True, blank=True)
    sent_date = models.DateTimeField(null=True, blank=True)

    # Metadata
    is_public = models.BooleanField(default=False)
    is_anonymous = models.BooleanField(default=False)
    likes_count = models.IntegerField(default=0)
    views_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Birthday Wish'
        verbose_name_plural = 'Birthday Wishes'
        indexes = [
            models.Index(fields=['recipient', 'status']),
            models.Index(fields=['scheduled_date']),
        ]

    def __str__(self):
        return f"Wish from {self.sender.username} to {self.recipient.username}"

    def mark_as_sent(self):
        """Mark wish as sent"""
        self.status = 'sent'
        self.sent_date = timezone.now()
        self.save()


class GroupWish(models.Model):
    """Group wishes where multiple people contribute"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_wishes_received')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_wishes_created')
    contributors = models.ManyToManyField(User, through='GroupWishContribution', related_name='contributed_wishes')

    description = models.TextField(blank=True)
    deadline = models.DateTimeField()
    scheduled_send_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    is_sent = models.BooleanField(default=False)

    invitation_code = models.CharField(max_length=12, unique=True)
    allow_anonymous_contributions = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Group Wish'
        verbose_name_plural = 'Group Wishes'

    def __str__(self):
        return f"Group Wish: {self.title}"

    def generate_invitation_code(self):
        """Generate unique invitation code"""
        import random
        import string

        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
        while GroupWish.objects.filter(invitation_code=code).exists():
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

        self.invitation_code = code
        self.save()


class GroupWishContribution(models.Model):
    """Individual contributions to group wishes"""
    group_wish = models.ForeignKey(GroupWish, on_delete=models.CASCADE, related_name='contributions')
    contributor = models.ForeignKey(User, on_delete=models.CASCADE)

    text_content = models.TextField(blank=True)
    voice_message = models.FileField(upload_to='group_voice_messages/', null=True, blank=True)
    is_anonymous = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['group_wish', 'contributor']
        ordering = ['created_at']

    def __str__(self):
        return f"{self.contributor.username}'s contribution to {self.group_wish.title}"


class GiftSuggestion(models.Model):
    """Gift suggestions and recommendations"""

    CATEGORY_CHOICES = [
        ('electronics', 'Electronics'),
        ('books', 'Books'),
        ('fashion', 'Fashion & Accessories'),
        ('home', 'Home & Living'),
        ('sports', 'Sports & Outdoors'),
        ('beauty', 'Beauty & Personal Care'),
        ('toys', 'Toys & Games'),
        ('food', 'Food & Beverages'),
        ('experience', 'Experiences'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    price_range = models.CharField(max_length=50)
    image = models.ImageField(upload_to='gift_images/', null=True, blank=True)
    product_url = models.URLField(blank=True)

    age_group = models.CharField(max_length=20, blank=True)  # e.g., "20-30", "30-40"
    gender_preference = models.CharField(max_length=10, blank=True)  # male, female, unisex
    interests = models.JSONField(default=list)  # List of interest tags

    popularity_score = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-popularity_score', '-created_at']
        verbose_name = 'Gift Suggestion'
        verbose_name_plural = 'Gift Suggestions'

    def __str__(self):
        return self.title


class CalendarEvent(models.Model):
    """Birthday calendar events"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='calendar_events')
    birthday_person = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    event_title = models.CharField(max_length=200)
    event_date = models.DateTimeField()
    reminder_time = models.DateTimeField(null=True, blank=True)

    notes = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)

    is_reminder_sent = models.BooleanField(default=False)
    google_calendar_event_id = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['event_date']
        verbose_name = 'Calendar Event'
        verbose_name_plural = 'Calendar Events'

    def __str__(self):
        return f"{self.event_title} - {self.event_date}"


class ChatMessage(models.Model):
    """Chatbot conversation history"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages')
    message = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=100)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Chat with {self.user.username} at {self.timestamp}"


class WishTemplate(models.Model):
    """Pre-made wish templates"""

    OCCASION_CHOICES = [
        ('birthday', 'Birthday'),
        ('milestone', 'Milestone Birthday'),
        ('belated', 'Belated Birthday'),
        ('surprise', 'Surprise Birthday'),
    ]

    title = models.CharField(max_length=100)
    occasion = models.CharField(max_length=20, choices=OCCASION_CHOICES, default='birthday')
    content = models.TextField()
    category = models.CharField(max_length=50)  # funny, heartfelt, professional, etc.

    is_premium = models.BooleanField(default=False)
    usage_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-usage_count', 'title']

    def __str__(self):
        return self.title
