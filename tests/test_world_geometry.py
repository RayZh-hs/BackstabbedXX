"""Geometry checks accept both original and editor-generated location predicates."""
import unittest

from world_geometry import in_region


class RegionPredicates(unittest.TestCase):
    def test_entity_location_and_location_check_have_the_same_boundaries(self):
        location = {'dimension': 'minecraft:overworld',
                    'position': {'x': {'min': 1, 'max': 3}, 'y': {'min': 2, 'max': 4},
                                 'z': {'min': 5, 'max': 7}}}
        predicates = [
            {'condition': 'minecraft:location_check', 'predicate': location},
            {'condition': 'minecraft:entity_properties', 'entity': 'this',
             'predicate': {'location': location}},
        ]
        for predicate in predicates:
            for point, expected in [([1, 2, 5], True), ([3, 4, 7], True),
                                    ([.999, 3, 6], False), ([2, 4.001, 6], False),
                                    ([2, 3, 7.001], False)]:
                with self.subTest(predicate=predicate['condition'], point=point):
                    self.assertEqual(in_region(predicate, point), expected)

    def test_nested_editor_keep_in_and_keep_out_regions(self):
        def box(low, high):
            return {'condition': 'minecraft:entity_properties', 'entity': 'this',
                    'predicate': {'location': {'position': {'x': {'min': low, 'max': high}}}}}

        predicate = {'condition': 'minecraft:all_of', 'terms': [
            {'condition': 'minecraft:any_of', 'terms': [box(0, 10), box(20, 30)]},
            {'condition': 'minecraft:inverted', 'term': box(4, 6)},
        ]}
        for x, expected in [(0, True), (5, False), (10, True), (15, False),
                            (20, True), (30, True), (31, False)]:
            with self.subTest(x=x):
                self.assertEqual(in_region(predicate, [x, 0, 0]), expected)

    def test_point_checks_reject_entity_constraints_they_cannot_validate(self):
        for entity, properties in [('attacker', {'location': {}}),
                                   ('this', {'location': {}, 'flags': {'is_on_ground': True}})]:
            with self.subTest(entity=entity, properties=properties), self.assertRaises(ValueError):
                in_region({'condition': 'minecraft:entity_properties', 'entity': entity,
                           'predicate': properties}, [0, 0, 0])
