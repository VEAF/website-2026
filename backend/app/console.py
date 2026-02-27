import typer

from app.commands.database import database_app
from app.commands.maintenance import maintenance_app

app = typer.Typer(help="VEAF Website CLI", invoke_without_command=True)
app.add_typer(database_app, name="database")
app.add_typer(maintenance_app, name="maintenance")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())


if __name__ == "__main__":
    app()
