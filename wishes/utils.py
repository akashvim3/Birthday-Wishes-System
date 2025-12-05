from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
import random
import openai


def send_birthday_notification(wish):
    """Send birthday notification to recipient"""
    subject = f"🎉 Birthday Wish from {wish.sender.get_full_name() or wish.sender.username}"

    message = f"""
    You've received a birthday wish!

    From: {wish.sender.get_full_name() or wish.sender.username}
    Message: {wish.text_content}

    View your wish at: {settings.SITE_URL}/dashboard/

    Have a wonderful birthday!
    """

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [wish.recipient.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def schedule_birthday_wish(wish):
    """Schedule a birthday wish using Celery"""
    from .tasks import send_scheduled_wish

    if wish.scheduled_date:
        # Schedule the task
        send_scheduled_wish.apply_async(
            args=[wish.id],
            eta=wish.scheduled_date
        )
        return True
    return False


def generate_ai_wish(message, user):
    """Generate AI response for chatbot using OpenAI"""

    # Default responses for common queries
    responses = {
        'hello': "Hello! 👋 How can I help you create the perfect birthday wish today?",
        'help': "I can help you with: "
                "• Creating personalized birthday wish "
                "• Suggesting gift ideas"
                "• Scheduling birthday reminders"
                "• Group wish coordination"
                "What would you like to do?",
       'gift': "I'd love to help you find the perfect gift! What's the person's age range and interests?",
    'template': "We have many birthday wish templates! Would you like something funny, heartfelt, professional, or creative?",
    }

    message_lower = message.lower()

    # Check for keywords
    for keyword, response in responses.items():
        if keyword in message_lower:
            return response

    # If OpenAI is configured, use it
    if hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
        try:
            openai.api_key = settings.OPENAI_API_KEY

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system",
                     "content": "You are a helpful birthday wishes assistant. Help users create meaningful birthday messages, suggest gifts, and provide advice on celebrating birthdays."},
                    {"role": "user", "content": message}
                ],
                max_tokens=200
            )

            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI error: {e}")

    # Default fallback response
    return "That's interesting! I'm here to help with birthday wishes and gift suggestions. What would you like to know more about?"


def get_gift_recommendations(age=None, gender=None, interests=None):
    """Get personalized gift recommendations"""
    from .models import GiftSuggestion

    gifts = GiftSuggestion.objects.all()

    if age:
        # Filter by age range
        gifts = gifts.filter(age_group__contains=str(age))

    if gender:
        gifts = gifts.filter(
            models.Q(gender_preference=gender) |
            models.Q(gender_preference='unisex')
        )

    if interests:
        # Filter by interests (stored as JSON array)
        for interest in interests:
            gifts = gifts.filter(interests__contains=interest)

    return gifts.order_by('-popularity_score')[:10]


def calculate_age(birthday):
    """Calculate age from birthday"""
    today = timezone.now().date()
    age = today.year - birthday.year

    if (today.month, today.day) < (birthday.month, birthday.day):
        age -= 1

    return age


def get_birthday_wishes_suggestions(occasion='birthday', category='heartfelt'):
    """Get wish suggestions based on occasion and category"""

    suggestions = {
        'heartfelt': [
            "Wishing you a day filled with love, laughter, and all the happiness your heart can hold. Happy Birthday!",
            "May this special day bring you endless joy and tons of precious memories. Have a wonderful birthday!",
            "Here's to another year of wonderful memories and countless blessings. Happy Birthday!",
        ],
        'funny': [
            "Congratulations on being born a really long time ago! 🎉",
            "You're not getting older, you're just becoming a classic! Happy Birthday! 🎂",
            "Age is just a number... and in your case, a really big one! 😄 Happy Birthday!",
        ],
        'professional': [
            "Wishing you continued success and happiness on your special day. Happy Birthday!",
            "May this year bring you professional growth and personal fulfillment. Best wishes on your birthday!",
            "Happy Birthday! May your day be filled with joy and your year with prosperity.",
        ],
        'creative': [
            "Another 365 days of awesomeness completed! 🌟 Level up! Happy Birthday!",
            "Today is the anniversary of your legendary arrival on Earth! 🚀 Happy Birthday!",
            "The world became a better place the day you were born. Keep shining! ✨ Happy Birthday!",
        ]
    }

    return suggestions.get(category, suggestions['heartfelt'])