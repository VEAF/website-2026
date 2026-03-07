import asyncio
import smtplib

import typer
from rich import print as rprint

from app.config import settings

email_app = typer.Typer(help="Email commands", no_args_is_help=True)


async def _send(to: str, subject: str, body: str) -> None:
    from fastapi_mail import MessageSchema, MessageType

    from app.services.email import _get_fastmail

    message = MessageSchema(
        subject=subject,
        recipients=[to],
        body=body,
        subtype=MessageType.html,
    )
    await _get_fastmail().send_message(message)


@email_app.command("check")
def check() -> None:
    """Check SMTP server connectivity and display current settings."""
    rprint("[bold]SMTP configuration:[/bold]")
    rprint(f"  Server:   {settings.MAIL_SERVER}:{settings.MAIL_PORT}")
    rprint(f"  From:     {settings.MAIL_FROM}")
    rprint(f"  STARTTLS: {settings.MAIL_STARTTLS}")
    rprint(f"  SSL/TLS:  {settings.MAIL_SSL_TLS}")
    rprint(f"  Username: {settings.MAIL_USERNAME or '(none)'}")
    rprint()
    rprint("[bold]Connecting to SMTP server...[/bold]")
    try:
        with smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT, timeout=10) as smtp:
            smtp.ehlo()
            if settings.MAIL_STARTTLS:
                smtp.starttls()
                smtp.ehlo()
            if settings.MAIL_USERNAME:
                smtp.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD.get_secret_value())
            rprint("[bold green]OK[/bold green] — SMTP server is reachable and ready.")
    except Exception as e:
        rprint(f"[bold red]Error[/bold red] — {e}")


@email_app.command("send")
def send(
    to: str = typer.Option(..., "--to", help="Recipient email address"),
    subject: str = typer.Option("Test VEAF", "--subject", help="Email subject"),
    body: str = typer.Option("Ceci est un email de test.", "--body", help="Email body (HTML supported)"),
) -> None:
    """Send a test email."""
    rprint(f"[bold]Sending email to {to}...[/bold]")
    try:
        asyncio.run(_send(to, subject, body))
        rprint(f"[bold green]OK[/bold green] — Email sent to {to}.")
    except Exception as e:
        rprint(f"[bold red]Error[/bold red] — {e}")
