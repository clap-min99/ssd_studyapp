from datetime import date
from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase

from fetcher.gmail_client import fetch_latest_digest


class DateSelectionTests(SimpleTestCase):
    @patch("fetcher.gmail_client.get_gmail_service")
    def test_exact_subject_date_across_pages(self, service):
        messages = service.return_value.users.return_value.messages.return_value
        messages.list.return_value.execute.side_effect = [
            {"messages": [{"id": "new"}], "nextPageToken": "page2"},
            {"messages": [{"id": "old"}]},
        ]
        messages.get.return_value.execute.side_effect = [
            {"payload": {"headers": [{"name": "Subject", "value": "[2026-10-14] SSD"}]}},
            {"payload": {"headers": [{"name": "Subject", "value": "[2026-10-13] SSD"}]}},
        ]
        result = fetch_latest_digest(target_date=date(2026, 10, 13))
        self.assertEqual(result["date"], "2026-10-13")
        query = messages.list.call_args.kwargs["q"]
        self.assertIn('subject:"2026-10-13"', query)
        self.assertNotIn("after:", query)
        self.assertEqual(messages.list.call_args.kwargs["pageToken"], "page2")

    @patch("fetcher.gmail_client.get_gmail_service")
    def test_default_search_keeps_recent_window(self, service):
        messages = service.return_value.users.return_value.messages.return_value
        messages.list.return_value.execute.return_value = {}
        self.assertIsNone(fetch_latest_digest())
        self.assertIn("after:", messages.list.call_args.kwargs["q"])

    @patch("digest.management.commands.fetch_digest.fetch_latest_digest")
    def test_invalid_date_fails_before_gmail(self, fetch):
        for value in ("2026-02-30", "20261013", "13/10/2026"):
            with self.subTest(value=value), self.assertRaises(CommandError):
                call_command("fetch_digest", "--date", value, stdout=StringIO())
        fetch.assert_not_called()

    @patch("digest.management.commands.fetch_digest.fetch_latest_digest", return_value=None)
    def test_missing_target_reports_requested_date(self, fetch):
        with self.assertRaisesMessage(CommandError, "2026-10-13"):
            call_command("fetch_digest", "--date", "2026-10-13", stdout=StringIO())
        fetch.assert_called_once_with(days_back=2, target_date=date(2026, 10, 13))
