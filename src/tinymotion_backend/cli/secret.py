import secrets

import click
from cryptography.fernet import Fernet


@click.group()
def secret():
    """Commands related to secrets"""
    pass


@secret.command()
@click.option("-a", "--auth", is_flag=True, default=False, help="Generate access and refresh tokens")
@click.option("-d", "--database", is_flag=True, default=False, help="Generate database secrets")
@click.option("-v", "--video", is_flag=True, default=False, help="Generate video secrets")
def generate(auth: bool, database: bool, video: bool):
    """Generate new secrets"""
    if not (auth or database or video):
        click.echo("Must select which secrets to generate")
        click.echo("")
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        ctx.exit()

    if auth:
        click.echo("")
        click.echo("Generating access and refresh tokens:")
        access_token = secrets.token_urlsafe()
        refresh_token = secrets.token_urlsafe()
        click.echo(f"access_token = {access_token}")
        click.echo(f"refresh_token = {refresh_token}")

    if database:
        click.echo("")
        click.echo("Generating database secrets:")
        database_secret = secrets.token_urlsafe()
        click.echo(f"database_secret = {database_secret}")

    if video:
        click.echo("")
        click.echo("Generating video secrets:")
        video_secret = Fernet.generate_key().decode("ascii")
        click.echo(f"video_secret = {video_secret}")

    click.echo("")
