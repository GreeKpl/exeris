import math
from statistics import mean

import sqlalchemy as sql
from flask import logging
from shapely.geometry import Point
from sqlalchemy import func

from exeris.core import deferred, main, util
from exeris.core import models, general, properties, recipes
from exeris.core.deferred import convert
from exeris.core.main import db, Events
from exeris.core.properties import P

logger = logging.getLogger(__name__)


class AbstractAction:
    """
    Top-level class in the action system. It represents a serializable in-game operation that leads to a change
    of the game state. It can have a specific executor (e.g. a character dropping an item) or not.

    All classes subclassing AbstactAction should implement method perform_action.
    """

    def perform(self):
        logger.info("Perform %s for arguments: %s", self.__class__.__name__, str(vars(self)))
        return self.perform_action()

    def perform_action(self):
        pass


class PlayerAction(AbstractAction):
    """
    A top-level player action. All we know is that it's done by a player (not their character)
    """

    def __init__(self, player):
        self.player = player


class Action(AbstractAction):
    """
    A top-level character action. All we know is that it's done by a character
    """

    def __init__(self, executor):
        self.executor = executor


# rich collection of pre-configured actions
class ActionOnSelf(Action):
    def __init__(self, executor, rng=None):
        super().__init__(executor)
        self.rng = rng
        if not rng:
            self.rng = general.SameLocationRange()


class ActionOnEntity(Action):
    def __init__(self, executor, entity, rng=None):
        super().__init__(executor)
        self.entity = entity
        if not rng:
            rng = general.SameLocationRange()
        self.rng = rng


class ActionOnItem(ActionOnEntity):
    def __init__(self, executor, item, rng=None):
        super().__init__(executor, item, rng)
        self.item = item


class ActionOnCharacter(ActionOnEntity):
    def __init__(self, executor, character, rng=None):
        super().__init__(executor, character, rng)
        self.character = character


class ActionOnLocation(ActionOnEntity):
    def __init__(self, executor, location, rng=None):
        super().__init__(executor, location, rng)
        self.location = location


class ActionOnActivity(ActionOnEntity):
    def __init__(self, executor, activity, rng=None):
        super().__init__(executor, activity, rng)
        self.activity = activity


class ActionOnItemAndActivity(Action):
    def __init__(self, executor, item, activity, rng=None):
        super().__init__(executor)
        self.item = item
        self.activity = activity
        self.rng = rng
        if not rng:
            self.rng = general.SameLocationRange()


class ActionOnItemAndCharacter(Action):
    def __init__(self, executor, item, character, rng=None):
        super().__init__(executor)
        self.item = item
        self.character = character
        self.rng = rng
        if not rng:
            self.rng = general.SameLocationRange()


####################
# ACTIVITY ACTIONS #
####################

class ActivityAction(AbstractAction):
    pass


def form_on_setup(**kwargs):  # adds a field "_form_input" to a class so it can be later used
    def f(clazz):
        clazz._form_inputs = kwargs
        return clazz

    return f


def set_visible_material(activity, visible_material, entity):
    visible_material_property = {}
    for place_to_show in visible_material:
        group_name = visible_material[place_to_show]
        req_input = activity.requirements["input"]
        for req_material_name, req_material in req_input.items():  # forall requirements
            real_used_type_name = req_material["used_type"]
            if group_name == req_material_name:  # this group is going to be shown by our visible material
                visible_material_property[place_to_show] = real_used_type_name
    entity.properties.append(models.EntityProperty(P.VISIBLE_MATERIAL, visible_material_property))


@form_on_setup(amount=recipes.AmountInput)
class CreateItemAction(ActivityAction):
    @convert(item_type=models.ItemType)
    def __init__(self, *, item_type, properties, used_materials, amount=1, visible_material=None, **injected_args):
        self.item_type = item_type
        self.activity = injected_args["activity"]
        self.initiator = injected_args["initiator"]
        self.amount = amount
        self.used_materials = used_materials
        self.injected_args = injected_args
        self.properties = properties
        self.visible_material = visible_material if visible_material else {}

    def perform_action(self):

        result_loc = self.activity.being_in.being_in

        if self.item_type.portable and self.initiator.being_in == result_loc:  # if being in the same location then go to inventory
            result_loc = self.initiator

        new_items = []
        if self.item_type.stackable:  # create one item with specified 'amount'
            weight = self.amount * self.item_type.unit_weight
            new_items += [self.create_item(result_loc, weight)]
        else:  # create 'amount' of single items
            for _ in range(self.amount):
                new_items += [self.create_item(result_loc, self.item_type.unit_weight)]

        return new_items

    def create_item(self, result_loc, item_weight):
        new_item = models.Item(self.item_type, result_loc, weight=item_weight)
        db.session.add(new_item)
        for property_name in self.properties:
            new_item.properties.append(models.EntityProperty(property_name, self.properties[property_name]))
        if self.used_materials == "all":  # all the materials used for an activity were set to build this item
            for material_type in models.Item.query.filter(models.Item.is_used_for(self.activity)).all():
                material_type.used_for = new_item
        else:  # otherwise it's a dict and we need to look into it
            for material_type_name in self.used_materials:
                self.extract_used_material(material_type_name, new_item)
        if self.visible_material:
            set_visible_material(self.activity, self.visible_material, new_item)
        return new_item

    def extract_used_material(self, material_type_name, new_item):
        for req_material_name, requirement_params in self.activity.requirements.get("input",
                                                                                    {}).items():  # forall requirements
            req_used_type_name = requirement_params["used_type"]
            if req_material_name == material_type_name:  # req is fulfilled by material
                real_material_type = models.ItemType.by_name(req_used_type_name)
                required_material_type = models.EntityType.by_name(req_material_name)

                amount = requirement_params["needed"] / required_material_type.quantity_efficiency(real_material_type)

                item = models.Item.query.filter_by(type=real_material_type).one()
                move_entity_between_entities(item, item.used_for, new_item, amount, to_be_used_for=True)


