import os
from flask import Flask, render_template


def create_app():
    app = Flask(__name__,
                instance_relative_config=True,
                static_url_path='')
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY') or
        'you-will-never-guess',
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL') or
        'sqlite:///' + os.path.join(app.instance_path, 'app.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        VCARD_FOLDER=os.path.join(app.instance_path, 'vcf')
    )

    try:
        os.makedirs(app.instance_path)
        os.makedirs(os.path.join(app.instance_path, 'vcf'))
    except OSError:
        pass

    from flask_sslify import SSLify
    if 'DYNO' in os.environ:
        sslify = SSLify(app)

    from app.model import db, migrate
    db.init_app(app)
    migrate.init_app(app, db)

    from app.controller import pwa, main, auth, user
    app.register_blueprint(pwa.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(user.bp)
    app.register_blueprint(main.bp)

    return app
