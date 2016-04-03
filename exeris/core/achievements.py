import sqlalchemy as sql
import sqlalchemy.dialects.postgresql as psql
from sqlalchemy import func

from exeris.core.main import hook
from exeris.core import main, models
from exeris.core.main import db
from exeris.core.models import AchievementCharacterProgress as ACProgress


class AchievementEntries:
    TEXTS_SPOKEN = "texts_spoken"
    WHISPERS = "whispers"
    ENTERED_LOCATIONS = "entered_locations"
    EATEN_POTATOES = "eaten_potatoes"


class CheckHelper:
    @staticmethod
    def check_list_min_length(name, character, min_length):
        return ACProgress.query.filter_by(name=name, character=character).filter(
            func.jsonb_array_length(ACProgress.details) >= min_length).first()

    @staticmethod
    def check_min_number(name, character, min_length):
        return ACProgress.query.filter_by(name=name, character=character).filter(
            ACProgress.details >= sql.cast(min_length, psql.JSONB)).first()


achievements = [
    ("superhero", "enter 5 different buildings",
     lambda ch: CheckHelper.check_list_min_length(AchievementEntries.ENTERED_LOCATIONS, ch, 5)),
    ("speaker", "speak 10 times",
     lambda ch: CheckHelper.check_min_number(AchievementEntries.TEXTS_SPOKEN, ch, 10)),
    ("whisperer", "whisper to 3 people",
     lambda ch: CheckHelper.check_list_min_length(AchievementEntries.WHISPERS, ch, 3)),
    ("potato_eater", "eat 2 potatoes",
     lambda ch: CheckHelper.check_min_number(AchievementEntries.EATEN_POTATOES, ch, 2)),
]


def check_achievement_progress(player):
    for achievement in achievements:
        for character in player.alive_characters:
            if achievement[2](character):
                if not models.Achievement.query.filter_by(achiever=player, achievement=achievement[0]).first():
                    db.session.add(models.Achievement(player, achievement[0]))
                    notification = models.Notification("achievement_unlocked", {"name": achievement[0]}, "well_done",
                                                       {}, player=player)
                    db.session.add(notification)
                    main.call_hook(main.Hooks.NEW_CHARACTER_NOTIFICATION, character=character, notification=notification)


class ProgressHelper:
    @staticmethod
    def add_to_set(name, character, element_to_add):
        existing = ACProgress.query.filter_by(name=name, character=character).first()
        if not existing:
            new_entry = ACProgress(name, character, [element_to_add])
            db.session.add(new_entry)
            return True

        elements_set = set(existing.details)
        old_len = len(elements_set)
        elements_set.add(element_to_add)
        existing.details = list(elements_set)

        return old_len == len(elements_set)  # check if set was really changed

    @staticmethod
    def increment_counter(name, character, by_value=1):
        existing = ACProgress.query.filter_by(name=name, character=character).first()
        if not existing:
            new_entry = ACProgress(name, character, by_value)
            db.session.add(new_entry)
            return True

        existing.details += by_value
        return True  # always changed


@hook(main.Hooks.LOCATION_ENTERED)
def on_location_entered(*, character, from_loc, to_loc):
    changed = ProgressHelper.add_to_set(AchievementEntries.ENTERED_LOCATIONS, character, to_loc.id)
    if changed:
        check_achievement_progress(character.player)


@hook(main.Hooks.SPOKEN_ALOUD)
def on_spoken_aloud(*, character):
    changed = ProgressHelper.increment_counter(AchievementEntries.TEXTS_SPOKEN, character)
    if changed:
        check_achievement_progress(character.player)


@hook(main.Hooks.WHISPERED)
def on_whispered(*, character, to_character):
    changed = ProgressHelper.add_to_set(AchievementEntries.WHISPERS, character, to_character.id)
    if changed:
        check_achievement_progress(character.player)


@hook(main.Hooks.EATEN)
def on_eaten(*, character, item, amount):
    if item.type_name == "potatoes":
        changed = ProgressHelper.increment_counter(AchievementEntries.EATEN_POTATOES, character, amount)
        if changed:
            check_achievement_progress(character.player)