class RemoveItemAction(ActivityAction):
    @convert(item=models.Item)
    def __init__(self, item, gracefully=True):
        self.item = item
        self.gracefully = gracefully

    def perform_action(self):
        self.item.remove(self.gracefully)


class RemoveActivityContainerAction(ActivityAction):
    def __init__(self, activity, **injected_args):
        self.activity = activity
        self.injected_args = injected_args

    def perform_action(self):
        self.activity.being_in.remove(True)


class CreateLocationAction(ActivityAction):
    @convert(location_type=models.LocationType)
    def __init__(self, *, location_type, used_materials, properties, visible_material=None, **injected_args):
        self.location_type = location_type
        self.used_materials = used_materials
        self.activity = injected_args["activity"]
        self.initiator = injected_args["initiator"]
        self.injected_args = injected_args
        self.properties = properties
        self.visible_material = visible_material if visible_material else {}

    def perform_action(self):
        result_loc = self.activity.being_in.being_in

        new_location = models.Location(result_loc, self.location_type)
        for prop_name, prop_value in self.properties.items():
            new_location.properties.append(models.EntityProperty(prop_name, prop_value))

        if self.used_materials == "all":  # all the materials used for an activity were set to build this item
            for material in models.Item.query.filter(models.Item.is_used_for(self.activity)).all():
                material.used_for = new_location
        # TODO what if used_materials is not all?

        if self.visible_material:
            set_visible_material(self.activity, self.visible_material, new_location)

        db.session.add(new_location)

        return [new_location]


@form_on_setup(entity_name=recipes.NameInput)
class AddNameToEntityAction(ActivityAction):
    def __init__(self, *, entity_name, results_index=-1, **injected_args):
        self.entity_name = entity_name
        self.entities = injected_args["resulting_entities"][results_index]

    def perform_action(self):
        for entity in self.entities:
            entity.title = self.entity_name


##############################
#      SCHEDULER ACTIONS     #
##############################


class ProcessAction(AbstractAction):
    """
    Process is a top-level class which is subclasses by all processes run by the scheduler.
    """
    pass


class TravelProcess(ProcessAction):
    SCHEDULER_RUNNING_INTERVAL = 10 * general.GameDate.SEC_IN_MIN

    def __init__(self):
        pass

    def perform_action(self):
        travel_intents = models.EntityIntent.query.filter_by(type=main.Intents.TRAVEL).order_by(
            models.EntityIntent.priority.desc()).all()

        for travel_intent in travel_intents:
            # really it shouldn't move anything, it should store intermediate data about direction and speed for each
            # RootLocation, because there can be multi-location vehicles.
            # But there can also be 2 separate veh in one RootLocation
            action_to_perform = deferred.call(travel_intent.action)
            try:
                action_to_perform.perform()
            except:
                logger.warn("Unable to perform action %s", str(action_to_perform.__class__), exc_info=True)


def move_entity_to_position(entity, direction, target_position):
    entity_root = entity.get_root()

    if entity_root.is_empty(excluding=[entity]):
        # nothing else, so we can move this RootLocation
        entity_root.position = target_position
        entity_root.direction = direction
    else:
        new_root_location = models.RootLocation(target_position, direction)
        db.session.add(new_root_location)
        entity.being_in = new_root_location
        main.call_hook(main.Hooks.ENTITY_CONTENTS_COUNT_DECREASED, entity=entity)


