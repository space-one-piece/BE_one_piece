from django.test import TestCase

from apps.chatbot.services.context_service import init_context
from apps.chatbot.services.scent_filter_service import (
    count_meaningful_turns,
    filter_scents,
    get_fallback_scents,
)


class ScentFilterServiceTest(TestCase):
    def test_get_fallback_scents(self) -> None:
        result = get_fallback_scents()
        self.assertTrue(len(result) > 0)
        for scent in result:
            self.assertTrue(scent["isBestseller"])

    def test_get_fallback_scents_excluded(self) -> None:
        result = get_fallback_scents(excluded_ids=[1, 4])
        ids = [s["id"] for s in result]
        self.assertNotIn(1, ids)
        self.assertNotIn(4, ids)

    def test_filter_scents_by_space(self) -> None:
        ctx = init_context()
        ctx["space"] = "bedroom"
        result = filter_scents(ctx)
        self.assertTrue(len(result) > 0)
        for scent in result:
            self.assertTrue(any("Bedroom" in p for p in scent["recommendedPlaces"]))

    def test_filter_scents_by_mood(self) -> None:
        ctx = init_context()
        ctx["mood"] = "fresh"
        result = filter_scents(ctx)
        self.assertTrue(len(result) > 0)

    def test_filter_scents_empty_fallback(self) -> None:
        non_bestseller_ids = [2, 3, 5, 6, 9, 11, 12, 14, 15, 16, 18, 19, 21, 23, 24, 26, 27, 28, 29]
        ctx = init_context()
        ctx["space"] = "study"
        ctx["mood"] = "romantic"
        ctx["intensity"] = "light"
        ctx["time"] = "morning"
        result = filter_scents(ctx, excluded_ids=non_bestseller_ids)
        self.assertTrue(len(result) > 0)
        for scent in result:
            self.assertTrue(scent["isBestseller"])

    def test_count_meaningful_turns(self) -> None:
        messages = [
            {"role": "user", "content": "침실에서 쓸 향수 추천해줘"},
            {"role": "assistant", "content": "어떤 분위기를 원하세요?"},
            {"role": "user", "content": "ㅇㅇ"},
            {"role": "user", "content": "편안한 향 좋아요"},
        ]
        self.assertEqual(count_meaningful_turns(messages), 2)
