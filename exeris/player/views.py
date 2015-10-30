import traceback

from flask import g, render_template

from exeris.core import models, achievements
from exeris.player import player_bp, sijax


@player_bp.with_sijax_route("/")
def page_player():

    try:
        if g.sijax.is_sijax_request:
            g.sijax.register_object(sijax.PlayerPage)
            return g.sijax.process_request()

        chars = models.Character.query.filter_by(player=g.player).all()

        awarded_achievements = models.Achievement.query.filter_by(achiever=g.player).all()
        achievements_to_show = []
        for awarded_achievement in awarded_achievements:
            for achievement in achievements.achievements:
                if achievement[0] == awarded_achievement.achievement:
                    achievements_to_show.append(achievement)

        return render_template("page_player.html", chars=chars, player=g.player, achievements=achievements_to_show)
    except Exception:
        print(traceback.format_exc())