class TravelInDirectionProcess(ProcessAction):
    @convert(entity=models.Entity)
    def __init__(self, entity, direction):
        self.entity = entity
        self.direction = direction

    def perform_action(self):
        speed = self.entity.get_max_speed()

        initial_pos = self.entity.get_root().position

        ticks_per_day = general.GameDate.SEC_IN_DAY / TravelProcess.SCHEDULER_RUNNING_INTERVAL
        speed_per_tick = speed / ticks_per_day

        max_potential_distance = speed_per_tick * general.LandTraversabilityBasedRange.MAX_RANGE_MULTIPLIER

        rng = general.LandTraversabilityBasedRange(speed_per_tick)
        travel_distance_per_tick = rng.get_maximum_range_from_estimate(initial_pos, self.direction, speed_per_tick,
                                                                       max_potential_distance)

        destination_pos = util.pos_for_distance_in_direction(initial_pos, self.direction, travel_distance_per_tick)

        logger.info("Travel of %s from %s to %s [speed: %s]", self.entity, initial_pos, destination_pos, speed_per_tick)

        move_entity_to_position(self.entity, self.direction, destination_pos)
        return False


class ActivitiesProgressProcess(ProcessAction):
    def __init__(self):
        pass

    def perform_action(self):
        activities = models.Activity.query.all()
        for activity in activities:
            activity_progress = SingleActivityProgressProcess(activity)
            activity_progress.perform()


