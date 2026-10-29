from io import StringIO
from pathlib import Path
from unittest.mock import patch
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET

from django.core.management import call_command
from django.test import SimpleTestCase, TestCase, override_settings

from digest.models import Lesson, Tag


class FirmwareCodeTests(SimpleTestCase):
    def test_c_examples_compile_and_assert_expected_values(self):
        compiler = shutil.which("gcc")
        if compiler is None:
            self.skipTest("C 예제 검증에 필요한 gcc가 없습니다.")
        folder = Path(__file__).resolve().parent / "content" / "firmware" / "chapter01"
        with tempfile.TemporaryDirectory(dir=folder.parents[3]) as directory:
            for lesson in sorted(folder.glob("*.md")):
                for index, code in enumerate(re.findall(r"```c\n(.*?)```", lesson.read_text(encoding="utf-8"), re.S)):
                    with self.subTest(lesson=lesson.name, example=index):
                        source = Path(directory) / f"{lesson.stem}.c"
                        executable = Path(directory) / f"{lesson.stem}.exe"
                        source.write_text(code, encoding="utf-8")
                        subprocess.run([compiler, "-std=c11", "-Wall", "-Wextra", "-Werror", "-O2",
                                        str(source), "-o", str(executable)], check=True, capture_output=True, timeout=30)
                        try:
                            subprocess.run([str(executable)], check=True, capture_output=True, timeout=10)
                        except PermissionError:
                            self.skipTest("컴파일 성공, 생성된 C 실행 파일에 대한 접근이 거부되었습니다.")

    def test_explained_bit_and_register_traces(self):
        config = 0xA5
        self.assertEqual(config & ~(3 << 4), 0x85)
        self.assertEqual((config & ~(3 << 4)) | (1 << 4), 0x95)
        self.assertEqual(config | (1 << 4), 0xB5)
        config = (config & ~(3 << 4)) | (2 << 4)
        self.assertEqual(config, 0xA5)
        config |= 1 << 3
        self.assertEqual(config, 0xAD)
        config &= ~(1 << 0)
        self.assertEqual(config, 0xAC)
        self.assertEqual((config >> 4) & 3, 2)
        self.assertEqual(0x03 & ~0x03, 0x00)
        self.assertEqual(0x03 & ~0x01, 0x02)
        self.assertEqual(0x0B & ~0x02, 0x09)


@override_settings(CACHES={"default": {
    "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    "LOCATION": "firmware-tests",
}})
class FirmwareTests(TestCase):
    def test_seed_preserves_ids_other_tracks_and_api_navigation(self):
        existing = Tag.objects.create(slug="existing-ssd", name="기존", category="ssd", order=1)
        old_lesson = Lesson.objects.create(chapter=existing, order=1, title="유지", body="기존 본문")
        call_command("seed_firmware", stdout=StringIO())
        chapter = Tag.objects.get(slug="firmware-memory-registers")
        chapter.full_clean()
        ids = list(chapter.lessons.values_list("id", flat=True))
        self.assertEqual(len(ids), 3)
        call_command("seed_firmware", stdout=StringIO())
        self.assertEqual(list(chapter.lessons.values_list("id", flat=True)), ids)
        old_lesson.refresh_from_db()
        self.assertEqual(old_lesson.body, "기존 본문")
        self.assertEqual(Tag.objects.count(), 2)
        tags = self.client.get("/api/tags/").json()
        self.assertIn("firmware", [tag["category"] for tag in tags])
        lessons = self.client.get(f"/api/tags/{chapter.slug}/lessons/")
        self.assertEqual(lessons.status_code, 200)
        self.assertEqual([item["order"] for item in lessons.json()], [1, 2, 3])
        for index, lesson_id in enumerate(ids):
            response = self.client.get(f"/api/lessons/{lesson_id}/")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["prev_lesson_id"], ids[index - 1] if index else None)
            self.assertEqual(data["next_lesson_id"], ids[index + 1] if index < 2 else None)
            self.assertIsNone(data["next_chapter_slug"])

    def test_missing_content_rolls_back_partial_updates(self):
        call_command("seed_firmware", stdout=StringIO())
        Lesson.objects.filter(chapter__category="firmware", order=1).update(body="수정 전")
        original = Path.read_text

        def read(path, *args, **kwargs):
            if path.name == "02-bits.md":
                raise FileNotFoundError(path)
            return original(path, *args, **kwargs)

        with patch.object(Path, "read_text", read):
            with self.assertRaises(FileNotFoundError):
                call_command("seed_firmware", stdout=StringIO())
        self.assertEqual(Lesson.objects.get(chapter__category="firmware", order=1).body, "수정 전")

    def test_lesson_structure_and_diagram_labels(self):
        call_command("seed_firmware", stdout=StringIO())
        for lesson in Lesson.objects.filter(chapter__category="firmware"):
            headings = ["이번 레슨의 목표", "앞에서 배운 내용", "개념과 동작", "코드 읽기",
                        "따라 풀기", "헷갈리기 쉬운 점", "직접 확인하기", "다음으로 이어가기", "참고 범위"]
            positions = [lesson.body.index(f"## {heading}") for heading in headings]
            self.assertEqual(positions, sorted(positions))
            self.assertIn("```c", lesson.body)
            self.assertIn("<details>", lesson.body)
            for source in re.findall(r"<svg\b.*?</svg>", lesson.body, re.S):
                svg = ET.fromstring(source)
                self.assertEqual(svg.attrib["role"], "img")
                ids = {node.attrib.get("id") for node in svg.iter()}
                self.assertTrue(set(svg.attrib["aria-labelledby"].split()).issubset(ids))
