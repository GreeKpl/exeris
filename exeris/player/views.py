import datetime
import json
import urllib

import base64

from exeris.app import oauth, app
from exeris.core import models, achievements, main
from exeris.core.main import db
from flask import g, render_template, redirect, request

# noinspection PyUnresolvedReferences
from exeris.player import player_bp, socketio_events
from pydiscourse.exceptions import DiscourseError
from pydiscourse.sso import sso_validate, sso_payload


@player_bp.route("/", defaults={'path': ''})
@player_bp.route("/<path:path>")
def page_player(path):
    return render_template("front/dist/index.html")


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


# endpoints to implement flask app as OAUTH2 provider
# it's needed to impersonate as GitLab to embrace single-sign-on for mattermost chat

class Client:
    def __init__(self, client_dict):
        self.client_id = client_dict["client_id"]
        self.client_secret = client_dict["client_secret"]
        self.client_type = client_dict["client_type"]
        self.redirect_uris = client_dict["redirect_uris"]
        self.default_redirect_uri = client_dict["default_redirect_uri"]
        self.default_scopes = client_dict["default_scopes"]


@app.route("/oauth/api/current_player_info")
@oauth.require_oauth("login")
def sso_user_info_for_mattermost():
    current_player = request.oauth.user
    return json.dumps({"id": current_player.serial_id,
                       "username": current_player.id,
                       "login": current_player.id,
                       "email": current_player.email,
                       "name": current_player.id,
                       })


@oauth.clientgetter
def load_client(requested_client_id):
    oauth_client_dicts = app.config["OAUTH2_CLIENTS"]
    found_client_dict = next(client for client in oauth_client_dicts if client["client_id"] == requested_client_id)
    if not found_client_dict:
        return None
    return Client(found_client_dict)


@oauth.grantgetter
def load_grant(client_id, code):
    return models.GrantToken.query.filter_by(client_id=client_id, code=code).first()


@oauth.grantsetter
def save_grant(client_id, code, request):
    expires = datetime.datetime.utcnow() + datetime.timedelta(seconds=100)
    grant = models.GrantToken(
        client_id=client_id,
        code=code['code'],
        redirect_uri=request.redirect_uri,
        _scopes=' '.join(request.scopes),
        user=g.player,
        expires=expires
    )
    db.session.add(grant)
    db.session.commit()

    return grant


@oauth.tokengetter
def load_token(access_token=None, refresh_token=None):
    if access_token:
        return models.BearerToken.query.filter_by(access_token=access_token).first()
    elif refresh_token:
        return models.BearerToken.query.filter_by(refresh_token=refresh_token).first()


@oauth.tokensetter
def save_token(token, request):
    existing_tokens = models.BearerToken.query.filter_by(
        client_id=request.client.client_id,
        user_id=request.user.id
    )
    # make sure that every client has only one token connected to a user
    for existing_bearer_token in existing_tokens:
        db.session.delete(existing_bearer_token)
    expires_in = token.pop('expires_in')
    expires = datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in)

    new_token = models.BearerToken(
        access_token=token['access_token'],
        refresh_token=token['refresh_token'],
        token_type=token['token_type'],
        _scopes=token['scope'],
        expires=expires,
        client_id=request.client.client_id,
        user_id=request.user.id,
    )
    db.session.add(new_token)
    db.session.commit()
    return new_token


@player_bp.route('/oauth/authorize', methods=['GET', 'POST'])
@oauth.authorize_handler
def authorize(*args, **kwargs):
    """
    Authorization of an user. It's in 'player' blueprint,
    so user needs to be logged in, otherwise the login form is shown.
    :param args:
    :param kwargs:
    :return: True when the user is logged in and the email address is confirmed
    """
    return g.player.confirmed_at is not None


@app.route('/oauth/token', methods=["GET", "POST"])
@oauth.token_handler
def access_token():
    return None