class SingleActivityProgressProcess(ProcessAction):
    DEFAULT_PROGRESS = 5.0

    def __init__(self, activity):
        self.activity = activity
        self.entity_worked_on = self.activity.being_in
        self.tool_based_quality = []
        self.machine_based_quality = []
        self.progress_ratio = 0.0

    def perform_action(self):
        logger.info("progress of %s", self.activity)
        workers = models.Character.query.filter_by(activity=self.activity).all()

        try:
            req = self.activity.requirements

            if "mandatory_machines" in req:
                logger.info("checking mandatory_machines")
                self.check_mandatory_machines(req["mandatory_machines"])

            if "optional_machines" in req:
                logger.info("checking optional_machines")
                self.check_optional_machines(req["optional_machines"])

            if "targets" in req:
                logger.info("checking targets")
                self.check_target_proximity(req["targets"])

            if "target_with_properties" in req:
                pass

            if "input" in req:
                self.check_input_requirements(req["input"])

            active_workers = []
            for worker in workers:
                self.check_worker_proximity(self.activity, worker)

                if "mandatory_tools" in req:
                    self.check_mandatory_tools(worker, req["mandatory_tools"])

                if "optional_tools" in req:
                    self.check_optional_tools(worker, req["optional_tools"])

                if "skill" in req:
                    self.check_skills(worker, req["skills"].items()[0])

                self.progress_ratio += SingleActivityProgressProcess.DEFAULT_PROGRESS
                active_workers.append(worker)

            if "max_workers" in req:
                self.check_min_workers(active_workers, req["min_workers"])

            if "min_workers" in req:
                self.check_max_workers(active_workers, req["max_workers"])

            self.activity.ticks_left -= self.progress_ratio

            if len(self.tool_based_quality):
                self.activity.quality_sum += mean(self.tool_based_quality)
                self.activity.quality_ticks += 1

            if len(self.machine_based_quality):
                self.activity.quality_sum += mean(self.machine_based_quality)
                self.activity.quality_ticks += 1

            for group, params in req.get("input", {}).items():
                if "quality" in params:
                    self.activity.quality_sum += params["quality"]
                    self.activity.quality_ticks += 1

        except Exception as e:
            logger.error("Error processing activity %s", str(self.activity), e)

        if self.activity.ticks_left <= 0:
            self.finish_activity(self.activity)

    def check_worker_proximity(self, activity, worker):
        rng = general.SameLocationRange()

        if not worker.has_access(activity, rng=rng):
            raise main.TooFarFromActivityException(activity=activity)

    def check_input_requirements(self, materials):
        for name, material in materials.items():
            if material["left"] > 0:
                raise main.NoInputMaterialException(item_type=models.EntityType.by_name(name))

    def check_mandatory_tools(self, worker, tools):
        for tool_type_name in tools:
            group = models.EntityType.by_name(tool_type_name)
            type_eff_pairs = group.get_descending_types()
            allowed_types = [pair[0] for pair in type_eff_pairs]

            tools = general.ItemQueryHelper.query_all_types_in(allowed_types, worker).all()
            if not tools:
                raise main.NoToolForActivityException(tool_name=group.name)

            tool_best_relative_quality = self._get_most_efficient_item_relative_quality(tools, type_eff_pairs)

            # tool quality affects quality of activity result
            self.tool_based_quality += [tool_best_relative_quality]

    def check_optional_tools(self, worker, tools_progress_bonus):
        for tool_type_name in tools_progress_bonus:
            group = models.EntityType.by_name(tool_type_name)
            type_eff_pairs = group.get_descending_types()
            allowed_types = [pair[0] for pair in type_eff_pairs]

            tools = general.ItemQueryHelper.query_all_types_in(allowed_types, worker).all()
            if not tools:
                continue

            tool_best_relative_quality = self._get_most_efficient_item_relative_quality(tools, type_eff_pairs)

            # quality affects only progress ratio increased
            self.progress_ratio += tools_progress_bonus[tool_type_name] * tool_best_relative_quality

    def _get_most_efficient_item_relative_quality(self, tools, type_eff_pairs):
        efficiency_of_type = {pair[0]: pair[1] for pair in type_eff_pairs}
        relative_quality = lambda item: efficiency_of_type[item.type] * item.quality

        sorted_by_quality = sorted(tools, key=relative_quality, reverse=True)
        most_efficient_tool = sorted_by_quality[0]
        return relative_quality(most_efficient_tool)

    def check_mandatory_machines(self, machines):
        for machine_name in machines:
            group = models.EntityType.by_name(machine_name)
            type_eff_pairs = group.get_descending_types()
            allowed_types = [pair[0] for pair in type_eff_pairs]

            machines = general.ItemQueryHelper.query_all_types_near(allowed_types, self.entity_worked_on.being_in).all()
            if not machines:
                raise main.NoMachineForActivityException(machine_name=group.name)

            machine_best_relative_quality = self._get_most_efficient_item_relative_quality(machines, type_eff_pairs)

            # machine quality affects quality of activity result
            self.machine_based_quality += [machine_best_relative_quality]

    def check_optional_machines(self, machine_progress_bonus):
        for machine_type_name in machine_progress_bonus:
            group = models.EntityType.by_name(machine_type_name)
            type_eff_pairs = group.get_descending_types()
            allowed_types = [pair[0] for pair in type_eff_pairs]

            machines = general.ItemQueryHelper.query_all_types_near(allowed_types, self.entity_worked_on.being_in).all()
            if not machines:
                continue

            machine_best_relative_quality = self._get_most_efficient_item_relative_quality(machines, type_eff_pairs)

            # quality affects only progress ratio increased
            self.progress_ratio += machine_progress_bonus[machine_type_name] * machine_best_relative_quality

    def finish_activity(self, activity):
        logger.info("Finishing activity %s", activity)
        entities_lists = []
        for serialized_action in activity.result_actions:
            logger.debug("executing action: %s", serialized_action)
            action = deferred.call(serialized_action, activity=activity, initiator=activity.initiator,
                                   resulting_entities=entities_lists)

            returned_entities = action.perform()

            entities_lists.append(
                returned_entities if returned_entities else [])  # always add a list (even if it's empty)

        db.session.delete(activity)

    def check_target_proximity(self, target_ids):
        targets = models.Entity.query.filter(models.Entity.id.in_(target_ids)).all()
        for target in targets:
            rng = general.SameLocationRange()
            if not rng.is_near(self.entity_worked_on, target):
                raise main.ActivityTargetTooFarAwayException(entity=target)

    def check_min_workers(self, active_workers, min_number):
        if len(active_workers) < min_number:
            raise main.TooFewParticipantsException(min_number=min_number)

    def check_max_workers(self, active_workers, max_number):
        if len(active_workers) > max_number:
            raise main.TooManyParticipantsException(max_number=max_number)

    def check_skills(self, worker, skill):
        skill_name = skill[0]
        min_skill_value = skill[1]

        if worker.get_skill_factor(skill_name) < min_skill_value:
            raise main.TooLowSkillException(skill_name=skill_name, required_level=min_skill_value)


class EatingProcess(ProcessAction):
    HUNGER_INCREASE = 0.1
    HUNGER_MAX_DECREASE = -0.2
    FOOD_BASED_ATTR_DECAY = 0.005
    FOOD_BASED_ATTR_MAX_POSSIBLE_INCREASE = 0.01

    @staticmethod
    def bonus_mult(vals):
        return 1 + max(0, (sum(vals) / EatingProcess.FOOD_BASED_ATTR_MAX_POSSIBLE_INCREASE - 1) * 0.3)

    def perform_action(self):
        characters = models.Character.query.all()

        for character in characters:
            character.hunger += EatingProcess.HUNGER_INCREASE

            eating_queue = character.eating_queue

            hunger_attr_points = eating_queue.get("hunger")
            if hunger_attr_points:
                character.hunger += max(hunger_attr_points, EatingProcess.HUNGER_MAX_DECREASE)
                eating_queue["hunger"] -= max(hunger_attr_points, EatingProcess.HUNGER_MAX_DECREASE)

            attributes_to_increase = {}
            for attribute in properties.EdiblePropertyType.FOOD_BASED_ATTR:
                setattr(character, attribute, getattr(character, attribute) - EatingProcess.FOOD_BASED_ATTR_DECAY)

                queue_attr_points = eating_queue.get(attribute, 0)
                increase = min(queue_attr_points, EatingProcess.FOOD_BASED_ATTR_MAX_POSSIBLE_INCREASE)
                attributes_to_increase[attribute] = increase
                eating_queue[attribute] = eating_queue.get(attribute, 0) - increase

            for attribute, increase in attributes_to_increase.items():
                setattr(character, attribute, getattr(character, attribute) + increase * EatingProcess.bonus_mult(
                    attributes_to_increase.values()))
            character.eating_queue = eating_queue


