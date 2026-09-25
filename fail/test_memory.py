import json
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from uuid import UUID

from pydantic import ValidationError

from fail.core import memory as memory_module
from fail.core.memory_candidate import MemoryCandidate
from fail.core.memory_manager import remember


class MemoryStorageTests(unittest.TestCase):
    def test_load_memories_reads_legacy_json_structure(self):
        expected_memories = [
            {
                "memory": "Fatima prefers concise guidance.",
                "type": "preference",
                "certainty": "confirmed",
            }
        ]

        with TemporaryDirectory() as directory:
            memory_path = Path(directory) / "memories.json"
            memory_path.write_text(
                json.dumps({"memories": expected_memories}),
                encoding="utf-8",
            )

            with patch.object(memory_module, "MEMORY_PATH", memory_path):
                self.assertEqual(memory_module.load_memories(), expected_memories)

    def test_load_memories_returns_empty_list_when_file_is_missing(self):
        with TemporaryDirectory() as directory:
            memory_path = Path(directory) / "missing_memories.json"

            with patch.object(memory_module, "MEMORY_PATH", memory_path):
                self.assertEqual(memory_module.load_memories(), [])

    def test_save_memory_appends_records_to_persistent_json(self):
        first_memory = {
            "memory": "Fatima is building FAiL.",
            "type": "project",
            "certainty": "confirmed",
        }
        second_memory = {
            "memory": "Fatima prefers step-by-step guidance.",
            "type": "preference",
            "certainty": "learned",
        }

        with TemporaryDirectory() as directory:
            memory_path = Path(directory) / "memories.json"

            with patch.object(memory_module, "MEMORY_PATH", memory_path):
                memory_module.save_memory(first_memory)
                memory_module.save_memory(second_memory)

                self.assertEqual(
                    memory_module.load_memories(),
                    [first_memory, second_memory],
                )
                self.assertEqual(
                    json.loads(memory_path.read_text(encoding="utf-8")),
                    {"memories": [first_memory, second_memory]},
                )

    def test_remember_persists_active_lifecycle_metadata(self):
        with TemporaryDirectory() as directory:
            memory_path = Path(directory) / "memories.json"

            with patch.object(memory_module, "MEMORY_PATH", memory_path):
                remember(
                    "Fatima has an ongoing project.",
                    "project",
                    "inferred",
                )
                remember(
                    "Fatima prefers concise guidance.",
                    "preference",
                    "confirmed",
                )

                memories = memory_module.load_memories()

                self.assertEqual(
                    [memory["status"] for memory in memories],
                    ["active", "active"],
                )
                self.assertNotEqual(memories[0]["id"], memories[1]["id"])

                for memory in memories:
                    UUID(memory["id"])
                    created_at = datetime.fromisoformat(memory["created_at"])
                    updated_at = datetime.fromisoformat(memory["updated_at"])

                    self.assertEqual(created_at.tzinfo, timezone.utc)
                    self.assertEqual(updated_at.tzinfo, timezone.utc)
                    self.assertEqual(memory["created_at"], memory["updated_at"])


class MemoryCandidateTests(unittest.TestCase):
    def test_memory_candidate_accepts_supported_values(self):
        candidate = MemoryCandidate(
            should_remember=True,
            memory="Fatima prefers concise guidance.",
            memory_type="preference",
            certainty="confirmed",
            reason="The preference was explicitly stated.",
        )

        self.assertTrue(candidate.should_remember)
        self.assertEqual(candidate.memory_type, "preference")
        self.assertEqual(candidate.certainty, "confirmed")

    def test_memory_candidate_rejects_unsupported_type(self):
        with self.assertRaises(ValidationError):
            MemoryCandidate(
                should_remember=True,
                memory="Fatima prefers concise guidance.",
                memory_type="unsupported",
                certainty="confirmed",
                reason="Test candidate.",
            )


if __name__ == "__main__":
    unittest.main()
