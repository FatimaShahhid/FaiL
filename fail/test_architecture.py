import unittest
from unittest.mock import Mock, patch

from fail.core.architecture import (
    ARCHITECTURE,
    format_architecture,
    find_capability_for_question,
)
from fail.main import (
    build_self_knowledge_prompt,
    build_system_prompt,
    handle_capability_question,
    is_self_knowledge_request,
    main,
)


class ArchitectureSelfKnowledgeTests(unittest.TestCase):
    def test_format_architecture_reports_implemented_and_unimplemented(self):
        architecture_text = format_architecture()

        self.assertIn("Implemented capabilities:", architecture_text)
        self.assertIn("cli_agent_loop", architecture_text)
        self.assertIn("Not implemented:", architecture_text)
        self.assertIn("rbac", architecture_text)
        self.assertIn("obsidian_note_reading", architecture_text)
        self.assertFalse(ARCHITECTURE["subsystems"]["rbac"]["implemented"])
        self.assertFalse(
            ARCHITECTURE["subsystems"]["obsidian_note_reading"]["implemented"]
        )

    def test_normal_system_prompt_excludes_self_knowledge_context(self):
        prompt = build_system_prompt("Identity text.", [])

        self.assertNotIn("Authoritative FAiL self-knowledge:", prompt)
        self.assertNotIn(format_architecture(), prompt)

    def test_detects_self_knowledge_requests(self):
        requests = (
            "What can you currently do?",
            "What can you do?",
            "What can't you do?",
            "What are your capabilities?",
            "What is implemented?",
        )

        for request in requests:
            with self.subTest(request=request):
                self.assertTrue(is_self_knowledge_request(request))

    def test_rejects_ordinary_question_as_self_knowledge_request(self):
        self.assertFalse(
            is_self_knowledge_request("What is DNS?")
        )

    def test_self_knowledge_prompt_uses_authoritative_architecture(self):
        self.assertTrue(
            is_self_knowledge_request("What can you currently do?")
        )

        prompt = build_self_knowledge_prompt()

        self.assertIn(format_architecture(), prompt)
        self.assertIn("implemented software capabilities, not general facts", prompt)
        self.assertIn("Do not use general model knowledge", prompt)
        self.assertIn("entries marked not implemented as unavailable", prompt)
    def test_known_capability_question_returns_architecture_entry(self):
        result = find_capability_for_question(
            "Can FAiL edit existing Obsidian notes?"
        )

        self.assertIsNotNone(result)
        self.assertFalse(result["implemented"])
        self.assertEqual(
            result["subsystem"],
            "obsidian_note_reading",
        )

    def test_unknown_capability_question_returns_none(self):
        result = find_capability_for_question(
            "Can FAiL integrate directly with VS Code?"
        )

        self.assertIsNone(result)