class DecayProcess(ProcessAction):
    DAILY_STACKABLE_DECAY_FACTOR = 0.01
    SCHEDULER_RUNNING_INTERVAL = general.GameDate.SEC_IN_DAY

    def perform_action(self):
        self.degrade_items()

        self.decay_progress_of_activities()

        self.decay_abandoned_activities()

    def degrade_items(self):
        items_and_props = db.session.query(models.Item, models.EntityTypeProperty).join(models.ItemType).filter(
            sql.and_(models.ItemType.name == models.EntityTypeProperty.type_name,  # ON clause
                     models.Item.role == models.Item.ROLE_BEING_IN,
                     models.EntityTypeProperty.name == P.DEGRADABLE)).all()  # handle all items
        for item, degradable_prop in items_and_props:
            item_lifetime = degradable_prop.data["lifetime"]
            damage_fraction_to_add_since_last_tick = DecayProcess.SCHEDULER_RUNNING_INTERVAL / item_lifetime
            item.damage += damage_fraction_to_add_since_last_tick

            if item.damage == 1.0:
                if item.type.stackable:
                    self.decay_stackable_item(item)
                else:
                    self.crumble_item(item)

    def decay_stackable_item(self, item):
        runs_per_day = DecayProcess.SCHEDULER_RUNNING_INTERVAL / general.GameDate.SEC_IN_DAY
        amount_left_fraction = (1 - DecayProcess.DAILY_STACKABLE_DECAY_FACTOR / runs_per_day)
        item.amount = util.round_probabilistic(item.amount * amount_left_fraction)

    def crumble_item(self, item):
        item.remove()

    def decay_progress_of_activities(self):
        # damage level for Activities is altered ONLY in ActivitiesProgressProcess
        activities = models.Activity.query.filter(models.Activity.ticks_left < models.Activity.ticks_needed).all()
        for activity in activities:  # decrease progress
            activity.ticks_left += min(SingleActivityProgressProcess.DEFAULT_PROGRESS, activity.ticks_needed)

    def decay_abandoned_activities(self):
        # activities abandoned for a long time
        activities = models.Activity.query.filter_by(damage=1.0) \
            .filter(models.Activity.ticks_left == models.Activity.ticks_needed).all()
        for activity in activities:
            items_and_props = db.session.query(models.Item, models.EntityTypeProperty).join(models.ItemType).filter(
                sql.and_(models.ItemType.name == models.EntityTypeProperty.type_name,  # ON clause
                         models.Item.is_used_for(activity),
                         models.EntityTypeProperty.name == P.DEGRADABLE)).all()  # handle all normal stackables
            for item, degradable_prop in items_and_props:
                item_lifetime = degradable_prop.data["lifetime"]
                damage_fraction_to_add_since_last_tick = DecayProcess.SCHEDULER_RUNNING_INTERVAL / item_lifetime
                item.damage += damage_fraction_to_add_since_last_tick

                if item.damage == 1.0:
                    if item.type.stackable:
                        previous_amount = item.amount
                        self.decay_stackable_item(item)
                        amount_to_be_removed = previous_amount - item.amount
                        self.update_activity_requirements(activity, amount_to_be_removed, item)
                    else:
                        self.crumble_item(item)
                        self.update_activity_requirements(activity, 1, item)

    def update_activity_requirements(self, activity, amount_to_be_removed, item):
        input_req = activity.requirements.get("input", {})
        # one item type can be used in many groups
        for group_name, requirement_params in sorted(input_req.items()):  # deterministic order
            if "used_type" in requirement_params and requirement_params["used_type"] == item.type_name:
                item_to_group_multiplier = models.EntityType.by_name(group_name).quantity_efficiency(
                    models.EntityType.by_name(requirement_params["used_type"]))
                units_used = requirement_params["needed"] - requirement_params["left"]
                units_of_group_to_be_removed = math.ceil(amount_to_be_removed * item_to_group_multiplier)
                requirement_params["left"] += min(units_of_group_to_be_removed, units_used)
                amount_which_was_just_removed = min(units_of_group_to_be_removed, units_used) / item_to_group_multiplier
                amount_to_be_removed -= min(amount_which_was_just_removed, amount_to_be_removed)

                if requirement_params["needed"] == requirement_params["left"]:
                    del requirement_params["used_type"]  # allow any type to fulfill the group

        activity.requirements = dict(activity.requirements)  # FORCE refresh


