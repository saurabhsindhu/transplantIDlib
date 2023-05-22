from environs import Env
from flask import Flask, redirect, url_for

from app import create_app

env = Env()
env.read_env()

app = create_app(env.str('FLASK_ENV'))


@app.route('/')
def home():
    return redirect(url_for('kerko.search'))


@app.shell_context_processor
def make_shell_context():
    """Return context dict for a shell session, giving access to variables."""
    return dict(app=app)
