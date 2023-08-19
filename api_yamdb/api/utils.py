
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken

from api_yamdb.settings import DEFAULT_FROM_EMAIL


def custom_send_mail(email, confirmation_code):
    """Отправляет код подтверждения на почту пользователя."""
    send_mail(
        'Код подтверждения',
        f'Код подтверждения для получения токена: {confirmation_code}',
        DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )


def get_tokens_for_user(user):
    """Генерит токен."""
    refresh = RefreshToken.for_user(user)

    return {
        'token': str(refresh.access_token),
    }
