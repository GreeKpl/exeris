import base64
import urllib

from flask import g, render_template, redirect, request
from pydiscourse.exceptions import DiscourseError
from pydiscourse.sso import sso_validate, sso_payload

from exeris.app import app
from exeris.core import main
# noinspection PyUnresolvedReferences
from exeris.player import player_bp, socketio_events


@player_bp.route("/", defaults={'path': ''})
@player_bp.route("/<path:path>")
def page_player(path):
    return render_template("frontend/build/index.html")


@player_bp.route("/discourse_sso")
def discourse_sso_login():
    if not main.app.config["ENABLE_SSO_FOR_DISCOURSE"]:
        return "Single-sign on for discourse forum is disabled by Exeris server configuration"

    payload = request.args["sso"]
    signature = request.args["sig"]
    sso_secret = main.app.config["DISCOURSE_SSO_SECRET"]

    try:
        sso_validate(payload, signature, sso_secret)
    except DiscourseError as e:
        return str(e.args)

    if g.player.confirmed_at is None:
        return "The email address of the {} is not yet confirmed".format(g.player.id)

    base64_encoded_payload = urllib.parse.unquote(payload)
    payload = urllib.parse.parse_qs(base64.b64decode(base64_encoded_payload).decode("utf8"))

    response_payload = sso_payload(sso_secret,
                                   nonce=payload["nonce"][0],
                                   email=g.player.email,
                                   external_id=g.player.id,
                                   username=g.player.id
                                   )

    return redirect(payload["return_sso_url"][0] + "?" + response_payload)
