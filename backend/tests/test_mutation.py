from exeris.core.main import db
from exeris.core.models import ScheduledTask, ItemType, EntityTypeProperty
from flask_testing import TestCase
from tests import util


class GameDateTest(TestCase):
    create_app = util.set_up_app_with_database
    tearDown = util.tear_down_rollback

    def assert_equality_of_scheduled_task_after_updating_db(self, expected_value, ):
        db.session.flush()

        # load directly from db
        test_object = ScheduledTask.query.one()
        self.assertEqual(expected_value, test_object.process_data)

        return test_object

    def assert_equality_of_entity_type_property_after_updating_db(self, expected_value):
        db.session.flush()

        # load directly from db
        type_property = EntityTypeProperty.query.filter_by(name="Funny").one()
        self.assertEqual(expected_value, type_property.data)

        return type_property

    def test_persistence_of_not_nested_json_list(self):
        test_object = ScheduledTask(["a", 1], 100)
        db.session.add(test_object)

        self.assertEqual(["a", 1], test_object.process_data)

        test_object = None
        test_object = self.assert_equality_of_scheduled_task_after_updating_db(["a", 1])

        # add  list
        test_object.process_data.append("b")
        test_object.process_data.append("c")

        test_object = None
        test_object = self.assert_equality_of_scheduled_task_after_updating_db(["a", 1, "b", "c"])

        test_object.process_data += ["d", "e"]

        self.assert_equality_of_scheduled_task_after_updating_db(["a", 1, "b", "c", "d", "e"])

    def test_persistence_of_not_nested_json_dict(self):
        test_type = ItemType("hammer", 100)
        type_property = EntityTypeProperty("Funny", {"a": 1}, test_type)

        db.session.add_all([test_type, type_property])

        type_property = None
        type_property = self.assert_equality_of_entity_type_property_after_updating_db({"a": 1})

        type_property.data["d"] = 23
        del type_property.data["a"]
        self.assertEqual({"d": 23}, type_property.data)

        type_property = None
        self.assert_equality_of_entity_type_property_after_updating_db({"d": 23})

    def test_persistence_of_nested_json_list(self):
        original_list = [1, 2, [3]]
        test_object = ScheduledTask(["a", original_list], 100)
        db.session.add(test_object)

        self.assertEqual(["a", [1, 2, [3]]], test_object.process_data)

        test_object = None
        test_object = self.assert_equality_of_scheduled_task_after_updating_db(["a", [1, 2, [3]]])

        # IT'S NOT A BUG, the original list needs to be converted into trackable counterpart, so original is unchanged
        original_list[2] += [4, 5]
        self.assertEqual(["a", [1, 2, [3]]], test_object.process_data)

        trackable_list = test_object.process_data[1][2]
        trackable_list += [4, 5]
        self.assertEqual(["a", [1, 2, [3, 4, 5]]], test_object.process_data)

        test_object = self.assert_equality_of_scheduled_task_after_updating_db(["a", [1, 2, [3, 4, 5]]])

        test_object.process_data[1][1] = []
        test_object = self.assert_equality_of_scheduled_task_after_updating_db(["a", [1, [], [3, 4, 5]]])

        test_object.process_data[1][1] += [9, 8]
        self.assert_equality_of_scheduled_task_after_updating_db(["a", [1, [9, 8], [3, 4, 5]]])

    def test_persistence_of_nested_json_dict(self):
        test_type = ItemType("hammer", 100)
        type_property = EntityTypeProperty("Funny", {"a": [1, {"d": "hello", 1: 3}]}, test_type)

        db.session.add_all([test_type, type_property])

        type_property = None
        type_property = self.assert_equality_of_entity_type_property_after_updating_db({"a": [1, {"d": "hello", 1: 3}]})

        type_property.data["a"][1]["d"] = "hej"
        self.assertEqual({"a": [1, {"d": "hej", 1: 3}]}, type_property.data)

        type_property = None
        type_property = self.assert_equality_of_entity_type_property_after_updating_db({"a": [1, {"d": "hej", 1: 3}]})

        type_property.data["a"] += [3, 4]
        self.assertEqual({"a": [1, {"d": "hej", 1: 3}, 3, 4]}, type_property.data)
        type_property = None
        type_property = self.assert_equality_of_entity_type_property_after_updating_db(
            {"a": [1, {"d": "hej", 1: 3}, 3, 4]})

        value = type_property.data["a"]
        del value[1][1]

        self.assertEqual({"a": [1, {"d": "hej"}, 3, 4]}, type_property.data)

        type_property = None
        type_property = self.assert_equality_of_entity_type_property_after_updating_db({"a": [1, {"d": "hej"}, 3, 4]})

        type_property.data["a"][1]["z"] = 1
        self.assertEqual({"a": [1, {"d": "hej", "z": 1}, 3, 4]}, type_property.data)
        db.session.flush()

        type_property = None
        self.assert_equality_of_entity_type_property_after_updating_db(
            {"a": [1, {"d": "hej", "z": 1}, 3, 4]})

    # def test_persistence_of_nested_json(self):
    #     rl = RootLocation(Point(1, 1), 11)
    #     char = util.create_character("jan", rl, util.create_player("fead"))
    #
    #     test_compound_json = AchievementCharacterProgress("potato_eater", char, {"a": "b", "d": {"1": 2}})
    #
    #     db.session.add_all([rl, test_compound_json])
    #
    #     self.assertEqual({"a": "b", "d": {"1": 2}}, test_compound_json.details)
    #     db.session.flush()
    #     test_compound_json = None
    #
    #     test_compound_json = AchievementCharacterProgress.query.one()
    #     self.assertEqual({"a": "b", "d": {"1": 2}}, test_compound_json.details)
    #
    #     d = test_compound_json.details["d"]
    #     d["3"] = 7
    #     test_compound_json.details["d"] = d
    #
    #     self.assertEqual({"a": "b", "d": {"1": 2, "3": 7}}, test_compound_json.details)
    #     db.session.flush()
    #     test_compound_json = None
    #
    #     test_compound_json = AchievementCharacterProgress.query.one()
    #     print(">>>", type(test_compound_json.details))
    #     self.assertEqual({"a": "b", "d": {"1": 2, "3": 7}}, test_compound_json.details)
    #
    #     test_compound_json.details = ["a", "b", "c"]
    #     db.session.flush()
    #     test_compound_json = None
    #
    #     test_compound_json = AchievementCharacterProgress.query.one()
    #     self.assertEqual(["a", "b", "c"], test_compound_json.details)
    #
    #     test_compound_json.details.append("d")
    #     test_compound_json.details.append("e")
    #
    #     db.session.flush()
    #     test_compound_json = None
    #
    #     test_compound_json = AchievementCharacterProgress.query.one()
    #     self.assertEqual(["a", "b", "c", "d", "e"], test_compound_json.details)
    #
    #     test_compound_json.details = 8
    #     db.session.flush()
    #     test_compound_json = None
    #
    #     test_compound_json = AchievementCharacterProgress.query.one()
    #     self.assertEqual(8, test_compound_json.details)
    #
    #     test_compound_json.details += 4
    #     db.session.flush()
    #     test_compound_json = None
    #
    #     test_compound_json = AchievementCharacterProgress.query.one()
    #     self.assertEqual(12, test_compound_json.details)
    #
    #     test_compound_json.details = "abc"
    #     db.session.flush()
    #     test_compound_json = None
    #
    #     test_compound_json = AchievementCharacterProgress.query.one()
    #     self.assertEqual("abc", test_compound_json.details)
    #
    #     test_compound_json.details += "def"
    #     db.session.flush()
    #     test_compound_json = None
    #
    #     test_compound_json = AchievementCharacterProgress.query.one()
    #     self.assertEqual("abcdef", test_compound_json.details)
    #
    #     test_compound_json.details = None
    #     db.session.flush()
    #     test_compound_json = None
    #
    #     test_compound_json = AchievementCharacterProgress.query.one()
    #     self.assertEqual("abcdef", test_compound_json.details)
