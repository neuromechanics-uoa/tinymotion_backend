import secrets

import click
from cryptography.fernet import Fernet


@click.group()
def secret():
    """Commands related to secrets"""
    pass


@secret.command()
@click.option("-a", "--access", is_flag=True, default=False, help="Generate access token")
@click.option("-r", "--refresh", is_flag=True, default=False, help="Generate refresh token")
@click.option("-d", "--database", is_flag=True, default=False, help="Generate database secret")
@click.option("-v", "--video", is_flag=True, default=False, help="Generate video secret")
@click.option("-e", "--for-env-file", is_flag=True, default=False, help="Print the secret(s) in .env file format")
def generate(access: bool, refresh: bool, database: bool, video: bool, for_env_file: bool):
    """Generate new secrets"""
    # at least one secret should be specified
    if not (access or refresh or database or video):
        click.echo("Must select which secrets to generate")
        click.echo("")
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        ctx.exit()

    if access:
        if not for_env_file:
            click.echo("")
            click.echo("Generating access token:")
        access_token = secrets.token_urlsafe()
        if for_env_file:
            click.echo(f"TINYMOTION_ACCESS_TOKEN_SECRET_KEY={access_token}")
        else:
            click.echo(f"access_token = {access_token}")

    if refresh:
        if not for_env_file:
            click.echo("")
            click.echo("Generating refresh token:")
        refresh_token = secrets.token_urlsafe()
        if for_env_file:
            click.echo(f"TINYMOTION_REFRESH_TOKEN_SECRET_KEY={refresh_token}")
        else:
            click.echo(f"refresh_token = {refresh_token}")

    if database:
        if not for_env_file:
            click.echo("")
            click.echo("Generating database secrets:")
        database_secret = secrets.token_urlsafe()
        if for_env_file:
            click.echo(f"TINYMOTION_DATABASE_SECRET_KEY={database_secret}")
        else:
            click.echo(f"database_secret = {database_secret}")

    if video:
        if not for_env_file:
            click.echo("")
            click.echo("Generating video secrets:")
        video_secret = Fernet.generate_key().decode("ascii")
        if for_env_file:
            click.echo(f"TINYMOTION_VIDEO_SECRET_KEY={video_secret}")
        else:
            click.echo(f"video_secret = {video_secret}")

    if not for_env_file:
        click.echo("")
