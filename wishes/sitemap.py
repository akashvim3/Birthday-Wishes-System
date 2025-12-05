from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import BirthdayWish, GiftSuggestion

class StaticViewSitemap(Sitemap):
    """Sitemap for static pages"""
    priority = 0.8
    changefreq = 'daily'

    def items(self):
        return ['index', 'gift_suggestions']

    def location(self, item):
        return reverse(item)

class PublicWishesSitemap(Sitemap):
    """Sitemap for public birthday wishes"""
    changefreq = 'weekly'
    priority = 0.6

    def items(self):
        return BirthdayWish.objects.filter(is_public=True, status='sent')

    @staticmethod
    def lastmod(obj):
        return obj.updated_at

class GiftSuggestionSitemap(Sitemap):
    """Sitemap for gift suggestions"""
    changefreq = 'monthly'
    priority = 0.7

    def items(self):
        return GiftSuggestion.objects.filter(is_featured=True)

    @staticmethod
    def lastmod(obj):
        return obj.updated_at