#

##############################
#   PLAYER-SPECIFIC ACTIONS  #
##############################


#

class CreateCharacterAction(PlayerAction):
    def __init__(self, player, character_name, sex, language):
        super().__init__(player)
        self.character_name = character_name
        self.sex = sex
        self.language = language

    def perform_action(self):
        loc = models.RootLocation.query.order_by(func.random()).first()
        new_char = models.Character(self.character_name, self.sex, self.player, self.language,
                                    general.GameDate.now(), loc.position, loc)
        db.session.add(new_char)

        return new_char


#


##############################
# CHARACTER-SPECIFIC ACTIONS #
##############################


def move_entity_between_entities(entity, source, destination, amount=1, to_be_used_for=False):
    if entity.parent_entity == source:

        assert isinstance(entity, models.Entity) and not isinstance(entity,
                                                                    models.Location), "moving locations not supported"

        if isinstance(entity, models.Item) and entity.type.stackable:
            weight = amount * entity.type.unit_weight
            move_stackable_resource(entity, source, destination, weight, to_be_used_for)
        elif to_be_used_for:
            entity.used_for = destination
        else:
            entity.being_in = destination
        main.call_hook(main.Hooks.ENTITY_CONTENTS_COUNT_DECREASED, entity=source)
    else:
        raise main.InvalidInitialLocationException(entity=entity)


def move_stackable_resource(item, source, goal, weight, to_be_used_for=False):
    # remove from the source
    if item.weight == weight:
        item.remove()
    else:
        item.weight -= weight

    # add to the goal
    if to_be_used_for:
        existing_pile = models.Item.query.filter_by(type=item.type) \
            .filter(models.Item.is_used_for(goal)).filter_by(visible_parts=item.visible_parts).first()
    else:
        existing_pile = models.Item.query.filter_by(type=item.type). \
            filter(models.Item.is_in(goal)).filter_by(visible_parts=item.visible_parts).first()

    if existing_pile:
        existing_pile.weight += weight
    else:
        new_pile = models.Item(item.type, goal, weight=weight, role_being_in=not to_be_used_for)
        new_pile.visible_parts = item.visible_parts
        db.session.add(new_pile)


def overwrite_item_amount(item, amount):
    if item.type.stackable:
        return dict(item_amount=amount)
    return {}


class DropItemAction(ActionOnItem):
    def __init__(self, executor, item, amount=1):
        super().__init__(executor, item)
        self.amount = amount

    def perform_action(self):
        if not self.executor.has_access(self.item, rng=general.InsideRange()):
            raise main.EntityNotInInventoryException(entity=self.item)

        if self.amount > self.item.amount:
            raise main.InvalidAmountException(amount=self.amount)

        move_entity_between_entities(self.item, self.executor, self.executor.being_in, self.amount)

        event_args = self.item.pyslatize(**overwrite_item_amount(self.item, self.amount))

        general.EventCreator.base(Events.DROP_ITEM, self.rng, event_args, self.executor)


class TakeItemAction(ActionOnItem):
    EXCEPTIONS_CREATING_INTENT = {
        main.Intents.TRAVEL: [main.EntityTooFarAwayException]
    }

    def __init__(self, executor, item, amount=1):
        super().__init__(executor, item)
        self.amount = amount

    def perform_action(self):
        if not self.executor.has_access(self.item, rng=general.SameLocationRange()):
            raise main.EntityTooFarAwayException(entity=self.item)

        if self.amount < 0 or self.amount > self.item.amount:
            raise main.InvalidAmountException(amount=self.amount)

        move_entity_between_entities(self.item, self.executor.being_in, self.executor, self.amount)

        event_args = self.item.pyslatize(**overwrite_item_amount(self.item, self.amount))
        general.EventCreator.base(Events.TAKE_ITEM, self.rng, event_args, self.executor)


class GiveItemAction(ActionOnItemAndCharacter):
    def __init__(self, executor, item, receiver, amount=1):
        super().__init__(executor, item, receiver)
        self.amount = amount

    def perform_action(self):
        if not self.executor.has_access(self.item, rng=general.InsideRange()):
            raise main.EntityNotInInventoryException(entity=self.item)

        if self.amount > self.item.amount:
            raise main.InvalidAmountException(amount=self.amount)

        if not self.character:  # has not enough space in inventory
            raise main.OwnInventoryExceededException()

        move_entity_between_entities(self.item, self.executor, self.character, self.amount)

        event_args = self.item.pyslatize(**overwrite_item_amount(self.item, self.amount))
        general.EventCreator.base(Events.GIVE_ITEM, self.rng, event_args,
                                  self.executor, self.character)


