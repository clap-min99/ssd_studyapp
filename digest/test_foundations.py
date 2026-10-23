from io import StringIO
from unittest.mock import patch
import re
import xml.etree.ElementTree as ET

from django.core.management import call_command
from django.test import TestCase, override_settings

from digest.models import Lesson, Tag
from digest.management.commands.seed_foundations import (
    LESSONS, COMBINATIONAL_LESSONS, SEQUENTIAL_LESSONS, HDL_LESSONS, BUILDING_BLOCK_LESSONS,
)


@override_settings(CACHES={"default": {
    "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    "LOCATION": "foundations-tests",
}})
class FoundationsTests(TestCase):
    def setUp(self):
        # 각 테스트의 API 조회 수가 다른 테스트의 요청 제한에 누적되지 않게 한다.
        from django.core.cache import cache
        cache.clear()

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
            self.assertEqual(data["next_chapter_slug"], "sequential-logic")
            self.assert_lesson_content(data["body"], 2)
        first_detail = self.client.get("/api/tags/binary-representation/").json()
        self.assertEqual(first_detail["next_slug"], second.slug)
        final_lesson = self.client.get(f"/api/lessons/{first.lessons.last().id}/").json()
        self.assertEqual(final_lesson["next_chapter_slug"], second.slug)
        self.assertEqual(self.client.get("/api/tags/combinational-logic/").json()["prerequisite_slug"], first.slug)

    def test_third_chapter_is_repeatable_and_linked_from_second(self):
        call_command("seed_foundations", stdout=StringIO())
        second = Tag.objects.get(slug="combinational-logic")
        third = Tag.objects.get(slug="sequential-logic")
        third.full_clean()
        self.assertEqual(third.prerequisite, second)
        self.assertEqual(third.order, 3)
        lesson_ids = list(third.lessons.values_list("id", flat=True))
        call_command("seed_foundations", stdout=StringIO())
        self.assertEqual(list(third.lessons.values_list("id", flat=True)), lesson_ids)
        response = self.client.get("/api/tags/sequential-logic/lessons/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual([lesson["order"] for lesson in response.json()], list(range(1, 18)))
        self.assertEqual(len(lesson_ids), len(SEQUENTIAL_LESSONS))
        for index, lesson_id in enumerate(lesson_ids):
            data = self.client.get(f"/api/lessons/{lesson_id}/").json()
            self.assertEqual(data["prev_lesson_id"], lesson_ids[index - 1] if index else None)
            self.assertEqual(data["next_lesson_id"], lesson_ids[index + 1] if index + 1 < len(lesson_ids) else None)
            self.assertEqual(data["next_chapter_slug"], "hardware-description-languages")
            self.assert_lesson_content(data["body"], 3)
        self.assertEqual(self.client.get("/api/tags/combinational-logic/").json()["next_slug"], third.slug)
        self.assertEqual(self.client.get("/api/tags/sequential-logic/").json()["prerequisite_slug"], second.slug)
        final_lesson = self.client.get(f"/api/lessons/{second.lessons.last().id}/").json()
        self.assertEqual(final_lesson["next_chapter_slug"], third.slug)

    def test_fourth_chapter_is_repeatable_preserves_previous_lessons_and_links_from_third(self):
        call_command("seed_foundations", stdout=StringIO())
        third = Tag.objects.get(slug="sequential-logic")
        fourth = Tag.objects.get(slug="hardware-description-languages")
        fourth.full_clean()
        self.assertEqual(fourth.prerequisite, third)
        self.assertEqual(fourth.order, 4)
        self.assertEqual(fourth.category, "foundations")
        previous = list(Lesson.objects.exclude(chapter=fourth).values_list("id", "chapter_id", "order", "body"))
        lesson_ids = list(fourth.lessons.values_list("id", flat=True))
        call_command("seed_foundations", stdout=StringIO())
        self.assertEqual(list(fourth.lessons.values_list("id", flat=True)), lesson_ids)
        self.assertEqual(list(Lesson.objects.exclude(chapter=fourth).values_list("id", "chapter_id", "order", "body")), previous)
        response = self.client.get("/api/tags/hardware-description-languages/lessons/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual([lesson["order"] for lesson in response.json()], list(range(1, 21)))
        self.assertEqual(len(lesson_ids), len(HDL_LESSONS))
        for index, lesson_id in enumerate(lesson_ids):
            data = self.client.get(f"/api/lessons/{lesson_id}/").json()
            self.assertEqual(data["prev_lesson_id"], lesson_ids[index - 1] if index else None)
            self.assertEqual(data["next_lesson_id"], lesson_ids[index + 1] if index + 1 < len(lesson_ids) else None)
            self.assertEqual(data["next_chapter_slug"], "digital-building-blocks")
            self.assert_lesson_content(data["body"], 4)
            self.assertIn("```systemverilog", data["body"])
        self.assertEqual(self.client.get("/api/tags/sequential-logic/").json()["next_slug"], fourth.slug)
        final_lesson = self.client.get(f"/api/lessons/{third.lessons.last().id}/").json()
        self.assertEqual(final_lesson["next_chapter_slug"], fourth.slug)

    def test_fifth_chapter_preserves_existing_lessons_and_links_from_fourth(self):
        call_command("seed_foundations", stdout=StringIO())
        fourth = Tag.objects.get(slug="hardware-description-languages")
        fifth = Tag.objects.get(slug="digital-building-blocks")
        fifth.full_clean()
        self.assertEqual(fifth.prerequisite, fourth)
        self.assertEqual(fifth.order, 5)
        self.assertEqual(fifth.category, "foundations")
        previous = list(Lesson.objects.exclude(chapter=fifth).values_list("id", "chapter_id", "order", "body"))
        ids = list(fifth.lessons.values_list("id", flat=True))
        call_command("seed_foundations", stdout=StringIO())
        self.assertEqual(list(fifth.lessons.values_list("id", flat=True)), ids)
        self.assertEqual(list(Lesson.objects.exclude(chapter=fifth).values_list("id", "chapter_id", "order", "body")), previous)
        response = self.client.get("/api/tags/digital-building-blocks/lessons/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual([lesson["order"] for lesson in response.json()], list(range(1, len(BUILDING_BLOCK_LESSONS)+1)))
        self.assertEqual(len(ids), len(BUILDING_BLOCK_LESSONS))
        for index, lesson_id in enumerate(ids):
            response = self.client.get(f"/api/lessons/{lesson_id}/")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["prev_lesson_id"], ids[index-1] if index else None)
            self.assertEqual(data["next_lesson_id"], ids[index+1] if index+1<len(ids) else None)
            self.assertIsNone(data["next_chapter_slug"])
            self.assert_lesson_content(data["body"], 5)
        self.assertEqual(self.client.get("/api/tags/hardware-description-languages/").json()["next_slug"], fifth.slug)
        self.assertEqual(self.client.get("/api/tags/digital-building-blocks/").json()["prerequisite_slug"], fourth.slug)
        data = self.client.get(f"/api/lessons/{fourth.lessons.last().id}/").json()
        self.assertEqual(data["next_chapter_slug"], fifth.slug)

    def test_missing_fifth_chapter_rolls_back_new_chapter_and_previous_updates(self):
        from pathlib import Path

        call_command("seed_foundations", stdout=StringIO())
        Tag.objects.get(slug="digital-building-blocks").delete()
        lesson = Lesson.objects.get(chapter__slug="hardware-description-languages", order=1)
        lesson.body = "보존할 기존 편집"
        lesson.save(update_fields=["body"])
        ids = set(Lesson.objects.values_list("id", flat=True))
        read_text = Path.read_text

        def read_content(path, *args, **kwargs):
            if "chapter05" in path.parts:
                raise FileNotFoundError("5장 본문 누락")
            return read_text(path, *args, **kwargs)

        with patch("digest.management.commands.seed_foundations.Path.read_text", autospec=True, side_effect=read_content):
            with self.assertRaises(FileNotFoundError):
                call_command("seed_foundations", stdout=StringIO())
        lesson.refresh_from_db()
        self.assertEqual(lesson.body, "보존할 기존 편집")
        self.assertEqual(set(Lesson.objects.values_list("id", flat=True)), ids)
        self.assertFalse(Tag.objects.filter(slug="digital-building-blocks").exists())

    def test_failure_in_fourth_chapter_rolls_back_prior_updates(self):
        from pathlib import Path

        call_command("seed_foundations", stdout=StringIO())
        lesson = Lesson.objects.get(chapter__slug="sequential-logic", order=1)
        lesson.body = "보존할 기존 편집"
        lesson.save(update_fields=["body"])
        lesson_ids = set(Lesson.objects.values_list("id", flat=True))
        read_text = Path.read_text

        def read_content(path, *args, **kwargs):
            if "chapter04" in path.parts:
                raise FileNotFoundError("4장 콘텐츠 누락")
            return read_text(path, *args, **kwargs)

        with patch("digest.management.commands.seed_foundations.Path.read_text", autospec=True, side_effect=read_content):
            with self.assertRaises(FileNotFoundError):
                call_command("seed_foundations", stdout=StringIO())
        lesson.refresh_from_db()
        self.assertEqual(lesson.body, "보존할 기존 편집")
        self.assertEqual(set(Lesson.objects.values_list("id", flat=True)), lesson_ids)

    def test_failure_in_third_chapter_rolls_back_existing_content(self):
        from pathlib import Path

        call_command("seed_foundations", stdout=StringIO())
        lesson = Lesson.objects.get(chapter__slug="combinational-logic", order=1)
        lesson.body = "보존할 기존 편집"
        lesson.save(update_fields=["body"])
        lesson_ids = set(Lesson.objects.values_list("id", flat=True))
        read_text = Path.read_text

        def read_content(path, *args, **kwargs):
            if "chapter03" in path.parts:
                raise FileNotFoundError("3장 콘텐츠 누락")
            return read_text(path, *args, **kwargs)

        with patch("digest.management.commands.seed_foundations.Path.read_text", autospec=True, side_effect=read_content):
            with self.assertRaises(FileNotFoundError):
                call_command("seed_foundations", stdout=StringIO())
        lesson.refresh_from_db()
        self.assertEqual(lesson.body, "보존할 기존 편집")
        self.assertEqual(set(Lesson.objects.values_list("id", flat=True)), lesson_ids)

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
