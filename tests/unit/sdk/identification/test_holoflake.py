import unittest
from datetime import datetime, timezone

from holobot.sdk.identification import Holoflake

class TestHoloflake(unittest.TestCase):
    def test_construction_from_segments(self):
        test_cases = (
            (datetime(2024, 11, 15, 0, 0, 0, 0, timezone.utc), 0, 0, 0),
            (datetime(2024, 11, 15, 0, 0, 0, 1_000, timezone.utc), 0, 0, 4_194_304),
            (datetime(2024, 11, 15, 0, 0, 0, 0, timezone.utc), 0, 1, 1),
            (datetime(2024, 11, 15, 0, 0, 0, 0, timezone.utc), 1, 0, 4_096),
            (datetime(2024, 11, 16, 22, 32, 17, 3_000, timezone.utc), 10, 5, 702_701_121_871_877),
            (datetime(2032, 12, 31, 23, 59, 59, 999_000, timezone.utc), 1023, 4095, 1_075_929_572_966_399_999),
        )

        for timestamp, worker_id, sequence_id, expected_value in test_cases:
            with self.subTest(
                timestamp=timestamp,
                worker_id=worker_id,
                sequence_id=sequence_id,
                expected_value=expected_value
            ):
                holoflake = Holoflake.from_segments(timestamp, worker_id, sequence_id)
                self.assertEqual(holoflake.created_at, timestamp)
                self.assertEqual(holoflake.worker_id, worker_id)
                self.assertEqual(holoflake.sequence_id, sequence_id)
                self.assertEqual(holoflake, expected_value)

    def test_min(self):
        holoflake = Holoflake.min()
        self.assertEqual(holoflake, 0)

    def test_max(self):
        holoflake = Holoflake.max()
        self.assertEqual(holoflake, 9_223_372_036_854_775_807)
