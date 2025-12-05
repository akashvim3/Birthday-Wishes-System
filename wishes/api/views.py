from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from wishes.models import (
    UserProfile, BirthdayWish, GroupWish, GiftSuggestion
)
from .serializers import (
    UserProfileSerializer, BirthdayWishSerializer,
    GroupWishSerializer, GiftSuggestionSerializer
)


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint for user profiles
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    ordering_fields = ['created_at', 'birthday']

    @action(detail=False, methods=['get'])
    def upcoming_birthdays(self, request):
        """Get upcoming birthdays"""
        days = int(request.query_params.get('days', 30))
        profiles = UserProfile.objects.get_upcoming_birthdays(days=days)
        serializer = self.get_serializer(profiles, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_profile(self, request):
        """Get current user's profile"""
        profile = request.user.profile
        serializer = self.get_serializer(profile)
        return Response(serializer.data)


class BirthdayWishViewSet(viewsets.ModelViewSet):
    """
    API endpoint for birthday wishes
    """
    queryset = BirthdayWish.objects.all()
    serializer_class = BirthdayWishSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['wish_type', 'status', 'is_public']
    ordering_fields = ['created_at', 'scheduled_date']

    def get_queryset(self):
        """Filter wishes based on user"""
        user = self.request.user
        return BirthdayWish.objects.filter(
            models.Q(sender=user) | models.Q(recipient=user)
        )

    def perform_create(self, serializer):
        """Set sender to current user"""
        serializer.save(sender=self.request.user)

    @action(detail=False, methods=['get'])
    def sent(self, request):
        """Get wishes sent by current user"""
        wishes = BirthdayWish.objects.filter(sender=request.user)
        serializer = self.get_serializer(wishes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def received(self, request):
        """Get wishes received by current user"""
        wishes = BirthdayWish.objects.filter(recipient=request.user)
        serializer = self.get_serializer(wishes, many=True)
        return Response(serializer.data)


class GiftSuggestionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for gift suggestions (read-only)
    """
    queryset = GiftSuggestion.objects.all()
    serializer_class = GiftSuggestionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'is_featured', 'gender_preference']
    search_fields = ['title', 'description']

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured gift suggestions"""
        gifts = GiftSuggestion.objects.filter(is_featured=True)
        serializer = self.get_serializer(gifts, many=True)
        return Response(serializer.data)


class GroupWishViewSet(viewsets.ModelViewSet):
    """
    API endpoint for group wishes
    """
    queryset = GroupWish.objects.all()
    serializer_class = GroupWishSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter group wishes based on user"""
        user = self.request.user
        return GroupWish.objects.filter(
            models.Q(creator=user) | models.Q(contributors=user)
        ).distinct()

    def perform_create(self, serializer):
        """Set creator to current user"""
        serializer.save(creator=self.request.user)

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """Join a group wish"""
        group_wish = self.get_object()

        if request.user == group_wish.recipient:
            return Response(
                {'error': 'You cannot join your own birthday wish'},
                status=status.HTTP_400_BAD_REQUEST
            )

        group_wish.contributors.add(request.user)
        return Response({'status': 'joined successfully'})
