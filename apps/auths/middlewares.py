# Python modules
from typing import Any, Callable, Optional

from django.core.handlers.wsgi import WSGIRequest

# Django modules
from django.utils import translation

# Django REST Framework modules
from rest_framework.request import Request as DRFResponse
from rest_framework_simplejwt.exceptions import TokenError

# Simple JWT
from rest_framework_simplejwt.tokens import AccessToken

# Project modules
from apps.auths.caches import PreferredLanguageCacheAccessor
from apps.auths.models import CustomUser
from settings.base import ENGLISH_LANGUAGE_CODE


class CustomLocaleMiddleware:
    """
    Determine and activate language for each request.

    Request language priority:
    1) Authenticated user preferred language
    2) App-Language header
    3) Default EN
    """

    def __init__(self, get_response: Callable[[WSGIRequest], DRFResponse]) -> None:
        """Initialize the middleware with the given get_response callable."""

        self.get_response = get_response

    def __call__(self, request: WSGIRequest) -> DRFResponse:
        """Process the request to set the appropriate language."""

        lang: str = self._determine_language(request)
        translation.activate(lang)
        request.LANGUAGE_CODE = lang

        response: DRFResponse = self.get_response(request)
        response.headers.setdefault("Content-Language", lang)

        translation.deactivate()
        return response

    def _get_user_id_from_jwt(self, request: WSGIRequest) -> Optional[int]:
        """Extract user_id from JWT token."""
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("JWT "):
            return None

        access_token: str = auth_header.strip().split(" ")[1]
        try:
            payload: dict[str, Any] = AccessToken(access_token)
            return payload.get("user_id")
        except TokenError:
            return None

    def _determine_language(self, request: WSGIRequest) -> str:
        """Determine the language for the request."""
        user_id: Optional[int] = self._get_user_id_from_jwt(request)

        if user_id is None:
            # Anonymous or fallback
            header_lang: Optional[str] = request.headers.get("App-Language")
            return (
                self._normalize(header_lang) if header_lang else ENGLISH_LANGUAGE_CODE
            )

        preferred: Optional[str] = PreferredLanguageCacheAccessor.get(user_id)
        return self._normalize(preferred) if preferred else ENGLISH_LANGUAGE_CODE

    def _normalize(self, lang: str) -> str:
        """Normalize language code to supported languages."""

        lang = lang.lower()
        return lang if lang in CustomUser.PREFERRED_LANGUAGES else ENGLISH_LANGUAGE_CODE
