# Python modules
import logging
from typing import Optional

# Django modules
from django.core.cache import cache

# Project modules
from apps.auths.models import CustomUser


logger = logging.getLogger(__name__)


class PreferredLanguageCacheAccessor:
    """
    Helper class to get, set, and delete the user's OTP (One-Time Password) from the cache.
    This is useful to avoid unnecessary DB queries in middleware.
    """

    KEY_PREFIX = "preferred_language"

    # value in hours
    PREFERRED_LANGUAGE_TTL_HOURS = 24

    # 24 hours in seconds
    PREFERRED_LANGUAGE_TTL_SECS = PREFERRED_LANGUAGE_TTL_HOURS * 60 * 60

    @classmethod
    def _make_cache_key(cls, user_id: int) -> str:
        """Generate cache key for user language preference."""
        return f"{cls.KEY_PREFIX}:{user_id}"

    @classmethod
    def set(cls, user_id: int, preferred_language: str) -> None:
        """
        Set the user's preferred language.

        :param user_id: The user's ID.
        :param preferred_language: The user's preferred language (e.g. "en", "de").
        """
        cache.set(
            key=cls._make_cache_key(user_id=user_id),
            value=preferred_language,
            timeout=cls.PREFERRED_LANGUAGE_TTL_SECS,
        )
        logger.info(
            f"Cached preferred language for user {user_id} to {preferred_language}"
        )

    @classmethod
    def get(cls, user_id: int, extra_db_query: bool = True) -> Optional[str]:
        """
        Get user's preferred language from cache.

        Args:
            user_id: The user's ID

        Returns:
            Language code (e.g., 'en', 'de') or None if not cached
        """
        cache_key: str = cls._make_cache_key(user_id)
        preferred_language: Optional[str] = cache.get(cache_key)

        logger.debug(
            f"Got preferred language for user {user_id}, which is {preferred_language}"
        )

        if not preferred_language and extra_db_query:
            logger.warning(
                f"Preferred language not set for the user with ID: '{user_id}'. Make db query to get and set it."
            )
            preferred_language = (
                CustomUser.objects.filter(id=user_id)
                .values_list("preferred_language", flat=True)
                .first()
            )
            logger.debug(
                f"Queried DB for preferred language for user {user_id}, got: {preferred_language}"
            )
            if preferred_language:
                cls.set(user_id=user_id, preferred_language=preferred_language)

        return preferred_language