class HandleCapabilityQuestionTests(unittest.TestCase):
    def test_returns_none_for_non_self_knowledge_input(self):
        self.assertIsNone(handle_capability_question("What is DNS?"))
        self.assertIsNone(handle_capability_question("Hello FAiL."))
        self.assertIsNone(handle_capability_question("Write a python script for calculating fibonacci."))

    def test_returns_none_for_conversational_requests(self):
        self.assertIsNone(handle_capability_question("Can you explain DNS?"))
        self.assertIsNone(handle_capability_question("Can you help me write Python code?"))

    def test_returns_architecture_summary_for_broad_self_knowledge_queries(self):
        broad_queries = (
            "What can you do?",
            "What are your capabilities?",
            "What is implemented?",
            "What can FAiL currently do?",
            "What can you currently do?",
            "What can't you do?",
            "What is not implemented?",
            "What can FAiL do?",
        )
        expected = format_architecture()
        for query in broad_queries:
            with self.subTest(query=query):
                self.assertEqual(handle_capability_question(query), expected)

    def test_returns_implemented_response_for_known_implemented_capability(self):
        result = handle_capability_question("Can FAiL create Obsidian notes?")
        self.assertIsNotNone(result)
        self.assertTrue(
            result.startswith(
                "Yes. FAiL currently implements this capability through obsidian_note_writing:"
            )
        )

    def test_returns_unimplemented_response_for_known_unimplemented_capability(self):
        result = handle_capability_question("Can FAiL edit existing Obsidian notes?")
        self.assertIsNotNone(result)
        self.assertTrue(
            result.startswith(
                "No. This capability is not currently implemented. FAiL's architecture records obsidian_note_reading as not implemented:"
            )
        )

        read_result = handle_capability_question("Can FAiL read Obsidian notes?")
        self.assertIsNotNone(read_result)
        self.assertTrue(
            read_result.startswith(
                "No. This capability is not currently implemented. FAiL's architecture records obsidian_note_reading as not implemented:"
            )
        )

        rbac_result = handle_capability_question("Does FAiL support RBAC?")
        self.assertIsNotNone(rbac_result)
        self.assertTrue(
            rbac_result.startswith(
                "No. This capability is not currently implemented. FAiL's architecture records rbac as not implemented:"
            )
        )

    def test_returns_architecture_fallback_for_unknown_capability(self):
        result = handle_capability_question("Can FAiL fly an airplane?")
        self.assertEqual(
            result,
            "FAiL's current architecture does not define this capability, "
            "so it cannot be described as an implemented FAiL capability.",
        )

    def test_second_person_implemented_capability(self):
        result = handle_capability_question("Can you create Obsidian notes?")
        self.assertIsNotNone(result)
        self.assertTrue(
            result.startswith(
                "Yes. FAiL currently implements this capability through obsidian_note_writing:"
            ),
            msg=f"Unexpected result: {result!r}",
        )

    def test_second_person_unimplemented_capability(self):
        for query in (
            "Can you read existing Obsidian notes?",
            "Can you read Obsidian notes?",
        ):
            with self.subTest(query=query):
                result = handle_capability_question(query)
                self.assertIsNotNone(result)
                self.assertTrue(
                    result.startswith(
                        "No. This capability is not currently implemented. "
                        "FAiL's architecture records obsidian_note_reading as not implemented:"
                    ),
                    msg=f"Unexpected result for {query!r}: {result!r}",
                )

    def test_second_person_unimplemented_rbac(self):
        result = handle_capability_question("Do you support RBAC?")
        self.assertIsNotNone(result)
        self.assertTrue(
            result.startswith(
                "No. This capability is not currently implemented. "
                "FAiL's architecture records rbac as not implemented:"
            ),
            msg=f"Unexpected result: {result!r}",
        )

    def test_second_person_unknown_capability(self):
        result = handle_capability_question("Can you fly an airplane?")
        self.assertEqual(
            result,
            "FAiL's current architecture does not define this capability, "
            "so it cannot be described as an implemented FAiL capability.",
        )


class CapabilityCliControlFlowTests(unittest.TestCase):
    def test_capability_questions_handled_deterministically_without_model_routing_or_chat(self):
        input_fn = Mock(
            side_effect=[
                "What can FAiL currently do?",
                "Can FAiL create Obsidian notes?",
                "Can FAiL fly an airplane?",
                # second-person variants
                "Can you create Obsidian notes?",
                "Can you read existing Obsidian notes?",
                "Do you support RBAC?",
                "Can you fly an airplane?",
                "exit",
            ]
        )

        with (
            patch("fail.main.load_identity", return_value="Identity"),
            patch("fail.main.load_memories", return_value=[]),
            patch("fail.main.choose_model") as choose_model_mock,
            patch("fail.main.chat") as chat_mock,
        ):
            main(input_fn=input_fn)

        # Capability questions must be answered deterministically before routing or chat
        choose_model_mock.assert_not_called()
        chat_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
