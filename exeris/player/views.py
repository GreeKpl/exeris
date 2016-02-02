from flask import g, render_template

from exeris.core import models, achievements
# noinspection PyUnresolvedReferences
from exeris.player import player_bp, socketio_events


@player_bp.route("/")
def page_player():
    chars = models.Character.query.filter_by(player=g.player).all()

    awarded_achievements = models.Achievement.query.filter_by(achiever=g.player).all()
    achievements_to_show = []
    for awarded_achievement in awarded_achievements:
        for achievement in achievements.achievements:
            if achievement[0] == awarded_achievement.achievement:
                achievements_to_show.append(achievement)

    return render_template("page_player.html", chars=chars, player=g.player, achievements=achievements_to_show)
