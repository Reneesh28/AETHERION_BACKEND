from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from django.contrib.auth import get_user_model
from django.db import close_old_connections
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from asgiref.sync import sync_to_async

User = get_user_model()


@sync_to_async
def get_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None


class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        print("JWT middleware triggered")

        close_old_connections()

        query_string = scope.get("query_string", b"").decode()
        query_params = parse_qs(query_string)
        token = query_params.get("token")

        if not token:
            scope["user"] = None
            return await super().__call__(scope, receive, send)

        token = token[0]

        try:
            access_token = AccessToken(token)
            user_id = int(access_token["user_id"])   # FIXED
            scope["user"] = await get_user(user_id)
        except (InvalidToken, TokenError, KeyError, ValueError):
            scope["user"] = None

        return await super().__call__(scope, receive, send)