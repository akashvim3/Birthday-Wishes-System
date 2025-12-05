from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Q
from .models import (
    UserProfile, BirthdayWish, GroupWish, GroupWishContribution,
    GiftSuggestion, CalendarEvent, ChatMessage, WishTemplate
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Custom admin for user profiles"""
    list_display = ['user', 'birthday', 'get_age', 'phone_number', 'created_at']
    list_filter = ['created_at', 'timezone']
    search_fields = ['user__username', 'user__email', 'phone_number']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('User Information', {
            'fields': ('user', 'birthday', 'profile_picture')
        }),
        ('Contact Details', {
            'fields': ('phone_number', 'bio', 'timezone')
        }),
        ('Preferences', {
            'fields': ('notification_preferences',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_age(self, obj):
        age = obj.get_age()
        return age if age else 'N/A'

    get_age.short_description = 'Age'


@admin.register(BirthdayWish)
class BirthdayWishAdmin(admin.ModelAdmin):
    """Custom admin for birthday wishes"""
    list_display = ['id_display', 'sender', 'recipient', 'wish_type', 'status',
                    'scheduled_date', 'is_public', 'views_count', 'likes_count']
    list_filter = ['wish_type', 'status', 'is_public', 'created_at']
    search_fields = ['sender__username', 'recipient__username', 'text_content']
    readonly_fields = ['id', 'created_at', 'updated_at', 'sent_date', 'views_count', 'likes_count']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'sender', 'recipient', 'wish_type', 'status')
        }),
        ('Content', {
            'fields': ('text_content', 'voice_message', 'video_message', 'card_template')
        }),
        ('Scheduling', {
            'fields': ('scheduled_date', 'sent_date')
        }),
        ('Settings', {
            'fields': ('is_public', 'is_anonymous')
        }),
        ('Engagement', {
            'fields': ('likes_count', 'views_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def id_display(self, obj):
        return str(obj.id)[:8]

    id_display.short_description = 'ID'

    actions = ['mark_as_sent', 'mark_as_scheduled']

    def mark_as_sent(self, request, queryset):
        updated = queryset.update(status='sent')
        self.message_user(request, f'{updated} wishes marked as sent.')

    mark_as_sent.short_description = 'Mark selected wishes as sent'

    def mark_as_scheduled(self, request, queryset):
        updated = queryset.update(status='scheduled')
        self.message_user(request, f'{updated} wishes marked as scheduled.')

    mark_as_scheduled.short_description = 'Mark selected wishes as scheduled'


@admin.register(GroupWish)
class GroupWishAdmin(admin.ModelAdmin):
    """Custom admin for group wishes"""
    list_display = ['title', 'recipient', 'creator', 'contributor_count',
                    'deadline', 'is_active', 'is_sent', 'invitation_code']
    list_filter = ['is_active', 'is_sent', 'created_at']
    search_fields = ['title', 'recipient__username', 'creator__username', 'invitation_code']
    readonly_fields = ['id', 'invitation_code', 'created_at', 'updated_at']
    filter_horizontal = ['contributors']

    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'title', 'recipient', 'creator', 'description')
        }),
        ('Scheduling', {
            'fields': ('deadline', 'scheduled_send_date')
        }),
        ('Settings', {
            'fields': ('is_active', 'is_sent', 'allow_anonymous_contributions')
        }),
        ('Invitation', {
            'fields': ('invitation_code',)
        }),
        ('Contributors', {
            'fields': ('contributors',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def contributor_count(self, obj):
        return obj.contributors.count()

    contributor_count.short_description = 'Contributors'


@admin.register(GroupWishContribution)
class GroupWishContributionAdmin(admin.ModelAdmin):
    """Custom admin for group wish contributions"""
    list_display = ['group_wish', 'contributor', 'is_anonymous', 'created_at']
    list_filter = ['is_anonymous', 'created_at']
    search_fields = ['group_wish__title', 'contributor__username', 'text_content']
    readonly_fields = ['created_at']


@admin.register(GiftSuggestion)
class GiftSuggestionAdmin(admin.ModelAdmin):
    """Custom admin for gift suggestions"""
    list_display = ['title', 'category', 'price_range', 'popularity_score',
                    'is_featured', 'age_group', 'gender_preference']
    list_filter = ['category', 'is_featured', 'gender_preference', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'category', 'price_range', 'image')
        }),
        ('Links', {
            'fields': ('product_url',)
        }),
        ('Target Audience', {
            'fields': ('age_group', 'gender_preference', 'interests')
        }),
        ('Settings', {
            'fields': ('popularity_score', 'is_featured')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_as_featured', 'unmark_as_featured']

    def mark_as_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} gifts marked as featured.')

    mark_as_featured.short_description = 'Mark as featured'

    def unmark_as_featured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} gifts unmarked as featured.')

    unmark_as_featured.short_description = 'Remove from featured'


@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    """Custom admin for calendar events"""
    list_display = ['event_title', 'user', 'birthday_person', 'event_date',
                    'is_reminder_sent', 'created_at']
    list_filter = ['is_reminder_sent', 'event_date', 'created_at']
    search_fields = ['event_title', 'user__username', 'notes']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'event_date'

    fieldsets = (
        ('Event Information', {
            'fields': ('user', 'birthday_person', 'event_title', 'event_date')
        }),
        ('Details', {
            'fields': ('notes', 'location')
        }),
        ('Reminder', {
            'fields': ('reminder_time', 'is_reminder_sent')
        }),
        ('Integration', {
            'fields': ('google_calendar_event_id',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """Custom admin for chatbot messages"""
    list_display = ['user', 'message_preview', 'response_preview', 'timestamp']
    list_filter = ['timestamp']
    search_fields = ['user__username', 'message', 'response']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'

    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message

    message_preview.short_description = 'Message'

    def response_preview(self, obj):
        return obj.response[:50] + '...' if len(obj.response) > 50 else obj.response

    response_preview.short_description = 'Response'


@admin.register(WishTemplate)
class WishTemplateAdmin(admin.ModelAdmin):
    """Custom admin for wish templates"""
    list_display = ['title', 'occasion', 'category', 'is_premium', 'usage_count', 'created_at']
    list_filter = ['occasion', 'is_premium', 'category', 'created_at']
    search_fields = ['title', 'content']
    readonly_fields = ['usage_count', 'created_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'occasion', 'category')
        }),
        ('Content', {
            'fields': ('content',)
        }),
        ('Settings', {
            'fields': ('is_premium', 'usage_count')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


# Customize admin site
admin.site.site_header = "Birthday Wishes Pro Admin"
admin.site.site_title = "Birthday Wishes Admin"
admin.site.index_title = "Welcome to Birthday Wishes Pro Administration"
