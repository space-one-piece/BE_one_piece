from django.test import TestCase

from apps.chatbot.services.context_service import (
    can_recommend,
    context_score,
    init_context,
    merge_context,
    rule_based_extract,
)


class ContextServiceTest(TestCase):
    def test_init_context(self) -> None:
        ctx = init_context()
        self.assertIsNone(ctx["space"])
        self.assertIsNone(ctx["mood"])
        self.assertIsNone(ctx["intensity"])
        self.assertIsNone(ctx["time"])

    def test_rule_based_extract_space(self) -> None:
        ctx = rule_based_extract("침실에서 쓸 향수 추천해줘")
        self.assertEqual(ctx["space"], "bedroom")

    def test_rule_based_extract_mood(self) -> None:
        ctx = rule_based_extract("편안한 향수 찾아요")
        self.assertEqual(ctx["mood"], "calm")

    def test_rule_based_extract_intensity(self) -> None:
        ctx = rule_based_extract("은은한 향수 원해요")
        self.assertEqual(ctx["intensity"], "light")

    def test_rule_based_extract_time(self) -> None:
        ctx = rule_based_extract("자기 전에 쓸 향수")
        self.assertEqual(ctx["time"], "night")

    def test_rule_based_extract_none(self) -> None:
        ctx = rule_based_extract("향수 추천해줘")
        self.assertIsNone(ctx["space"])
        self.assertIsNone(ctx["mood"])

    def test_merge_context_keep_existing(self) -> None:
        existing = {"space": "bedroom", "mood": None, "intensity": None, "time": None}
        new = {"space": None, "mood": "calm", "intensity": None, "time": None}
        merged = merge_context(existing, new)
        self.assertEqual(merged["space"], "bedroom")
        self.assertEqual(merged["mood"], "calm")

    def test_merge_context_overwrite(self) -> None:
        existing = {"space": "bedroom", "mood": "calm", "intensity": None, "time": None}
        new = {"space": "livingroom", "mood": None, "intensity": None, "time": None}
        merged = merge_context(existing, new)
        self.assertEqual(merged["space"], "livingroom")
        self.assertEqual(merged["mood"], "calm")

    def test_context_score_full(self) -> None:
        ctx: dict[str, str | None] = {"space": "bedroom", "mood": "calm", "intensity": "light", "time": "night"}
        self.assertEqual(context_score(ctx), 6)

    def test_context_score_partial(self) -> None:
        ctx = {"space": "bedroom", "mood": None, "intensity": None, "time": None}
        self.assertEqual(context_score(ctx), 2)

    def test_can_recommend_true(self) -> None:
        ctx = {"space": "bedroom", "mood": "calm", "intensity": "light", "time": None}
        self.assertTrue(can_recommend(ctx))

    def test_can_recommend_no_space(self) -> None:
        ctx = {"space": None, "mood": "calm", "intensity": "light", "time": "night"}
        self.assertFalse(can_recommend(ctx))

    def test_can_recommend_no_mood(self) -> None:
        ctx = {"space": "bedroom", "mood": None, "intensity": "light", "time": "night"}
        self.assertFalse(can_recommend(ctx))

    def test_can_recommend_no_intensity_or_time(self) -> None:
        ctx = {"space": "bedroom", "mood": "calm", "intensity": None, "time": None}
        self.assertFalse(can_recommend(ctx))
