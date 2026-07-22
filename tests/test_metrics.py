from datetime import datetime
import unittest

from osna_pipeline.metrics import minutes_between


class MinutesBetweenTests(unittest.TestCase):
    def test_calculates_minutes(self):
        start = datetime.fromisoformat("2026-07-20T09:12:00+01:00")
        end = datetime.fromisoformat("2026-07-20T09:21:00+01:00")
        self.assertEqual(minutes_between(start, end), "9.0")

    def test_returns_blank_for_negative_duration(self):
        start = datetime.fromisoformat("2026-07-20T09:21:00+01:00")
        end = datetime.fromisoformat("2026-07-20T09:12:00+01:00")
        self.assertEqual(minutes_between(start, end), "")

    def test_returns_blank_for_missing_timestamp(self):
        end = datetime.fromisoformat("2026-07-20T09:12:00+01:00")
        self.assertEqual(minutes_between(None, end), "")


if __name__ == "__main__":
    unittest.main()
