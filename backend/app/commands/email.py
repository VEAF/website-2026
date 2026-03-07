import asyncio
import smtplib

import typer
from rich import print as rprint

from app.config import settings

email_app = typer.Typer(help="Email commands", no_args_is_help=True)


async def _send_with_template(to: str, subject: str, body: str, template: str) -> None:
    from app.services.email import send_email_with_template

    template_vars: dict[str, str] = {}
    if template == "register":
        template_vars = {"nickname": "Pilote"}
    elif template == "reset_password":
        template_vars = {"nickname": "Pilote", "reset_url": f"{settings.APP_URL}/reset-password?token=test-token"}

    await send_email_with_template(to=to, subject=subject, template=template, body=body, template_vars=template_vars)


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
    if settings.MAIL_SSL_TLS and settings.MAIL_STARTTLS:
        rprint("[bold red]Error[/bold red] — MAIL_SSL_TLS and MAIL_STARTTLS are mutually exclusive.")
        raise typer.Exit(1)

    rprint("[bold]Connecting to SMTP server...[/bold]")
    try:
        if settings.MAIL_SSL_TLS:
            with smtplib.SMTP_SSL(settings.MAIL_SERVER, settings.MAIL_PORT, timeout=10) as smtp:
                smtp.ehlo()
                if settings.MAIL_USERNAME:
                    smtp.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD.get_secret_value())
                rprint("[bold green]OK[/bold green] — SMTP server is reachable and ready.")
        else:
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
    template: str = typer.Option("default", "--template", help="Template name: default, register, reset_password"),
) -> None:
    """Send a test email using a template."""
    rprint(f"[bold]Sending email to {to} (template: {template})...[/bold]")
    try:
        asyncio.run(_send_with_template(to, subject, body, template))
        rprint(f"[bold green]OK[/bold green] — Email sent to {to}.")
    except Exception as e:
        rprint(f"[bold red]Error[/bold red] — {e}")
