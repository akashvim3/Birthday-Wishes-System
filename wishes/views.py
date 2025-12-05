from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Q, Count
from django.core.paginator import Paginator
import json
from datetime import datetime, timedelta

from .models import (
    UserProfile, BirthdayWish, GroupWish, GroupWishContribution,
    GiftSuggestion, CalendarEvent, ChatMessage, WishTemplate
)
from .forms import (
    UserProfileForm, BirthdayWishForm, GroupWishForm,
    VoiceMessageForm, CalendarEventForm
)
from .utils import (
    send_birthday_notification, generate_ai_wish,
    schedule_birthday_wish, get_gift_recommendations
)


def index(request):
    """Homepage with featured content"""
    context = {
        'upcoming_birthdays': [],
        'featured_templates': WishTemplate.objects.filter(is_premium=False)[:6],
        'total_wishes_sent': BirthdayWish.objects.filter(status='sent').count(),
    }

    if request.user.is_authenticated:
        # Get upcoming birthdays for authenticated users
        context['upcoming_birthdays'] = UserProfile.objects.get_upcoming_birthdays(days=30)
        context['user_wishes'] = BirthdayWish.objects.filter(
            recipient=request.user
        ).order_by('-created_at')[:5]

    return render(request, 'index.html', context)


@login_required
def dashboard(request):
    """User dashboard with statistics and overview"""
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    # Statistics
    sent_wishes = BirthdayWish.objects.filter(sender=request.user, status='sent').count()
    received_wishes = BirthdayWish.objects.filter(recipient=request.user, status='sent').count()
    scheduled_wishes = BirthdayWish.objects.filter(sender=request.user, status='scheduled').count()

    # Upcoming birthdays
    upcoming = UserProfile.objects.get_upcoming_birthdays(days=30)

    # Recent activity
    recent_wishes = BirthdayWish.objects.filter(
        Q(sender=request.user) | Q(recipient=request.user)
    ).order_by('-created_at')[:10]

    # Group wishes
    active_group_wishes = GroupWish.objects.filter(
        contributors=request.user,
        is_active=True
    ).distinct()

    context = {
        'user_profile': user_profile,
        'sent_wishes': sent_wishes,
        'received_wishes': received_wishes,
        'scheduled_wishes': scheduled_wishes,
        'upcoming_birthdays': upcoming,
        'recent_wishes': recent_wishes,
        'active_group_wishes': active_group_wishes,
    }

    return render(request, 'dashboard.html', context)


@login_required
def create_wish(request):
    """Create a new birthday wish"""
    if request.method == 'POST':
        form = BirthdayWishForm(request.POST, request.FILES)

        if form.is_valid():
            wish = form.save(commit=False)
            wish.sender = request.user
            wish.save()

            # Handle voice message if uploaded
            if 'voice_message' in request.FILES:
                wish.voice_message = request.FILES['voice_message']
                wish.wish_type = 'voice'
                wish.save()

            # Schedule if needed
            if wish.scheduled_date:
                schedule_birthday_wish(wish)
                messages.success(request, 'Birthday wish scheduled successfully!')
            else:
                wish.mark_as_sent()
                send_birthday_notification(wish)
                messages.success(request, 'Birthday wish sent successfully!')

            return redirect('dashboard')
    else:
        form = BirthdayWishForm()

    # Get available templates
    templates = WishTemplate.objects.all()[:10]

    context = {
        'form': form,
        'templates': templates,
    }

    return render(request, 'create_wish.html', context)


@login_required
def calendar_view(request):
    """Calendar view with all birthdays"""
    # Get all user profiles with birthdays
    profiles = UserProfile.objects.exclude(birthday__isnull=True)

    # Get user's calendar events
    events = CalendarEvent.objects.filter(user=request.user)

    # Prepare calendar data
    calendar_data = []
    for profile in profiles:
        next_birthday = profile.get_next_birthday()
        if next_birthday:
            calendar_data.append({
                'title': f"{profile.user.get_full_name() or profile.user.username}'s Birthday",
                'date': next_birthday.isoformat(),
                'user_id': profile.user.id,
                'age': profile.get_age(),
            })

    context = {
        'calendar_data': json.dumps(calendar_data),
        'events': events,
    }

    return render(request, 'calendar.html', context)


