import base64

from django.http import Http404
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from playwright.sync_api import sync_playwright

from apps.analysis.models import ImageAnalysis
from apps.chatbot.models import ChatbotRecommendation
from apps.core.utils.cloud_front import image_url_cloud
from apps.core.utils.s3_handler import image_url_edit
from apps.question.google_ai_studio import Gemini
from apps.question.models import QuestionsResults
from apps.question.service.service import QuestServices
from apps.users.models.models import User


class ImageUserService(QuestServices, Gemini):
    @classmethod
    def image_new(cls, user_id: int) -> str | None:
        quest_data = QuestionsResults.objects.filter(user_id=user_id).order_by("created_at").first()
        image_data = ImageAnalysis.objects.filter(user_id=user_id).order_by("created_at").first()
        chat_data = ChatbotRecommendation.objects.filter(user_id=user_id).order_by("created_at").first()

        result = [obj for obj in [quest_data, image_data, chat_data] if obj is not None]

        if not result:
            raise Http404

        last_data = max(result, key=lambda x: x.created_at)

        category_data = {
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

        if isinstance(last_data, ImageAnalysis):
            last_sent_data = last_data.recommended_scent.eng_name if last_data.recommended_scent else ""
            color_palette = category_data[last_data.recommended_scent.categories] if last_data.recommended_scent else ""
        else:
            last_sent_data = last_data.scent.eng_name if last_data.scent else ""
            color_palette = category_data[last_data.scent.categories] if last_data.scent else ""

        prompt = color_palette.replace("( )", last_sent_data)
        generated_image_url: str | None = cls.image_gemini(prompt)
        return generated_image_url

    @classmethod
    def user_profile_save(cls, user_id: int, image_url: str) -> None:
        if image_url is None:
            raise Http404

        user_data = get_object_or_404(User, pk=user_id)
        user_data.profile_image_url = image_url_edit(image_url)
        user_data.save()

    @classmethod
    def web_share(cls, user_id: int, result_id: int, division: str) -> dict[str, str]:
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
            "scent_image_url": image_url_cloud(scent.thumbnail_url),
            "description": scent.description,
            "ai_comment": ai_comment,  # 수정된 부분
            "profiles": profile_list,
            "notes_list": notes_list,
        }

        html_string = render_to_string("share_template.html", context)

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.set_content(html_string)
            page.wait_for_load_state("networkidle")
            image_bytes = page.screenshot(full_page=True, type="png")
            browser.close()

        data = {"image_data": base64.b64encode(image_bytes).decode("utf-8")}

        return data
