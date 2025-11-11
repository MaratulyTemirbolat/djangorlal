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


def validate_email_payload_not_in_full_name(email: str, full_name: str) -> None:
    """
    Validate that the email address does not contain the full name.
    """
    email_payload: str = email.split("@")[0]
    if email_payload.lower() in full_name.lower():
        raise ValidationError(
            {
                "email": "Email address payload should not be part of the full name.",
                "full_name": "Full name should not contain email address payload.",
            },
            code="invalid_email_full_name_relation",
        )
