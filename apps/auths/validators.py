# Django modules
from django.core.exceptions import ValidationError

_RESTRICTED_DOMAINS = (
    "mail.ru",
)


def validate_email_domain(value: str) -> None:
    """
    Validate that the email address belongs to a specific domain.
    """
    domain: str = value.split('@')[-1]
    if domain in _RESTRICTED_DOMAINS:
        raise ValidationError(
            message=f"Registration using \"{domain}\" is not allowed.",
            code="invalid_domain",
        )
