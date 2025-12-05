from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserProfileViewSet, BirthdayWishViewSet,
    GiftSuggestionViewSet, GroupWishViewSet
)

router = DefaultRouter()
router.register(r'profiles', UserProfileViewSet)
router.register(r'wishes', BirthdayWishViewSet)
router.register(r'gifts', GiftSuggestionViewSet)
router.register(r'group-wishes', GroupWishViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
