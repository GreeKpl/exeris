import urllib

import base64
from exeris.core import models, achievements, main
from flask import g, render_template, redirect, request

# noinspection PyUnresolvedReferences
from exeris.player import player_bp, socketio_events
from pydiscourse.exceptions import DiscourseError
from pydiscourse.sso import sso_validate, sso_payload


@player_bp.route("/")
def page_player():
    chars = models.Character.query.filter_by(player=g.player).all()

    awarded_achievements = models.Achievement.query.filter_by(achiever=g.player).all()
    achievements_to_show = []
    for awarded_achievement in awarded_achievements:
        for achievement in achievements.achievements:
            if achievement[0] == awarded_achievement.achievement:
                achievements_to_show.append(achievement)

    return render_template("page_dashboard.html", chars=chars, player=g.player, achievements=achievements_to_show)


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

    base64_encoded_payload = urllib.parse.unquote(payload)
    payload = urllib.parse.parse_qs(base64.b64decode(base64_encoded_payload).decode("utf8"))

    response_payload = sso_payload(sso_secret,
                                   nonce=payload["nonce"][0],
                                   email=g.player.email,
                                   external_id=g.player.id,
                                   username=g.player.id
                                   )

    return redirect(payload["return_sso_url"][0] + "?" + response_payload)
