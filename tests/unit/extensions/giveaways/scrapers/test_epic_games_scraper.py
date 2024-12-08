import unittest
from datetime import datetime, timezone

from holobot.extensions.giveaways.models import EpicScraperOptions
from holobot.extensions.giveaways.scrapers import EpicGamesScraper
from tests.machinery.fakes import (
    FakeClock, FakeHttpClientPool, FakeLoggerFactory, FakeOptionsProvider
)

class TestEpicGamesScraper(unittest.TestCase):
    def setUp(self) -> None:
        self.clock = FakeClock()
        self.http_client_pool = FakeHttpClientPool()
        self.subject = EpicGamesScraper(
            clock=self.clock,
            http_client_pool=self.http_client_pool,
            logger_factory=FakeLoggerFactory(),
            options=FakeOptionsProvider(
                EpicScraperOptions()
            )
        )

    async def asyncTearDown(self) -> None:
        await self.http_client_pool.close()

    def test_get_next_scraper_time(self):
        test_cases = (
            # Just released, last scraped after the previous release -> should scrape in 5 mins.
            (
                datetime(2023, 1, 12, 16, 0, tzinfo=timezone.utc),
                datetime(2023, 1, 5, 16, 5, tzinfo=timezone.utc),
                datetime(2023, 1, 12, 16, 5, tzinfo=timezone.utc)
            ),
            # Just released, last scraped before the previous release -> should scrape in 5 mins (on the same day we wait for the new release).
            (
                datetime(2023, 1, 12, 16, 0, tzinfo=timezone.utc),
                datetime(2022, 12, 29, 16, 5, tzinfo=timezone.utc),
                datetime(2023, 1, 12, 16, 5, tzinfo=timezone.utc)
            ),
            # Releases in 5 mins, last scraped after the previous release -> should scrape in 10 mins.
            (
                datetime(2023, 1, 12, 15, 55, tzinfo=timezone.utc),
                datetime(2023, 1, 5, 16, 5, tzinfo=timezone.utc),
                datetime(2023, 1, 12, 16, 5, tzinfo=timezone.utc)
            ),
            # Releases in 5 mins, last scraped before the previous release -> should scrape in 10 mins (on the same day we wait for the new release).
            (
                datetime(2023, 1, 12, 15, 55, tzinfo=timezone.utc),
                datetime(2022, 12, 29, 16, 5, tzinfo=timezone.utc),
                datetime(2023, 1, 12, 16, 5, tzinfo=timezone.utc)
            ),
            # Releases tomorrow, last scraped after the previous release -> should scrape tomorrow at 10 AM (US/Central).
            (
                datetime(2023, 1, 11, 18, 0, tzinfo=timezone.utc),
                datetime(2023, 1, 11, 16, 5, tzinfo=timezone.utc),
                datetime(2023, 1, 12, 16, 5, tzinfo=timezone.utc)
            ),
            # Released 4 hours ago, last scraped before the previous release -> should scrape 1 min ago.
            (
                datetime(2023, 1, 11, 20, 0, tzinfo=timezone.utc),
                datetime(2022, 12, 29, 16, 5, tzinfo=timezone.utc),
                datetime(2023, 1, 11, 19, 59, tzinfo=timezone.utc)
            )
        )

        for ct, lt, et in test_cases:
            with self.subTest(current_time=ct, last_time=lt, expected_time=et):
                self.clock.set_now(ct)
                result = self.subject.get_next_scrape_time(lt)
                self.assertEqual(result, et)