@login_required
def gift_suggestions(request):
    """Gift suggestions page with filtering"""
    category = request.GET.get('category', '')
    price_range = request.GET.get('price_range', '')
    search_query = request.GET.get('q', '')

    gifts = GiftSuggestion.objects.all()

    if category:
        gifts = gifts.filter(category=category)

    if search_query:
        gifts = gifts.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(gifts, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'categories': GiftSuggestion.CATEGORY_CHOICES,
        'selected_category': category,
    }

    return render(request, 'gift_suggestions.html', context)


@login_required
def group_wishes(request):
    """Manage group wishes"""
    if request.method == 'POST':
        form = GroupWishForm(request.POST)

        if form.is_valid():
            group_wish = form.save(commit=False)
            group_wish.creator = request.user
            group_wish.save()
            group_wish.generate_invitation_code()

            messages.success(request, f'Group wish created! Invitation code: {group_wish.invitation_code}')
            return redirect('group_wish_detail', pk=group_wish.pk)
    else:
        form = GroupWishForm()

    # Get user's group wishes
    created_wishes = GroupWish.objects.filter(creator=request.user)
    contributed_wishes = GroupWish.objects.filter(contributors=request.user).exclude(creator=request.user)

    context = {
        'form': form,
        'created_wishes': created_wishes,
        'contributed_wishes': contributed_wishes,
    }

    return render(request, 'group_wishes.html', context)


@login_required
def group_wish_detail(request, pk):
    """Detail view for a group wish"""
    group_wish = get_object_or_404(GroupWish, pk=pk)

    # Check if user has access
    if request.user != group_wish.creator and request.user not in group_wish.contributors.all():
        messages.error(request, 'You do not have access to this group wish.')
        return redirect('group_wishes')

    contributions = group_wish.contributions.all()

    context = {
        'group_wish': group_wish,
        'contributions': contributions,
        'is_creator': request.user == group_wish.creator,
    }

    return render(request, 'group_wish_detail.html', context)


@login_required
def join_group_wish(request):
    """Join a group wish with invitation code"""
    if request.method == 'POST':
        invitation_code = request.POST.get('invitation_code')

        try:
            group_wish = GroupWish.objects.get(invitation_code=invitation_code, is_active=True)

            if request.user == group_wish.recipient:
                messages.error(request, 'You cannot contribute to your own birthday wish!')
            elif request.user in group_wish.contributors.all():
                messages.info(request, 'You have already joined this group wish.')
            else:
                group_wish.contributors.add(request.user)
                messages.success(request, 'Successfully joined the group wish!')

            return redirect('group_wish_detail', pk=group_wish.pk)

        except GroupWish.DoesNotExist:
            messages.error(request, 'Invalid invitation code.')

    return redirect('group_wishes')


@login_required
@csrf_exempt
def save_voice_message(request):
    """Save voice message via AJAX"""
    if request.method == 'POST' and request.FILES.get('voice_recording'):
        wish_id = request.POST.get('wish_id')
        voice_file = request.FILES['voice_recording']

        if wish_id:
            wish = get_object_or_404(BirthdayWish, id=wish_id, sender=request.user)
            wish.voice_message = voice_file
            wish.wish_type = 'voice'
            wish.save()

            return JsonResponse({
                'success': True,
                'message': 'Voice message saved successfully!'
            })

        return JsonResponse({
            'success': False,
            'message': 'Invalid wish ID'
        }, status=400)

    return JsonResponse({
        'success': False,
        'message': 'No voice recording provided'
    }, status=400)


@login_required
@csrf_exempt
def chatbot_api(request):
    """Chatbot API endpoint"""
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message', '')
        session_id = data.get('session_id', '')

        if not user_message:
            return JsonResponse({
                'success': False,
                'message': 'No message provided'
            }, status=400)

        # Generate AI response (you can integrate OpenAI or custom logic)
        response = generate_ai_wish(user_message, request.user)

        # Save chat history
        ChatMessage.objects.create(
            user=request.user,
            message=user_message,
            response=response,
            session_id=session_id
        )

        return JsonResponse({
            'success': True,
            'response': response
        })

    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    }, status=405)


@login_required
def profile_view(request):
    """User profile page"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)

        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)

    context = {
        'form': form,
        'profile': profile,
    }

    return render(request, 'profile.html', context)


def register(request):
    """User registration"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)

            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')

            user = authenticate(username=username, password=password)
            login(request, user)

            messages.success(request, f'Welcome {username}! Your account has been created.')
            return redirect('dashboard')
    else:
        form = UserCreationForm()

    return render(request, 'registration/register.html', {'form': form})
