import typer

from app.commands.calendar import calendar_app
from app.commands.database import database_app
from app.commands.maintenance import maintenance_app

app = typer.Typer(help="VEAF Website CLI", no_args_is_help=True)
app.add_typer(calendar_app, name="calendar")
app.add_typer(database_app, name="database")
app.add_typer(maintenance_app, name="maintenance")


if __name__ == "__main__":
    app()
