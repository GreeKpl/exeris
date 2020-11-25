from flask import request, jsonify
from flask_login import login_user, logout_user

from exeris.core import models
# noinspection PyUnresolvedReferences
from exeris.outer import outer_bp, socketio_events


@outer_bp.route("/static/en.json")
def static_en_json():
    return outer_bp.send_static_file("en.json")


@outer_bp.route('/login', methods=['POST'])
def login():
    email = request.json.get('email', None)
    password = request.json.get('password', None)
    player = models.Player.query.filter_by(email=email, password=password).first()
    if not player:
        return jsonify({'login': False}), 401

    login_user(player, remember=True)

    resp = jsonify({'login': True})
    return resp, 200


@outer_bp.route('/logout', methods=['POST'])
def logout():
    resp = jsonify({'logout': True})
    logout_user()
    return resp, 200