class AddEntityToActivityAction(ActionOnItemAndActivity):
    def __init__(self, executor, item, activity, amount):
        super().__init__(executor, item, activity)
        self.amount = amount

    def perform_action(self):

        if not self.executor.has_access(self.item, rng=general.SameLocationRange()):
            raise main.EntityNotInInventoryException(entity=self.item)

        if not self.executor.has_access(self.activity, rng=general.SameLocationRange()):
            raise main.TooFarFromActivityException(activity=self.activity)

        if self.amount > self.item.amount:
            raise main.InvalidAmountException(amount=self.amount)

        req = self.activity.requirements

        for required_group_name, required_group_params in sorted(req.get("input", {}).items()):  # TODO make it prettier
            required_group = models.EntityType.by_name(required_group_name)
            if "used_type" in required_group_params:
                if required_group_params["used_type"] != self.item.type_name:  # must be exactly the same type
                    raise main.OnlySpecificTypeForGroupException(
                        type_name=required_group_params["used_type"], group_name=required_group_name)
            if required_group_params["left"] == 0:  # this requirement is fulfilled
                continue
            if not required_group.contains(self.item.type):  # requirement cannot be fulfilled by this type
                continue
            type_efficiency_ratio = required_group.quantity_efficiency(self.item.type)
            max_to_be_added = math.ceil(required_group_params["left"] / type_efficiency_ratio)
            amount_to_add = min(self.amount, max_to_be_added)

            source = self.item.being_in  # on ground
            if self.item.being_in == self.executor:  # in inventory
                source = self.executor

            move_entity_between_entities(self.item, source, self.activity, amount_to_add, to_be_used_for=True)

            material_left_reduction = amount_to_add * type_efficiency_ratio

            required_group_params["left"] = max(0, required_group_params["left"] - material_left_reduction)
            required_group_params["used_type"] = self.item.type_name
            if not self.item.type.stackable:  # non-stackables affect quality
                added_to_needed_fraction = material_left_reduction / required_group_params["needed"]
                total_item_quality = required_group.quality_efficiency(self.item.type) * self.item.quality
                required_group_params["quality"] = (total_item_quality * added_to_needed_fraction) \
                                                   + required_group_params.get("quality", 0)

            overwrites = {}
            if self.item.type.stackable:
                overwrites["item_amount"] = amount_to_add

            item_info = self.item.pyslatize(**overwrite_item_amount(self.item, amount_to_add))
            event_args = {"groups": {
                "item": item_info,
                "activity": self.activity.pyslatize()
            }}
            general.EventCreator.base(Events.ADD_TO_ACTIVITY, self.rng, event_args, doer=self.executor)
            break
        else:
            raise main.ItemNotApplicableForActivityException(item=self.item, activity=self.activity)

        self.activity.requirements = {}  # TODO CATASTROPHE
        db.session.flush()
        self.activity.requirements = req


class EatAction(ActionOnItem):
    def __init__(self, executor, item, amount):
        super().__init__(executor, item, rng=general.VisibilityBasedRange(20))
        self.amount = amount

    def perform_action(self):

        if not self.executor.has_access(self.item, rng=general.LandTraversabilityBasedRange(10)):
            raise main.EntityTooFarAwayException(entity=self.item)

        if self.item.amount < self.amount:
            raise main.InvalidAmountException(amount=self.amount)

        if self.item.get_max_edible(self.executor) < self.amount:
            raise main.InvalidAmountException(amount=self.amount)

        self.item.amount -= self.amount

        self.item.eat(self.executor, self.amount)

        food_item_info = self.item.pyslatize(item_amount=self.amount, detailed=False)
        general.EventCreator.base(Events.EAT, self.rng, {"groups": {"food": food_item_info}}, doer=self.executor)

        main.call_hook(main.Hooks.EATEN, character=self.executor, item=self.item, amount=self.amount)


class SayAloudAction(ActionOnSelf):
    def __init__(self, executor, message):
        super().__init__(executor, rng=general.VisibilityBasedRange(20))
        self.message = message

    def perform_action(self):
        general.EventCreator.base(Events.SAY_ALOUD, self.rng, {"message": self.message}, doer=self.executor)

        main.call_hook(main.Hooks.SPOKEN_ALOUD, character=self.executor)


class SpeakToSomebodyAction(ActionOnCharacter):
    def __init__(self, executor, character, message):
        super().__init__(executor, character, rng=general.VisibilityBasedRange(20))
        self.message = message

    def perform_action(self):
        if not self.executor.has_access(self.character, rng=general.VisibilityBasedRange(20)):
            raise main.EntityTooFarAwayException(entity=self.character)

        general.EventCreator.base(Events.SPEAK_TO_SOMEBODY, self.rng, {"message": self.message}, doer=self.executor,
                                  target=self.character)


