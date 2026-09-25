import unittest
from unittest.mock import Mock, patch
from types import SimpleNamespace

from fail.core.memory_candidate import MemoryCandidate
from fail.core.memory_consent import request_memory_consent
from fail.core.memory_policy import is_memory_eligible, normalize_memory
from fail.main import main, persist_memory_candidate


def make_candidate(**overrides) -> MemoryCandidate:
    values = {
        "should_remember": True,
        "memory": "User prefers step-by-step technical guidance.",
        "memory_type": "preference",
        "certainty": "confirmed",
        "reason": "The user explicitly stated a stable preference.",
    }
    values.update(overrides)

    return MemoryCandidate(**values)


class MemoryPolicyTests(unittest.TestCase):
    def test_eligible_candidate_can_be_presented_for_consent(self):
        candidate = make_candidate(certainty="inferred")
        input_fn = Mock(return_value="yes")
        output_fn = Mock()

        self.assertTrue(is_memory_eligible(candidate))
        self.assertTrue(
            request_memory_consent(
                candidate.memory,
                input_fn=input_fn,
                output_fn=output_fn,
            )
        )
        output_fn.assert_called_once_with(
            "\nFAiL memory candidate: " + candidate.memory
        )
        input_fn.assert_called_once_with("Save this memory? [y/N]: ")

    def test_yes_consent_allows_persistence(self):
        candidate = make_candidate()

        with patch("fail.main.remember") as remember_mock:
            persisted = persist_memory_candidate(
                candidate,
                input_fn=Mock(return_value="yes"),
                output_fn=Mock(),
            )

        self.assertTrue(persisted)
        remember_mock.assert_called_once_with(
            "Fatima prefers step-by-step technical guidance.",
            "preference",
            "confirmed",
        )

    def test_y_consent_allows_persistence(self):
        candidate = make_candidate()

        with patch("fail.main.remember") as remember_mock:
            persisted = persist_memory_candidate(
                candidate,
                input_fn=Mock(return_value="y"),
                output_fn=Mock(),
            )

        self.assertTrue(persisted)
        remember_mock.assert_called_once()

    def test_non_affirmative_consent_rejects_persistence(self):
        candidate = make_candidate()

        for response in ("no", "", "maybe"):
            with self.subTest(response=response):
                with patch("fail.main.remember") as remember_mock:
                    persisted = persist_memory_candidate(
                        candidate,
                        input_fn=Mock(return_value=response),
                        output_fn=Mock(),
                    )

                self.assertFalse(persisted)
                remember_mock.assert_not_called()

    def test_policy_rejects_candidate_marked_not_to_remember(self):
        candidate = make_candidate(
            should_remember=False,
            memory="",
        )

        self.assertFalse(is_memory_eligible(candidate))

    def test_policy_rejects_blank_memory_text(self):
        candidate = make_candidate(memory="   ")

        self.assertFalse(is_memory_eligible(candidate))

    def test_policy_rejection_does_not_request_consent_or_persist(self):
        candidate = make_candidate(
            should_remember=False,
            memory="",
        )

        with (
            patch("fail.main.request_memory_consent") as consent_mock,
            patch("fail.main.remember") as remember_mock,
        ):
            persisted = persist_memory_candidate(candidate)

        self.assertFalse(persisted)
        consent_mock.assert_not_called()
        remember_mock.assert_not_called()

    def test_normalize_memory_strips_text_and_uses_persistent_field_names(self):
        candidate = make_candidate(
            memory="  User says the creator prefers concise guidance.  ",
            certainty="learned",
        )

        self.assertEqual(
            normalize_memory(candidate),
            {
                "memory": "Fatima says Fatima prefers concise guidance.",
                "type": "preference",
                "certainty": "learned",
            },
        )

    def test_normalize_memory_replaces_capitalized_the_user_as_a_full_phrase(self):
        candidate = make_candidate(
            memory=(
                "The user prefers step-by-step explanations when learning "
                "technical topics."
            )
        )

        self.assertEqual(
            normalize_memory(candidate),
            {
                "memory": (
                    "Fatima prefers step-by-step explanations when learning "
                    "technical topics."
                ),
                "type": "preference",
                "certainty": "confirmed",
            },
        )

    def test_normalize_memory_accepts_a_custom_creator_name(self):
        candidate = make_candidate(memory="the user has an ongoing project.")

        self.assertEqual(
            normalize_memory(candidate, creator_name="Amina"),
            {
                "memory": "Amina has an ongoing project.",
                "type": "preference",
                "certainty": "confirmed",
            },
        )


class MemoryConsentCliControlFlowTests(unittest.TestCase):
    def assert_consent_response_is_consumed(
        self,
        consent_response: str,
        should_persist: bool,
    ) -> None:
        user_message = "Remember that I prefer VS Code for coding."
        input_fn = Mock(
            side_effect=[
                user_message,
                consent_response,
                "exit",
            ]
        )
        response = SimpleNamespace(
            message=SimpleNamespace(
                tool_calls=[],
                content="I will consider that memory candidate.",
            )
        )

        with (
            patch("fail.main.load_identity", return_value="Identity"),
            patch("fail.main.load_memories", return_value=[]),
            patch(
                "fail.main.choose_model",
                return_value=SimpleNamespace(model="test-model"),
            ),
            patch("fail.main.chat", return_value=response) as chat_mock,
            patch(
                "fail.main.detect_memory_candidate",
                return_value=make_candidate(),
            ),
            patch("fail.main.remember") as remember_mock,
        ):
            main(input_fn=input_fn)

        self.assertEqual(
            input_fn.call_args_list,
            [
                unittest.mock.call("You: "),
                unittest.mock.call("Save this memory? [y/N]: "),
                unittest.mock.call("You: "),
            ],
        )
        self.assertEqual(chat_mock.call_count, 1)

        sent_messages = chat_mock.call_args.kwargs["messages"]
        self.assertEqual(
            [
                message["content"]
                for message in sent_messages
                if message["role"] == "user"
            ],
            [user_message],
        )

        if should_persist:
            remember_mock.assert_called_once_with(
                "Fatima prefers step-by-step technical guidance.",
                "preference",
                "confirmed",
            )
        else:
            remember_mock.assert_not_called()

    def test_n_consent_response_is_consumed(self):
        self.assert_consent_response_is_consumed("n", should_persist=False)

    def test_uppercase_n_consent_response_is_consumed(self):
        self.assert_consent_response_is_consumed("N", should_persist=False)

    def test_y_consent_response_is_consumed(self):
        self.assert_consent_response_is_consumed("y", should_persist=True)

    def test_yes_consent_response_is_consumed(self):
        self.assert_consent_response_is_consumed("yes", should_persist=True)


if __name__ == "__main__":
    unittest.main()
