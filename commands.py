# commands.py
from flask import current_app
from flask.cli import with_appcontext
import click
from .extensions import db

@click.command("create-db")
@with_appcontext
def create_db():
    db.create_all()
    click.echo("✅ Database tables created.")