class WhisperToSomebodyAction(ActionOnCharacter):
    def __init__(self, executor, character, message):
        super().__init__(executor, character, rng=general.VisibilityBasedRange(20))
        self.message = message

    def perform_action(self):
        if not self.executor.has_access(self.character, rng=general.SameLocationRange()):
            raise main.EntityTooFarAwayException(entity=self.character)

        general.EventCreator.base(Events.WHISPER, self.rng, {"message": self.message}, doer=self.executor,
                                  target=self.character)

        main.call_hook(main.Hooks.WHISPERED, character=self.executor, to_character=self.character)


class JoinActivityAction(ActionOnActivity):
    def __init__(self, executor, activity):
        super().__init__(executor, activity, rng=None)

    def perform_action(self):
        if not self.executor.has_access(self.activity, rng=general.SameLocationRange()):
            raise main.TooFarFromActivityException(activity=self.activity)

        self.executor.activity = self.activity


class MoveToLocationAction(ActionOnLocation):
    def __init__(self, executor, passage):
        if executor.being_in == passage.left_location:
            location = passage.right_location
        else:
            location = passage.left_location
        super().__init__(executor, location, rng=general.SameLocationRange())
        self.passage = passage

    def perform_action(self):

        # TODO check if passage is locked

        if not self.executor.has_access(self.passage, rng=general.SameLocationRange()):
            raise main.EntityTooFarAwayException(entity=self.location)

        from_loc = self.executor.being_in
        if not self.passage.between(from_loc, self.location):
            raise main.EntityTooFarAwayException(entity=self.location)  # TODO Better event?

        general.EventCreator.base(Events.MOVE, self.rng, {"groups": {"from": from_loc.pyslatize(),
                                                                     "destination": self.location.pyslatize()}},
                                  doer=self.executor)

        self.executor.being_in = self.location

        general.EventCreator.create(rng=general.SameLocationRange(), tag_observer=Events.MOVE + "_observer",
                                    params={"groups": {"from": from_loc.pyslatize(),
                                                       "destination": self.location.pyslatize()}},
                                    doer=self.executor)

        main.call_hook(main.Hooks.LOCATION_ENTERED, character=self.executor, from_loc=from_loc, to_loc=self.location)


class ToggleCloseableAction(ActionOnEntity):
    def __init__(self, executor, closeable_entity):
        super().__init__(executor, closeable_entity)

    def perform_action(self):

        # TODO check if entity is locked

        if not self.executor.has_access(self.entity, rng=general.SameLocationRange()):
            raise main.EntityTooFarAwayException(entity=self.entity)

        closeable_prop = self.entity.get_property(P.CLOSEABLE)
        going_to_open = closeable_prop["closed"]
        self.entity.alter_property(P.CLOSEABLE, {"closed": not going_to_open})

        if going_to_open:
            event_name = Events.OPEN_ENTITY
        else:
            event_name = Events.CLOSE_ENTITY

        general.EventCreator.base(event_name, self.rng, {"groups": {"entity": self.entity.pyslatize()}},
                                  doer=self.executor)


class DeathAction(Action):
    def __init__(self, executor):
        super().__init__(executor)

    def turn_into_body(self):
        self.executor.type = models.EntityType.by_name(main.Types.DEAD_CHARACTER)

    @staticmethod
    def create_death_info_property():
        return models.EntityProperty(P.DEATH_INFO,
                                     {"date": general.GameDate.now().game_timestamp})


class DeathOfStarvationAction(DeathAction):
    def __init__(self, executor):
        super().__init__(executor)

    def perform_action(self):
        general.EventCreator.base(main.Events.DEATH_OF_STARVATION, rng=general.VisibilityBasedRange(30),
                                  doer=self.executor)

        death_prop = self.create_death_info_property()
        death_prop.data["cause"] = models.Character.DEATH_STARVATION
        self.executor.properties.append(death_prop)
        self.turn_into_body()


class DeathOfDamageAction(DeathAction):
    def __init__(self, executor, killer, weapon):  # apparently, executor is the executed character ;)
        super().__init__(executor)
        self.killer = killer
        self.weapon = weapon

    def perform_action(self):
        general.EventCreator.base(main.Events.DEATH_OF_DAMAGE, rng=general.VisibilityBasedRange(30), doer=self.executor,
                                  params=dict(killer=self.killer, weapon=self.weapon))

        death_prop = self.create_death_info_property()
        death_prop.data["cause"] = models.Character.DEATH_WEAPON
        death_prop.data["weapon"] = self.weapon.type.name
        death_prop.data["killer_id"] = self.killer.id
        self.executor.properties.append(death_prop)
        self.turn_into_body()
