import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'birthday_system.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    # Add WebSocket support if needed in the future
    # "websocket": AuthMiddlewareStack(
    #     URLRouter(
    #         # websocket URL patterns here
    #     )
    # ),
})
