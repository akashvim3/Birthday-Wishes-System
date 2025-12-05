from rest_framework import serializers
from wishes.models import (
    UserProfile, BirthdayWish, GroupWish,
    GiftSuggestion, CalendarEvent
)
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model"""
    user = UserSerializer(read_only=True)
    age = serializers.IntegerField(source='get_age', read_only=True)
    next_birthday = serializers.DateField(source='get_next_birthday', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'birthday', 'profile_picture',
                  'phone_number', 'bio', 'age', 'next_birthday',
                  'timezone', 'created_at']
        read_only_fields = ['id', 'created_at']


class BirthdayWishSerializer(serializers.ModelSerializer):
    """Serializer for BirthdayWish model"""
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    recipient_name = serializers.CharField(source='recipient.username', read_only=True)

    class Meta:
        model = BirthdayWish
        fields = ['id', 'sender', 'sender_name', 'recipient',
                  'recipient_name', 'wish_type', 'text_content',
                  'voice_message', 'status', 'scheduled_date',
                  'is_public', 'is_anonymous', 'likes_count',
                  'views_count', 'created_at']
        read_only_fields = ['id', 'sender', 'likes_count',
                            'views_count', 'created_at']


class GiftSuggestionSerializer(serializers.ModelSerializer):
    """Serializer for GiftSuggestion model"""

    class Meta:
        model = GiftSuggestion
        fields = ['id', 'title', 'description', 'category',
                  'price_range', 'image', 'product_url',
                  'age_group', 'gender_preference', 'interests',
                  'popularity_score', 'is_featured']
        read_only_fields = ['id', 'popularity_score']


class GroupWishSerializer(serializers.ModelSerializer):
    """Serializer for GroupWish model"""
    creator_name = serializers.CharField(source='creator.username', read_only=True)
    recipient_name = serializers.CharField(source='recipient.username', read_only=True)
    contributor_count = serializers.IntegerField(
        source='contributors.count',
        read_only=True
    )

    class Meta:
        model = GroupWish
        fields = ['id', 'title', 'recipient', 'recipient_name',
                  'creator', 'creator_name', 'description',
                  'deadline', 'scheduled_send_date', 'is_active',
                  'is_sent', 'invitation_code', 'contributor_count',
                  'created_at']
        read_only_fields = ['id', 'creator', 'invitation_code',
                            'is_sent', 'created_at']
