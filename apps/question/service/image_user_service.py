from django.http import Http404
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from playwright.sync_api import sync_playwright

from apps.analysis.models import ImageAnalysis
from apps.chatbot.models import ChatbotRecommendation
from apps.core.utils.cloud_front import image_url_cloud
from apps.core.utils.s3_handler import S3Handler, image_url_edit
from apps.question.google_ai_studio import Gemini
from apps.question.models import QuestionsResults
from apps.question.service.service import QuestServices
from apps.users.models.models import User

SCENT_COLOR_MAP = {
    "amber": "radial-gradient(circle, #E6BE8A 0%, #D4A373 50%, rgba(255,255,255,0) 100%)",
    "aquatic": "radial-gradient(circle, #A3C9D9 0%, #D1E5ED 50%, rgba(255,255,255,0) 100%)",
    "citrus": "radial-gradient(circle, #EAB638 0%, #A2C579 50%, rgba(255,255,255,0) 100%)",
    "floral": "radial-gradient(circle, #FFB6C1 0%, #FFD1DC 50%, rgba(255,255,255,0) 100%)",
    "fruity": "radial-gradient(circle, #FF7E5F 0%, #FEB47B 50%, rgba(255,255,255,0) 100%)",
    "green": "radial-gradient(circle, #92B4A7 0%, #B5C9C3 50%, rgba(255,255,255,0) 100%)",
    "musk": "radial-gradient(circle, #E3D9D1 0%, #F5F5F5 50%, rgba(255,255,255,0) 100%)",
    "powdery": "radial-gradient(circle, #D1D1E9 0%, #E2E2F3 50%, rgba(255,255,255,0) 100%)",
    "spicy": "radial-gradient(circle, #D98880 0%, #F2D7D5 50%, rgba(255,255,255,0) 100%)",
    "woody": "radial-gradient(circle, #A28D76 0%, #D4C3B1 50%, rgba(255,255,255,0) 100%)",
}


