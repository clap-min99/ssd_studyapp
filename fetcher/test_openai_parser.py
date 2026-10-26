import json
import os
from types import SimpleNamespace
from unittest.mock import Mock, patch

import httpx
from django.test import SimpleTestCase
from openai import OpenAI

from fetcher.ai_schemas import AnswerOutput, DigestOutput, SourcesOutput, TagsOutput
from fetcher.openai_parser import (
    _card_summary, _card_summary_errors, _get_client, _valid_card_summary, check_term_answer, explain_item, extract_sources, get_model,
    parse_digest, tag_article, tag_term,
)


class OpenAIParserTests(SimpleTestCase):
    def test_technical_punctuation_and_line_wraps_are_valid(self):
        for text in (
            "AUTOSAR는 CAPI 1.0을 공개합니다. 호환성을 높입니다.",
            "1.0 버전과 3.3V 전원을 지원합니다.",
            "U.S. 기업은 e.g. NVMe 2.0 기술을 활용합니다.",
            "플랫폼(Adaptive Platform, AP)을\n지원합니다.\n\n개발에 활용됩니다.",
            "(CAPI 1.0은 공개 구현입니다.) 호환성을 높입니다.",
            "‘기술 검증에 활용됩니다.’라고 설명합니다.",
            "“플랫폼을 공개합니다.” 호환성을 높입니다.",
        ):
            with self.subTest(text=text):
                self.assertTrue(_valid_card_summary(text, 300))

    def test_length_targets_are_advisory_and_do_not_trigger_regeneration(self):
        for limit in (80, 300, 350):
            text = "가" * (limit - len(" \n입니다.")) + " \n입니다."
            with self.subTest(limit=limit):
                self.assertTrue(_valid_card_summary(text, limit))
                with self.assertLogs("fetcher.openai_parser", level="WARNING") as logs, \
                     patch("fetcher.openai_parser._generate_json") as generate:
                    self.assertTrue(_valid_card_summary("가" + text, limit))
                    self.assertEqual(_card_summary("가" + text, "제목", "원문", "기사", limit), "가" + text)
                generate.assert_not_called()
                self.assertIn(f"{limit + 1}자", logs.output[0])

    def test_numbering_markdown_and_mixed_style_are_rejected(self):
        for text in (
            "1. 설명입니다.", "설명입니다.\n\n② 설명입니다.",
            "**기술** 설명입니다.", "`CAPI` 설명입니다.",
            "*기술* 설명입니다.", "_기술_ 설명입니다.", "~~기술~~ 설명입니다.",
            "[기술](https://example.com) 설명입니다.", "+ 설명입니다.",
            "기술이다. 활용됩니다.", "기술이에요. 활용됩니다.",
            "기술입니다! 활용됩니다.", "기술입니다. 미완성 문장",
        ):
            with self.subTest(text=text):
                self.assertFalse(_valid_card_summary(text, 300))

    def test_logs_each_violation_and_sends_latest_feedback_until_third_retry(self):
        original = "1. **설명이다.**" + "가" * 80
        with patch("fetcher.openai_parser._generate_json", side_effect=[
            {"summary": "두 번째이다."}, {"summary": "세 번째예요."},
            {"summary": "핵심을 설명합니다."},
        ]) as generate, self.assertLogs("fetcher.openai_parser", level="WARNING") as logs:
            self.assertEqual(_card_summary(original, "CAPI", "원문", "인사이트", 80), "핵심을 설명합니다.")
        self.assertEqual(generate.call_count, 3)
        self.assertTrue(any("권장 분량 초과" in entry for entry in logs.output))
        for reason in ("항목 번호 포함", "마크다운 또는 목록 포함", "문체 위반"):
            self.assertTrue(any(reason in entry for entry in logs.output))
            self.assertIn(reason, generate.call_args_list[0].args[0])
        self.assertIn("두 번째이다.", generate.call_args_list[1].args[0])
        self.assertIn("세 번째예요.", generate.call_args_list[2].args[0])

    def test_retries_stop_after_three_and_report_final_reason(self):
        with patch("fetcher.openai_parser._generate_json", return_value={"summary": "반말이다."}) as generate:
            with self.assertRaisesMessage(ValueError, "학습, 재생성 3회") as error:
                _card_summary("최초 반말이다.", "제목", "원문", "학습", 350)
        self.assertEqual(generate.call_count, 3)
        self.assertIn("문체 위반", str(error.exception))
        self.assertEqual(_card_summary_errors("   ", 300), ["빈 요약"])

    def test_card_summary_checks_length_style_and_numbering(self):
        for text in ("", "설명이다.", "설명입니다. 다음이다.", "(1) 설명입니다.", "1) 설명입니다.", "① 설명입니다.", "# 설명입니다.", "- 설명입니다."):
            with self.subTest(text=text):
                self.assertFalse(_valid_card_summary(text, 350))
        self.assertTrue(_valid_card_summary("개념 설명입니다.\n\n필요한 이유를 설명합니다.", 350))

    def test_only_invalid_summaries_are_rewritten_and_checked(self):
        with patch("fetcher.openai_parser._generate_json", return_value={"summary": "핵심을 설명합니다."}) as generate:
            self.assertEqual(_card_summary("정상 요약입니다.", "제목", "원문", "학습", 350), "정상 요약입니다.")
            generate.assert_not_called()
            self.assertEqual(_card_summary("너무 긴 설명이다." * 50, "제목", "원문", "학습", 350), "핵심을 설명합니다.")
            generate.assert_called_once()
            generate.return_value = {"summary": "여전히 반말이다."}
            with self.assertRaisesMessage(ValueError, "요약 길이·문체 검증 실패"):
                _card_summary("반말이다.", "제목", "원문", "학습", 350)

    def test_title_number_cleanup_preserves_technical_numbers(self):
        items = [dict(heading=title, body="학습 내용입니다.", source_text=f"{title}\n원문")
                 for title in ("(1) NAND", "2) FTL", "③ NVMe", "3.3V 전원", "3D NAND")]
        raw = "\n\n".join(item["source_text"] for item in items)
        with patch("fetcher.openai_parser._generate_json", return_value={"learning_items": items}):
            parsed = parse_digest(raw)
        self.assertEqual([item.heading for item in parsed.learning_items], ["NAND", "FTL", "NVMe", "3.3V 전원", "3D NAND"])
        self.assertEqual(parsed.learning_items[0].source_text, items[0]["source_text"])

    def test_merged_numbered_items_are_retried_then_kept_separate(self):
        items = [dict(heading=f"({i}) 주제 {i}", body="개념 설명입니다.", source_text=f"({i}) 주제 {i}\n원문 {i}") for i in range(1, 4)]
        raw = "\n\n".join(item["source_text"] for item in items)
        merged = {"learning_items": [dict(items[0], source_text=raw)]}
        with patch("fetcher.openai_parser._generate_json", side_effect=[merged, {"learning_items": items}]) as generate:
            result = parse_digest(raw)
        self.assertEqual(len(result.learning_items), 3)
        self.assertEqual(generate.call_count, 2)
        with patch("fetcher.openai_parser._generate_json", return_value=merged), self.assertRaisesMessage(ValueError, "누락되거나 합쳐졌습니다"):
            parse_digest(raw)

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
