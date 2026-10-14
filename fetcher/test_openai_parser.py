import json
import os
from types import SimpleNamespace
from unittest.mock import Mock, patch

import httpx
from django.test import SimpleTestCase
from openai import OpenAI

from fetcher.ai_schemas import AnswerOutput, DigestOutput, SourcesOutput, TagsOutput
from fetcher.openai_parser import (
    _get_client, check_term_answer, explain_item, extract_sources, get_model,
    parse_digest, tag_article, tag_term,
)


class OpenAIParserTests(SimpleTestCase):
    def mock_client(self, result=None, text=""):
        client = Mock()
        client.responses.parse.return_value = SimpleNamespace(status="completed", output_parsed=result)
        client.responses.create.return_value = SimpleNamespace(status="completed", output_text=text)
        return client

    def test_models_follow_override_base_default_order(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(get_model("parse"), "gpt-5.4-mini")
            os.environ["OPENAI_MODEL"] = "base-model"
            self.assertEqual(get_model("review"), "base-model")
            os.environ["OPENAI_REVIEW_MODEL"] = "review-model"
            self.assertEqual(get_model("review"), "review-model")
            os.environ["OPENAI_PARSE_MODEL"] = "  "
            self.assertEqual(get_model("parse"), "base-model")

    def test_missing_key_has_actionable_error(self):
        with patch.dict(os.environ, {}, clear=True), self.assertRaisesMessage(ValueError, "OPENAI_API_KEY"):
            _get_client()

    def test_schema_roundtrip_through_real_sdk_without_network(self):
        captured = []

        def respond(request):
            captured.append(json.loads(request.content))
            return httpx.Response(200, json={
                "id": "resp_test", "object": "response", "created_at": 0,
                "status": "completed", "model": "gpt-5.4-mini",
                "output": [{"type": "message", "id": "msg_test", "role": "assistant", "status": "completed",
                    "content": [{"type": "output_text", "text": DigestOutput().model_dump_json(), "annotations": []}]}],
            })

        with httpx.Client(transport=httpx.MockTransport(respond)) as http_client:
            client = OpenAI(api_key="test-key", http_client=http_client)
            with patch("fetcher.openai_parser._get_client", return_value=client):
                result = parse_digest("no content")
        self.assertEqual(result.articles, [])
        body = captured[0]
        self.assertFalse(body["store"])
        self.assertEqual(body["text"]["format"]["type"], "json_schema")
        self.assertTrue(body["text"]["format"]["strict"])
        schema = body["text"]["format"]["schema"]
        self.assertEqual(set(schema["required"]), set(schema["properties"]))

    def test_answer_check_uses_review_schema(self):
        client = self.mock_client(AnswerOutput(verdict="partial", feedback="핵심을 보완하세요."))
        with patch("fetcher.openai_parser._get_client", return_value=client):
            result = check_term_answer("NAND", "memory", "storage", "my answer")
        self.assertEqual(result["verdict"], "partial")
        self.assertIs(client.responses.parse.call_args.kwargs["text_format"], AnswerOutput)

    def test_tags_and_source_backfills(self):
        client = self.mock_client(TagsOutput(tags=["nand"]))
        with patch("fetcher.openai_parser._get_client", return_value=client):
            self.assertEqual(tag_article("title", "summary", "ssd"), ["nand"])
            self.assertEqual(tag_term("NAND", "meaning"), ["nand"])
            client.responses.parse.return_value.output_parsed = SourcesOutput(sources=["source"])
            self.assertEqual(extract_sources("source", ["title"]), ["source"])
            with self.assertRaisesMessage(ValueError, "항목 수 불일치"):
                extract_sources("source", ["one", "two"])

    def test_refused_or_incomplete_output_rejected(self):
        client = self.mock_client()
        with patch("fetcher.openai_parser._get_client", return_value=client):
            with self.assertRaisesMessage(ValueError, "유효한 구조화"):
                parse_digest("mail")
            client.responses.parse.return_value.output_parsed = DigestOutput()
            client.responses.parse.return_value.status = "incomplete"
            with self.assertRaises(ValueError):
                parse_digest("mail")

    def test_explanation_is_markdown_and_empty_response_rejected(self):
        client = self.mock_client(text="## 쉽게 풀어보기\n설명")
        with patch("fetcher.openai_parser._get_client", return_value=client):
            self.assertTrue(explain_item("title", "body", "mail").startswith("##"))
            self.assertFalse(client.responses.create.call_args.kwargs["store"])
            client.responses.create.return_value.output_text = " "
            with self.assertRaises(ValueError):
                explain_item("title", "body", "mail")
