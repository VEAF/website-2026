import logging
from datetime import UTC, datetime
from pathlib import Path

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from app.config import settings

logger = logging.getLogger(__name__)

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates" / "email"


def _get_mail_config() -> ConnectionConfig:
    return ConnectionConfig(
        MAIL_USERNAME=settings.MAIL_USERNAME,
        MAIL_PASSWORD=settings.MAIL_PASSWORD.get_secret_value(),
        MAIL_FROM=settings.MAIL_FROM,
        MAIL_PORT=settings.MAIL_PORT,
        MAIL_SERVER=settings.MAIL_SERVER,
        MAIL_STARTTLS=settings.MAIL_STARTTLS,
        MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
        USE_CREDENTIALS=bool(settings.MAIL_USERNAME),
        TEMPLATE_FOLDER=TEMPLATE_DIR,
    )


_fm: FastMail | None = None


def _get_fastmail() -> FastMail:
    global _fm
    if _fm is None:
        _fm = FastMail(_get_mail_config())
    return _fm


def _base_template_vars() -> dict:
    return {"app_url": settings.APP_URL, "year": datetime.now(UTC).year}


async def send_welcome_email(email: str, nickname: str) -> None:
    """Send welcome email after registration."""
    message = MessageSchema(
        subject="Bienvenue sur le site de la VEAF",
        recipients=[email],
        template_body={**_base_template_vars(), "nickname": nickname},
        subtype=MessageType.html,
    )
    try:
        await _get_fastmail().send_message(message, template_name="register.html")
    except Exception:
        logger.exception("Failed to send welcome email to %s", email)


async def send_password_reset_email(email: str, nickname: str, token: str) -> None:
    """Send password reset link."""
    reset_url = f"{settings.APP_URL}/reset-password?token={token}"
    message = MessageSchema(
        subject="Réinitialisation de votre mot de passe - VEAF",
        recipients=[email],
        template_body={**_base_template_vars(), "nickname": nickname, "reset_url": reset_url},
        subtype=MessageType.html,
    )
    try:
        await _get_fastmail().send_message(message, template_name="reset_password.html")
    except Exception:
        logger.exception("Failed to send password reset email to %s", email)


async def send_email_with_template(
    to: str,
    subject: str,
    template: str = "default",
    body: str = "",
    template_vars: dict | None = None,
) -> None:
    """Send an email using a named template."""
    context = {**_base_template_vars(), "body": body}
    if template_vars:
        context.update(template_vars)
    message = MessageSchema(
        subject=subject,
        recipients=[to],
        template_body=context,
        subtype=MessageType.html,
    )
    await _get_fastmail().send_message(message, template_name=f"{template}.html")