class ImageUserService(QuestServices, Gemini):
    CATEGORY_PROMPTS: dict[str, str] = {
        "floral": """A elegant crystal perfume bottle labeled "( )" placed on white marble slab,
                surrounded by blooming roses, jasmine flowers, peony petals scattered around,
                soft pink and ivory bokeh background, romantic and feminine atmosphere,
                delicate floral mist drifting around the bottle,
                golden hour diffused lighting, macro product photography, ultra realistic, 8k""",
        "fruity": """A vibrant glass perfume bottle labeled "( )" on a rustic wooden surface,
                surrounded by fresh peach slices, ripe berries, fig halves, and passion fruit,
                warm coral and golden yellow bokeh background, playful and juicy atmosphere,
                fine fruit mist sparkling around the bottle,
                bright natural sunlight, macro product photography, ultra realistic, 8k""",
        "woody": """A dark matte perfume bottle labeled "( )" resting on aged oak wood slab,
                surrounded by cedarwood chips, sandalwood shavings, dry bark and forest moss,
                deep brown and forest green bokeh background, warm and grounded atmosphere,
                smoky woody mist curling around the bottle,
                warm amber side lighting, macro product photography, ultra realistic, 8k""",
        "citrus": """A sleek transparent perfume bottle labeled "( )" on wet white stone,
                surrounded by sliced lemon, bergamot, grapefruit halves and fresh orange peel,
                bright yellow and crisp white bokeh background, fresh and energetic atmosphere,
                sparkling citrus droplets bursting around the bottle,
                sharp natural daylight, macro product photography, ultra realistic, 8k""",
        "musk": """A minimalist frosted perfume bottle labeled "( )" on soft white linen fabric,
                surrounded by white cotton flowers, soft feathers and sheer silk cloth,
                clean white and pale grey bokeh background, soft and skin-like atmosphere,
                barely visible warm mist hovering around the bottle,
                soft diffused studio lighting, macro product photography, ultra realistic, 8k""",
        "green": """A fresh matte green perfume bottle labeled "( )" on damp dark soil,
                surrounded by cut grass, fern leaves, eucalyptus branches and morning dew drops,
                deep emerald and cool green bokeh background, natural and earthy atmosphere,
                light green herbal mist rising around the bottle,
                cool morning light with soft shadows, macro product photography, ultra realistic, 8k""",
        "spicy": """A bold dark red perfume bottle labeled "( )" on black volcanic stone,
                surrounded by cinnamon sticks, black pepper, cloves, dried chili and cardamom pods,
                deep crimson and burnt orange bokeh background, intense and fiery atmosphere,
                spiced dark smoke swirling dramatically around the bottle,
                strong dramatic side lighting, macro product photography, ultra realistic, 8k""",
        "powdery": """A soft pastel perfume bottle labeled "( )" on a vintage vanity tray,
                surrounded by loose powder, dried iris petals, soft cotton and white talc dust,
                blush pink and lavender bokeh background, nostalgic and delicate atmosphere,
                fine powder particles floating gently around the bottle,
                warm soft candlelight, macro product photography, ultra realistic, 8k""",
        "aquatic": """A translucent blue perfume bottle labeled "( )" on smooth ocean pebbles,
                surrounded by sea salt crystals, coral fragments, driftwood and ocean foam,
                deep ocean blue and seafoam teal bokeh background, cool and breezy atmosphere,
                fine ocean mist and water droplets suspended around the bottle,
                soft coastal morning light, macro product photography, ultra realistic, 8k""",
        "amber": """A luxurious gold-tinted perfume bottle labeled "( )" on dark resin surface,
                surrounded by amber resin chunks, dried vanilla pods, benzoin and labdanum pieces,
                rich golden and deep copper bokeh background, warm and opulent atmosphere,
                golden resinous haze glowing around the bottle,
                warm dramatic candlelight, macro product photography, ultra realistic, 8k""",
    }

    @classmethod
    def _get_latest(cls, user_id: int) -> QuestionsResults | ImageAnalysis | ChatbotRecommendation:
        records = [
            QuestionsResults.objects.filter(user_id=user_id).order_by("-created_at").first(),
            ImageAnalysis.objects.filter(user_id=user_id).order_by("-created_at").first(),
            ChatbotRecommendation.objects.filter(user_id=user_id).order_by("-created_at").first(),
        ]

        valid_records = [r for r in records if r is not None]

        if not valid_records:
            raise Http404

        return max(valid_records, key=lambda x: x.created_at)

    @classmethod
    def _extract_scent_info(cls, record: QuestionsResults | ImageAnalysis | ChatbotRecommendation) -> tuple[str, str]:
        scent = record.recommended_scent if isinstance(record, ImageAnalysis) else record.scent

        if not scent:
            return "", ""

        return scent.eng_name, scent.categories

    @classmethod
    def image_new(cls, user_id: int) -> str | None:
        last_record = cls._get_latest(user_id)
        scent_eng_name, category = cls._extract_scent_info(last_record)

        if not category or category not in cls.CATEGORY_PROMPTS:
            return None

        prompt = cls.CATEGORY_PROMPTS[category].replace("( )", scent_eng_name)
        return cls.image_gemini(prompt)

    @classmethod
    def user_profile_save(cls, user_id: int, image_url: str) -> None:
        if image_url is None:
            raise Http404

        user_data = get_object_or_404(User, pk=user_id)
        user_data.profile_image_url = image_url_edit(image_url)
        user_data.save()

    @classmethod
    def web_share(cls, result_id: int, division: str) -> str:
        if result_id is None:
            raise Http404

        result_obj = cls.result_division(result_id, division)

        ai_comment = ""
        if division == "chatbot":
            if hasattr(result_obj, "reply"):
                ai_comment = result_obj.reply if result_obj.reply else ""
        else:
            if hasattr(result_obj, "answer_ai"):
                ai_comment = getattr(result_obj, "answer_ai", "")

        scent = getattr(result_obj, "scent", None)
        if not scent:
            raise Http404

        scent_color = SCENT_COLOR_MAP.get(scent.categories, SCENT_COLOR_MAP["citrus"])

        s3_handler = S3Handler()
        s3_key = S3Handler.build_share_image_key(scent.name, result_id, division)

        if s3_handler.check_share_image_exists(s3_key):
            image_url_data = image_url_cloud(s3_handler.get_img_url(s3_key))
            return image_url_data if image_url_data else ""

        raw_profile = scent.profile
        profile_list = []
        if isinstance(raw_profile, dict):
            for name, value in raw_profile.items():
                profile_list.append({"name": name, "value": value})
        else:
            profile_list = raw_profile

        raw_notes = scent.scent_notes
        notes_list = []
        if isinstance(raw_notes, dict):
            for key in ["top", "middle", "base"]:
                note_item = raw_notes.get(key)
                if note_item:
                    notes_list.append(note_item)

        context = {
            "scent_name": scent.name,
            "eng_name": scent.eng_name,
            "scent_color": scent_color,
            "tags": scent.tags if isinstance(scent.tags, list) else scent.tags.split(",") if scent.tags else [],
            "ai_comment": ai_comment,
        }

        html_string = render_to_string("share_template.html", context)

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.set_content(html_string)
            page.wait_for_load_state("networkidle")
            image_bytes = page.screenshot(full_page=True, type="png")
            browser.close()

        image_url = s3_handler.get_or_create_share_image(
            image_bytes=image_bytes,
            scent_name=scent.name,
            result_id=result_id,
            division=division,
        )
        image_data = image_url_cloud(image_url)
        if image_data:
            return image_data

        return ""
