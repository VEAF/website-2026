import logging

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from app.config import settings

logger = logging.getLogger(__name__)


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
    )


_fm: FastMail | None = None


def _get_fastmail() -> FastMail:
    global _fm
    if _fm is None:
        _fm = FastMail(_get_mail_config())
    return _fm


async def send_welcome_email(email: str, nickname: str) -> None:
    """Send welcome email after registration."""
    html = f"""\
<h2>Bienvenue sur le site de la VEAF, {nickname} !</h2>
<p>Votre compte a bien été créé.</p>
<p>Vous pouvez dès à présent vous connecter sur <a href="{settings.APP_URL}">{settings.APP_URL}</a>.</p>
<p>À bientôt sur nos serveurs !</p>
<p>L'équipe VEAF</p>"""

    message = MessageSchema(
        subject="Bienvenue sur le site de la VEAF",
        recipients=[email],
        body=html,
        subtype=MessageType.html,
    )
    try:
        await _get_fastmail().send_message(message)
    except Exception:
        logger.exception("Failed to send welcome email to %s", email)


async def send_password_reset_email(email: str, nickname: str, token: str) -> None:
    """Send password reset link."""
    reset_url = f"{settings.APP_URL}/reset-password?token={token}"
    html = f"""\
<h2>Réinitialisation de votre mot de passe</h2>
<p>Bonjour {nickname},</p>
<p>Vous avez demandé la réinitialisation de votre mot de passe.</p>
<p>Cliquez sur le lien ci-dessous pour choisir un nouveau mot de passe :</p>
<p><a href="{reset_url}">{reset_url}</a></p>
<p>Ce lien est valable pendant 24 heures.</p>
<p>Si vous n'êtes pas à l'origine de cette demande, ignorez cet email.</p>
<p>L'équipe VEAF</p>"""

    message = MessageSchema(
        subject="Réinitialisation de votre mot de passe - VEAF",
        recipients=[email],
        body=html,
        subtype=MessageType.html,
    )
    try:
        await _get_fastmail().send_message(message)
    except Exception:
        logger.exception("Failed to send password reset email to %s", email)
