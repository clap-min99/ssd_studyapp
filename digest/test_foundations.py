from io import StringIO
from unittest.mock import patch
import re
import xml.etree.ElementTree as ET

from django.core.management import call_command
from django.test import TestCase, override_settings

from digest.models import Lesson, Tag
from digest.management.commands.seed_foundations import LESSONS, COMBINATIONAL_LESSONS


@override_settings(CACHES={"default": {
    "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    "LOCATION": "foundations-tests",
}})
class FoundationsTests(TestCase):
    def test_seed_is_repeatable_preserves_existing_track_and_serves_lessons(self):
        existing = Tag.objects.create(slug="nand", name="기존 챕터", description="유지", category="ssd", order=1)
        call_command("seed_foundations", stdout=StringIO())
        chapter = Tag.objects.get(slug="binary-representation")
        lesson_ids = list(chapter.lessons.values_list("id", flat=True))
        call_command("seed_foundations", stdout=StringIO())
        self.assertEqual(list(chapter.lessons.values_list("id", flat=True)), lesson_ids)
        existing.refresh_from_db()
        self.assertEqual(existing.description, "유지")
        chapter.full_clean()

        tags = self.client.get("/api/tags/")
        self.assertEqual(tags.status_code, 200)
        self.assertIn("foundations", [tag["category"] for tag in tags.json()])
        response = self.client.get("/api/tags/binary-representation/lessons/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual([lesson["order"] for lesson in response.json()], list(range(1, 13)))
        for index, lesson_id in enumerate(lesson_ids):
            detail = self.client.get(f"/api/lessons/{lesson_id}/")
            self.assertEqual(detail.status_code, 200)
            data = detail.json()
            self.assertEqual(data["prev_lesson_id"], lesson_ids[index - 1] if index else None)
            self.assertEqual(data["next_lesson_id"], lesson_ids[index + 1] if index + 1 < len(lesson_ids) else None)
            self.assert_lesson_content(data["body"], 1)

    def assert_lesson_content(self, body, chapter_number):
        self.assertIn("<details>", body)
        headings = ["이번 레슨의 목표", "앞에서 배운 내용", "따라 풀기", "헷갈리기 쉬운 점", "직접 확인하기", "다음으로 이어가기", "참고 범위"]
        positions = [body.index(f"## {heading}") for heading in headings]
        self.assertEqual(positions, sorted(positions))
        self.assertRegex(body, rf"§{chapter_number}\..*인쇄 pp\..*/ PDF pp\.")
        self.assertNotRegex(body, r"[\u3040-\u30ff\u4e00-\u9fff]")
        diagrams = re.findall(r"<svg\b.*?</svg>", body, re.S)
        self.assertTrue(diagrams)
        for diagram in diagrams:
            self.assertNotRegex(diagram, r"\n\s*\n")
            svg = ET.fromstring(diagram)
            self.assertEqual(svg.attrib["role"], "img")
            labels = svg.attrib["aria-labelledby"].split()
            ids = {node.attrib.get("id") for node in svg.iter()}
            self.assertTrue(set(labels).issubset(ids))

    def test_second_chapter_is_repeatable_and_linked_from_first(self):
        call_command("seed_foundations", stdout=StringIO())
        first = Tag.objects.get(slug="binary-representation")
        second = Tag.objects.get(slug="combinational-logic")
        second.full_clean()
        self.assertEqual(second.prerequisite, first)
        self.assertEqual(second.order, 2)
        lesson_ids = list(second.lessons.values_list("id", flat=True))
        call_command("seed_foundations", stdout=StringIO())
        self.assertEqual(list(second.lessons.values_list("id", flat=True)), lesson_ids)
        response = self.client.get("/api/tags/combinational-logic/lessons/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual([lesson["order"] for lesson in response.json()], list(range(1, 15)))
        self.assertEqual(len(lesson_ids), len(COMBINATIONAL_LESSONS))
        for index, lesson_id in enumerate(lesson_ids):
            detail = self.client.get(f"/api/lessons/{lesson_id}/")
            self.assertEqual(detail.status_code, 200)
            data = detail.json()
            self.assertEqual(data["prev_lesson_id"], lesson_ids[index - 1] if index else None)
            self.assertEqual(data["next_lesson_id"], lesson_ids[index + 1] if index + 1 < len(lesson_ids) else None)
            self.assertIsNone(data["next_chapter_slug"])
            self.assert_lesson_content(data["body"], 2)
        first_detail = self.client.get("/api/tags/binary-representation/").json()
        self.assertEqual(first_detail["next_slug"], second.slug)
        final_lesson = self.client.get(f"/api/lessons/{first.lessons.last().id}/").json()
        self.assertEqual(final_lesson["next_chapter_slug"], second.slug)
        self.assertEqual(self.client.get("/api/tags/combinational-logic/").json()["prerequisite_slug"], first.slug)

    def test_upgrade_preserves_three_prototype_lesson_ids(self):
        chapter = Tag.objects.create(slug="binary-representation", name="비트와 수의 표현", category="foundations", order=1)
        legacy = [Lesson.objects.create(chapter=chapter, order=order, title=LESSONS[target - 1][2], body="시범판")
                  for order, target in [(1, 3), (2, 4), (3, 6)]]
        call_command("seed_foundations", stdout=StringIO())
        call_command("seed_foundations", stdout=StringIO())
        for lesson, order in zip(legacy, [3, 4, 6]):
            lesson.refresh_from_db()
            self.assertEqual(lesson.order, order)
            self.assertNotEqual(lesson.body, "시범판")
        self.assertEqual(chapter.lessons.count(), 12)

    def test_missing_content_rolls_back_chapter_and_lessons(self):
        with patch("digest.management.commands.seed_foundations.Path.read_text", side_effect=FileNotFoundError):
            with self.assertRaises(FileNotFoundError):
                call_command("seed_foundations", stdout=StringIO())
        self.assertFalse(Tag.objects.filter(category="foundations").exists())
        self.assertFalse(Lesson.objects.exists())

    def test_failure_in_second_chapter_rolls_back_first_chapter_updates(self):
        from pathlib import Path

        call_command("seed_foundations", stdout=StringIO())
        first_lesson = Lesson.objects.get(chapter__slug="binary-representation", order=1)
        first_lesson.body = "DB에 남겨둔 편집"
        first_lesson.save(update_fields=["body"])
        lesson_ids = set(Lesson.objects.values_list("id", flat=True))
        read_text = Path.read_text

        def read_content(path, *args, **kwargs):
            if "chapter02" in path.parts:
                raise FileNotFoundError("2장 콘텐츠 누락")
            return read_text(path, *args, **kwargs)

        with patch("digest.management.commands.seed_foundations.Path.read_text", autospec=True, side_effect=read_content):
            with self.assertRaises(FileNotFoundError):
                call_command("seed_foundations", stdout=StringIO())
        first_lesson.refresh_from_db()
        self.assertEqual(first_lesson.body, "DB에 남겨둔 편집")
        self.assertEqual(set(Lesson.objects.values_list("id", flat=True)), lesson_ids)
