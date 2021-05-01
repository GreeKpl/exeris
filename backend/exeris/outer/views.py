from flask import request, jsonify
from flask_login import login_user, logout_user

from exeris.core import models, main
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


@outer_bp.route('/ping', methods=['GET'])
def ping():
    resp = '{"pong": true}'
    return resp, 200


@outer_bp.route("/report_missing_tag", methods=['POST'])
def report_missing_tag():
    """
    API endpoint that (when run in debug mode) allows to report tag keys missing on the client-side.
    When not run in the debug mode, then it does nothing with the value.
    :return:
    """
    if not main.app.config["DEBUG"]:
        return ""

    missing_keys_info = dict(request.form)
    del missing_keys_info["_t"]  # remove date
    assert len(missing_keys_info) == 1, "Missing tag should give a single key"
    missing_tag_key = list(missing_keys_info.keys())[0]

    g.pyslate.t(missing_tag_key, client_side=True)  # ask pyslate to call standard "missing key" code
    return ""
