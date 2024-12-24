import threading
import time
import unittest
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone

from holobot.framework.identification import HoloflakeProvider
from holobot.sdk.identification import Holoflake
from holobot.sdk.threading import CancellationTokenSource
from tests.machinery.fakes import FakeClock, FakeEnvironment

@dataclass
class _Context:
    holoflake: Holoflake | None = None

def signal_and_get_next_id(
    provider: HoloflakeProvider,
    signal: Callable[[], None],
    context: _Context
) -> None:
    print("Signaling for 'get_next_id()'...")
    signal()
    context.holoflake = provider.get_next_id()
    print("Next Holoflake has been created")

class TestHoloflakeProvider(unittest.TestCase):
    def setUp(self) -> None:
        self.clock = FakeClock()
        self.subject = HoloflakeProvider(
            self.clock,
            FakeEnvironment()
        )

    def test_holoflake_generation_when_time_progresses(self):
        self.clock.set_now(datetime(2024, 11, 16, 0, 0, 0, 0, timezone.utc))
        id1 = self.subject.get_next_id()
        self.assertEqual(id1, 362_387_865_640_960)
        id2 = self.subject.get_next_id()
        self.assertEqual(id2, 362_387_865_640_961)
        id3 = self.subject.get_next_id()
        self.assertEqual(id3, 362_387_865_640_962)

        self.clock.set_now(datetime(2024, 11, 16, 0, 0, 0, 1000, timezone.utc))
        id4 = self.subject.get_next_id()
        self.assertEqual(id4, 362_387_869_835_264)
        id5 = self.subject.get_next_id()
        self.assertEqual(id5, 362_387_869_835_265)

        self.clock.set_now(datetime(2024, 11, 16, 0, 0, 0, 2000, timezone.utc))
        id6 = self.subject.get_next_id()
        self.assertEqual(id6, 362_387_874_029_568)

    def test_holoflake_generation_when_sequence_ids_are_exhausted(self):
        self.clock.set_now(datetime(2024, 11, 16, 0, 0, 0, 1000, timezone.utc))
        for sequence_id in range(1 << 12):
            holoflake = self.subject.get_next_id()
            self.assertEqual(holoflake, 362_387_869_835_264 + sequence_id)

        signal_token_source = CancellationTokenSource()
        signal_token = signal_token_source.token
        signal = lambda: signal_token_source.cancel()
        context = _Context()
        get_next_id_thread = threading.Thread(
            target=signal_and_get_next_id,
            args=(self.subject, signal, context,)
        )

        print("Starting 'get_next_id_thread'...")
        get_next_id_thread.start()

        print("Waiting for 'get_next_id_thread' signal...")
        while not signal_token.is_cancellation_requested:
            time.sleep(0.0001)

        # Wait an extra bit just to make sure the waiting loop in the provider is triggered.
        time.sleep(0.5)

        print("Signal received, changing clock...")
        self.clock.set_now(datetime(2024, 11, 16, 0, 0, 0, 2000, timezone.utc))

        get_next_id_thread.join()
        print("Finished 'get_next_id_thread'")

        self.assertIsNotNone(context.holoflake)
        self.assertEqual(context.holoflake, 362_387_874_029_568)
