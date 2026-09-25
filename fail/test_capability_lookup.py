import unittest

from fail.core.architecture import (
    get_capability_status,
    resolve_capability_alias,
    find_capability_for_question,
)


class TestCapabilityLookup(unittest.TestCase):

    def test_direct_lookup(self):
        result = get_capability_status("obsidian_note_reading")

        self.assertIsNotNone(result)
        self.assertFalse(result["implemented"])
        self.assertEqual(
            result["subsystem"],
            "obsidian_note_reading",
        )

    def test_create_notes_is_implemented(self):
        result = resolve_capability_alias(
            "create obsidian notes"
        )

        self.assertIsNotNone(result)
        self.assertTrue(result["implemented"])
        self.assertEqual(
            result["subsystem"],
            "obsidian_note_writing",
        )

    def test_edit_existing_notes_is_not_implemented(self):
        result = resolve_capability_alias(
            "edit existing obsidian notes"
        )

        self.assertIsNotNone(result)
        self.assertFalse(result["implemented"])
        self.assertEqual(
            result["subsystem"],
            "obsidian_note_reading",
        )
    def test_question_about_editing_notes(self):
        result = find_capability_for_question(
            "Can FAiL edit existing Obsidian notes?"
        )

        self.assertIsNotNone(result)
        self.assertFalse(result["implemented"])
        self.assertEqual(
            result["subsystem"],
            "obsidian_note_reading",
        )

    def test_question_about_creating_notes(self):
        result = find_capability_for_question(
            "Can FAiL create Obsidian notes?"
        )

        self.assertIsNotNone(result)
        self.assertTrue(result["implemented"])
        self.assertEqual(
            result["subsystem"],
            "obsidian_note_writing",
        )

    def test_unknown_capability(self):
        result = resolve_capability_alias(
            "time travel"
        )

        self.assertIsNone(result)

    def test_read_existing_obsidian_notes_alias(self):
        result = resolve_capability_alias(
            "read existing obsidian notes"
        )

        self.assertIsNotNone(result)
        self.assertFalse(result["implemented"])
        self.assertEqual(
            result["subsystem"],
            "obsidian_note_reading",
        )

    def test_question_about_reading_existing_notes_second_person(self):
        result = find_capability_for_question(
            "Can you read existing Obsidian notes?"
        )

        self.assertIsNotNone(result)
        self.assertFalse(result["implemented"])
        self.assertEqual(
            result["subsystem"],
            "obsidian_note_reading",
        )

    def test_question_about_reading_notes_second_person(self):
        result = find_capability_for_question(
            "Can you read Obsidian notes?"
        )

        self.assertIsNotNone(result)
        self.assertFalse(result["implemented"])
        self.assertEqual(
            result["subsystem"],
            "obsidian_note_reading",
        )

    def test_question_about_creating_notes_second_person(self):
        result = find_capability_for_question(
            "Can you create Obsidian notes?"
        )

        self.assertIsNotNone(result)
        self.assertTrue(result["implemented"])
        self.assertEqual(
            result["subsystem"],
            "obsidian_note_writing",
        )


if __name__ == "__main__":
    unittest.main()