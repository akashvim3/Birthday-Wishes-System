from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Main pages
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),

    # Wish management
    path('create-wish/', views.create_wish, name='create_wish'),
    path('save-voice/', views.save_voice_message, name='save_voice_message'),

    # Calendar
    path('calendar/', views.calendar_view, name='calendar'),

    # Gift suggestions
    path('gifts/', views.gift_suggestions, name='gift_suggestions'),

    # Group wishes
    path('group-wishes/', views.group_wishes, name='group_wishes'),
    path('group-wish/<uuid:pk>/', views.group_wish_detail, name='group_wish_detail'),
    path('join-group-wish/', views.join_group_wish, name='join_group_wish'),

    # Chatbot
    path('api/chatbot/', views.chatbot_api, name='chatbot_api'),

    # Authentication
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', views.custom_logout, name='logout'),
]
