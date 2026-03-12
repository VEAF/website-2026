import typer

from app.commands.calendar import calendar_app
from app.commands.database import database_app
from app.commands.email import email_app
from app.commands.maintenance import maintenance_app
from app.commands.discord import discord_app
from app.commands.teamspeak import teamspeak_app

app = typer.Typer(help="VEAF Website CLI", no_args_is_help=True)
app.add_typer(calendar_app, name="calendar")
app.add_typer(database_app, name="database")
app.add_typer(discord_app, name="discord")
app.add_typer(email_app, name="email")
app.add_typer(maintenance_app, name="maintenance")
app.add_typer(teamspeak_app, name="teamspeak")


if __name__ == "__main__":
    app()
