from celery import shared_task


@shared_task
def send_email(to_email: str, msg: str) -> bool:
    """
    Simulate sending an email.

    Parameters:
        to_email: str
            The recipient's email address.
        msg: str
            The message content.

    Returns:
        bool
            True if the email was "sent" successfully, False otherwise.
    """
    # Simulate email sending logic here (e.g., using an email service)
    print(f"Sending email to {to_email} with message: {msg}")
    return True

@shared_task(name="spam_everyone_every_5_minutes")
def spam_everyone_every_5_minutes():
    ...