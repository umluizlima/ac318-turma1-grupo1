from flask import (
    Blueprint, send_from_directory
)

bp = Blueprint('pwa', __name__, url_prefix='')


@bp.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')


@bp.route('/sw.js')
def service_worker():
    return send_from_directory('static', 'sw.js')
